# Source and build provenance

- Original Amiga port: https://github.com/bdgscotland/libSDL2-amigaos3
- Exact upstream commit: `1eefa8f35c5ad4b63fa835e251e801a9315dff5c`
- Upstream commit subject: `perf(framebuffer): asm bswap32 + LockBitMap fast-path engagement (PDR-015 OpenTTD)`
- SDL header version: 2.33.0; upstream Amiga port VERSION: 0.7.0.
- Imported unchanged in our first commit: `src/`, `include/`, `Makefile`, `LICENSE`.
- Upstream game ports/assets, reference-document mirrors, built examples,
  emulator configuration and ancillary scripts were not imported. All library
  source and original notices under the imported trees are preserved.
- Exact local patch SHA-256: `2da264f70a3bdbf81b4df693d947f3de1de7e9405d9499a27e7dd9f1eb105c91`.
- Hardware-tested `libSDL2.a` SHA-256:
  `59a641479effc2a67853b9c91a01dd015ef2e38b90b9d4cab3cc9b6e3ebe8e96`.
- Clean SDK `libSDL2.a` SHA-256:
  `eb805aac436378a29a20fb50270e7c21cb8dbe61fdf6f317ff62418ba16be000`.
  Duplicate C2P archive members removed; both relinked hardware diagnostics
  remain byte-identical. See [validation](VALIDATION.md).
- Compiler image:
  `docker.io/amigadev/crosstools@sha256:93ca1a47903b61873f6638881b44f9f2d6086a39f1b9b916a26faff3a8ea4d3d`.
- Container platform: `linux/amd64`; compiler: `m68k-amigaos-gcc`.
- Library flags:
  `-std=gnu99 -O0 -m68030 -noixemul -Wall -Wextra -Wno-unused-parameter -Wno-sign-compare -I./include -I./src -D__AMIGAOS3__`.

The SDK's `build-info.json` records the actual compiler version, source commit,
source-tree fingerprint and output hashes. The fingerprint covers tracked
`src/`, `include/`, `Makefile` and `LICENSE`: sorted pathname, a NUL byte, file
contents, a NUL byte, repeated into SHA-256. It excludes generated objects.
Release documentation can be added after the build without altering the
library source fingerprint. Compiler warnings are retained in the build log;
a successful build does not establish API compatibility or hardware execution.

The original diagnostic source and complete ARM launcher remain in
[Amiga-MCP-Debugger at dcad46b](https://github.com/SkiltonUSA/Amiga-MCP-Debugger/tree/dcad46b/amiga/sdl_probe).
This SDK does not incorporate or require that application's ARM components.
