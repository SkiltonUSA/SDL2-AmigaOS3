#!/usr/bin/env python3
"""Package the standalone Amiga executable, native icons, notices and metadata."""
import hashlib
import json
from pathlib import Path
import struct
import zipfile
ROOT=Path(__file__).resolve().parents[1]

def main():
    build=ROOT/'build/zzfractal';source=ROOT/'examples/zzfractal';dist=ROOT/'dist'
    record=json.loads((build/'build.json').read_text());binary=(build/'SDLZZFractal').read_bytes()
    if not record.get('standalone_release') or binary[:4]!=b'\0\0\x03\xf3':raise ValueError('Standalone Amiga Hunk required')
    if hashlib.sha256(binary).hexdigest()!=record['files']['SDLZZFractal']:raise ValueError('Executable build hash mismatch')
    tool=(source/'icons/SDLZZFractal.info').read_bytes();drawer=(source/'icons/drawer.info').read_bytes()
    for data,kind in ((tool,3),(drawer,2)):
        if len(data)<78 or data[:4]!=b'\xe3\x10\0\x01' or data[48]!=kind or struct.unpack_from('>I',data,74)[0]!=131072:
            raise ValueError('Expected native tool/drawer icon with a 131072-byte stack')
    files={'SDLZZFractal/SDLZZFractal':binary,'SDLZZFractal/SDLZZFractal.info':tool,'SDLZZFractal.info':drawer,
           'SDLZZFractal/build-info.json':(build/'build.json').read_bytes(),'SDLZZFractal/LICENSE':(ROOT/'LICENSE').read_bytes()}
    for name in ['ReadMe.txt','ThirdParty.txt','COPYING3','COPYING.RUNTIME']:
        files['SDLZZFractal/'+name]=(source/name).read_bytes()
    files['SHA256SUMS.txt']=''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in sorted(files.items())).encode()
    dist.mkdir(exist_ok=True);stage=build/'package';stage.mkdir(exist_ok=True)
    archive=dist/('SDLZZFractal-'+record['version']+'-XX19c.zip')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(files.items()):
            target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            executable=name=='SDLZZFractal/SDLZZFractal';target.chmod(0o755 if executable else 0o644)
            info=zipfile.ZipInfo(name,date_time=(2026,10,8,0,0,0));info.create_system=3
            info.external_attr=((0o100755 if executable else 0o100644)<<16);info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and set(z.namelist())==set(files)
        for name,data in files.items():assert z.read(name)==data
    metadata={'archive':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size,
        'executable_bytes':len(binary),'build_id':record['build_id'],'files':{n:hashlib.sha256(v).hexdigest() for n,v in files.items()}}
    (build/'package.json').write_text(json.dumps(metadata,indent=2)+'\n');print(json.dumps(metadata,indent=2))
if __name__=='__main__':main()
