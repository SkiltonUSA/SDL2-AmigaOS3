#!/usr/bin/env python3
"""Build and package the pinned 68k SDL2 SDK. zlib licence; see LICENSE."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "docker.io/amigadev/crosstools@sha256:93ca1a47903b61873f6638881b44f9f2d6086a39f1b9b916a26faff3a8ea4d3d"
UPSTREAM = "1eefa8f35c5ad4b63fa835e251e801a9315dff5c"
FLAGS = "-std=gnu99 -O0 -m68030 -noixemul -Wall -Wextra -Wno-unused-parameter -Wno-sign-compare -I./include -I./src -D__AMIGAOS3__"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode().strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--container-command", default='["docker"]',
                        help="JSON array of container command and global arguments")
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()
    engine = json.loads(args.container_command)
    if not isinstance(engine, list) or not engine or not all(isinstance(s, str) and s for s in engine):
        parser.error("--container-command must be a nonempty JSON array of strings")
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    if git("status", "--porcelain", "--untracked-files=no"):
        parser.error("Commit tracked source/documentation changes before building a release")
    version = (ROOT / "VERSION").read_text().strip()
    name = "SDL2-AmigaOS3-" + version
    build = ROOT / "build"
    dist = ROOT / "dist"
    build.mkdir(exist_ok=True)
    dist.mkdir(exist_ok=True)
    stage = build / name
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir()
    base = engine + ["run", "--rm", "--platform", "linux/amd64",
                     "-v", str(ROOT) + ":/work", "-w", "/work", IMAGE]
    log_path = build / "build.log"
    with log_path.open("w") as log:
        def run(command, capture=False):
            log.write("ARGV " + json.dumps(command) + "\n")
            log.flush()
            if capture:
                value = subprocess.check_output(base + command, stderr=subprocess.STDOUT).decode()
                log.write(value)
                log.flush()
                return value.strip()
            subprocess.run(base + command, check=True, stdout=log, stderr=subprocess.STDOUT)

        compiler = run(["m68k-amigaos-gcc", "--version"], capture=True)
        # Delete archives as well as objects so stale members cannot survive ar rcs.
        # Makefile clean also references upstream examples, so only remove build products here.
        for path in (ROOT / "src").rglob("*.o"):
            path.unlink()
        for name_lib in ("libSDL2.a", "libSDL2_test.a"):
            (ROOT / name_lib).unlink(missing_ok=True)
        print("Building SDL2; compiler output: " + str(log_path), flush=True)
        run(["make", "-B", "-j" + str(args.jobs), "native-build", "CFLAGS=" + FLAGS])
        shutil.copytree(ROOT / "include", stage / "include" / "SDL2")
        (stage / "lib").mkdir()
        for name_lib in ("libSDL2.a", "libSDL2_test.a"):
            shutil.copy2(ROOT / name_lib, stage / "lib" / name_lib)
        for file_name in ("README.md", "LICENSE", "CHANGELOG.md", "VERSION"):
            shutil.copy2(ROOT / file_name, stage / file_name)
        for dir_name in ("docs", "patches", "examples", "evidence"):
            shutil.copytree(ROOT / dir_name, stage / dir_name)
        sdk = "/work/build/" + name
        print("Linking example using the staged SDK headers and library", flush=True)
        run(["m68k-amigaos-gcc", "-std=c99", "-O2", "-m68030", "-noixemul",
             "-D__AMIGAOS3__", "-I" + sdk + "/include/SDL2", sdk + "/examples/window.c",
             sdk + "/lib/libSDL2.a", "-lm", "-lamiga", "-o", sdk + "/examples/window-demo"])
    (stage / "examples/window-demo").chmod(0o755)
    source_paths = sorted(git("ls-files", "src", "include", "Makefile", "LICENSE").splitlines())
    source_hash = hashlib.sha256()
    for path in source_paths:
        source_hash.update(path.encode() + b"\0" + (ROOT / path).read_bytes() + b"\0")
    metadata = {
        "distribution_version": version,
        "sdl_header_version": "2.33.0",
        "upstream_port_version": "0.7.0",
        "upstream_repository": "https://github.com/bdgscotland/libSDL2-amigaos3",
        "upstream_revision": UPSTREAM,
        "build_revision": git("rev-parse", "HEAD"),
        "library_source_sha256": source_hash.hexdigest(),
        "patch_sha256": sha(ROOT / "patches/window-safety.patch"),
        "public_screen_patch_sha256": sha(ROOT / "patches/public-screen.patch"),
        "compiler_image": IMAGE,
        "compiler_version": compiler,
        "container_platform": "linux/amd64",
        "library_flags": FLAGS,
        "files": {str(p.relative_to(stage)): {"bytes": p.stat().st_size, "sha256": sha(p)}
                  for p in [stage / "lib/libSDL2.a", stage / "lib/libSDL2_test.a", stage / "examples/window-demo"]},
        "example_link_verified": True,
        "example_hardware_execution_verified": False,
        "hardware_evidence": "docs/VALIDATION.md",
        "arm_offloading_in_sdl": False,
    }
    (stage / "build-info.json").write_text(json.dumps(metadata, indent=2) + "\n")
    tested_sha = "bf90c1f12536df97bfc85e838cc2fa0047fc23f37d5128dbb89bb38dddec386e"
    verification = {
        "build_revision": metadata["build_revision"],
        "library_source_sha256": metadata["library_source_sha256"],
        "hardware_tested_library_sha256": tested_sha,
        "rebuilt_library_sha256": metadata["files"]["lib/libSDL2.a"]["sha256"],
        "rebuilt_library_matches_hardware_tested_binary": sha(stage / "lib/libSDL2.a") == tested_sha,
        "sdk_example_link_verified": True,
        "sdk_example_hardware_execution_verified": False,
        "hardware_acceptance_scope": "docs/VALIDATION.md",
    }
    (stage / "evidence/distribution-verification.json").write_text(json.dumps(verification, indent=2) + "\n")
    members = sorted(p for p in stage.rglob("*") if p.is_file())
    (stage / "SHA256SUMS").write_text("".join(sha(p) + "  " + str(p.relative_to(stage)) + "\n" for p in members))
    archive_zip = dist / (name + "-sdk.zip")
    with zipfile.ZipFile(archive_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for p in sorted(stage.rglob("*")):
            if p.is_file():
                archive.write(p, str(p.relative_to(build)))
    archive_tar = dist / (name + "-sdk.tar.gz")
    with tarfile.open(archive_tar, "w:gz") as archive:
        archive.add(stage, arcname=name)
    (dist / "SHA256SUMS").write_text("".join(sha(p) + "  " + p.name + "\n" for p in [archive_zip, archive_tar]))
    print(json.dumps(metadata, indent=2))
    print("SDK archives and checksums: " + str(dist))


if __name__ == "__main__":
    main()
