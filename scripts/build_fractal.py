#!/usr/bin/env python3
"""Build the standalone SDL ZZFractal example with its embedded XX19c ARM worker."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
ROOT=Path(__file__).resolve().parents[1]
DEMO=ROOT/'examples/zzfractal'
OUT=ROOT/'build/zzfractal'
IMAGE='docker.io/amigadev/crosstools@sha256:93ca1a47903b61873f6638881b44f9f2d6086a39f1b9b916a26faff3a8ea4d3d'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--container-command',default='["docker"]',help='JSON container command/arguments')
    p.add_argument('--clang',default='clang')
    p.add_argument('--ld',default=shutil.which('ld.lld') or '/opt/homebrew/opt/lld/bin/ld.lld')
    args=p.parse_args();engine=json.loads(args.container_command)
    if not isinstance(engine,list) or not engine or not all(isinstance(x,str) and x for x in engine):p.error('Nonempty JSON array of command strings required')
    cc=shutil.which(args.clang);ld=shutil.which(args.ld)
    if not cc or not ld:p.error('Clang with ARM target and LLVM ld.lld required')
    pin=json.loads((DEMO/'sdl.json').read_text())
    library=ROOT/'libSDL2.a'
    if not library.is_file() or hashlib.sha256(library.read_bytes()).hexdigest()!=pin['library_sha256']:
        p.error('Build the matching SDK with scripts/build_release.py first')
    OUT.mkdir(parents=True,exist_ok=True)
    flags=['--target=arm-none-eabi','-mcpu=cortex-a9','-marm','-mfloat-abi=soft','-ffreestanding',
        '-fno-builtin','-fPIC','-fvisibility=hidden','-fno-stack-protector','-O1','-Wall','-Wextra','-Werror','-DFF_TIMING']
    sources=sorted(f for f in DEMO.iterdir() if f.suffix in ('.c','.h','.S','.ld'))
    source_hash=hashlib.sha256()
    for f in sources:source_hash.update(f.name.encode()+b'\0'+f.read_bytes()+b'\0')
    source_hash.update(b'fractal-kernel-O2-row512-v1');source_hash.update(' '.join(flags).encode());source_hash.update(pin['library_sha256'].encode())
    for tool in (cc,ld):source_hash.update(subprocess.check_output([tool,'--version']))
    build_id=int.from_bytes(source_hash.digest()[:4],'big') or 1
    unpack=runpy.run_path(str(DEMO/'elf_image.py'))['unpack_elf']
    objects=[]
    for name in ['core.c','entry.S','worker.c','fractal.c']:
        obj=OUT/(Path(name).stem+'.o');objects.append(obj)
        subprocess.run([cc,*flags,*(['-O2'] if name=='fractal.c' else []),'-I',str(DEMO),f'-DZZ_BUILD_ID=0x{build_id:08x}u','-c',str(DEMO/name),'-o',str(obj)],check=True)
    subprocess.run([ld,'-shared','-Bsymbolic','--no-undefined','-T',str(DEMO/'payload.ld'),*map(str,objects),'-o',str(OUT/'zzarm.elf')],check=True)
    image,rel,entry=unpack((OUT/'zzarm.elf').read_bytes())
    subprocess.run([cc,*flags,'-I',str(DEMO),'-c',str(DEMO/'mapping_probe.S'),'-o',str(OUT/'mapping.o')],check=True)
    subprocess.run([ld,'-shared','-Bsymbolic','--no-undefined','-T',str(DEMO/'payload.ld'),str(OUT/'mapping.o'),'-o',str(OUT/'mapping.elf')],check=True)
    probe,probe_rel,probe_entry=unpack((OUT/'mapping.elf').read_bytes())
    if probe_rel or probe_entry or len(probe)>1024:raise ValueError('Invalid mapping bootstrap')
    def array(name,data):return 'static const unsigned char '+name+'[]={'+','.join('0x%02x'%b for b in data)+'};\n'
    (OUT/'zz_payload.h').write_text(f'#define ZZ_ENTRY {entry}u\n'+array('zz_image',image)+array('zz_mapping_probe',probe)+'static const unsigned long zz_relocations[]={'+','.join(map(str,rel))+'};\n')
    container=[*engine,'run','--rm','--platform','linux/amd64','-v',str(ROOT)+':/work','-w','/work',IMAGE]
    common=[*container,'m68k-amigaos-gcc','-std=c99','-noixemul','-m68030','-O2','-Wall','-Wextra','-Werror',
        '-D__AMIGAOS3__','-DZZ_FRACTAL','-DZZ_RELEASE','-DZZ_APP_NAME="SDLZZFractal"','-DZZ_APP_VERSION="0.3"',
        '-DZZ_CLIENT_NAME="sdlfractal"','-DZZ_MIN_STACK=65536','-Iexamples/zzfractal','-Iinclude','-Ibuild/zzfractal']
    subprocess.run([*common,'-DIntuitionBase=ZZIntuitionBase','-c','examples/zzfractal/launcher.c','-o','build/zzfractal/launcher.o'],check=True)
    subprocess.run([*common,'examples/zzfractal/app.c','examples/zzfractal/xx19c.c','examples/zzfractal/fractal.c','build/zzfractal/launcher.o','libSDL2.a','-lm','-lamiga','-s','-o','build/zzfractal/SDLZZFractal'],check=True)
    binary=OUT/'SDLZZFractal'
    if binary.read_bytes()[:4]!=b'\0\0\x03\xf3':raise ValueError('Expected Amiga Hunk')
    record={'version':'0.3','application':'SDLZZFractal','standalone_release':True,'build_id':build_id,
        'source_identity_sha256':source_hash.hexdigest(),'sdl':pin,'compiler_image':IMAGE,'arm_flags':flags,
        'arm_kernel_flags':['-O2'],'arm_step_budget':512,'row_checkpoints':True,
        'work_slice_us':2000,'yield_us':1000,'integrity':'TIM3 request and timing bound FNV-1a','arm_image_bytes':len(image),'relocations':rel,'hardware_execution_verified_by_build':False,
        'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [binary,OUT/'zzarm.elf',OUT/'zz_payload.h']}}
    (OUT/'build.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
if __name__=='__main__':main()
