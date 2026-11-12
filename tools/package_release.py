"""Build a private checkpoint + database-free source archive with source DB guards.

This packaging helper is intentionally opt-in. It does not publish to GitHub.
Example (from project root):
 python tools/package_release.py --source-zip /path/to/previous.zip --output-dir /path/to/out --version V154
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

SKIP_DIRS={'.venv','.git','__pycache__','.pytest_cache','.mypy_cache','node_modules'}
PRIVATE_SUFFIXES=('.db','.sqlite','.sqlite3','.db-wal','.db-shm','.sqlite-wal','.sqlite-shm',
                  '.sqlite3-wal','.sqlite3-shm','.pem','.key','.p12','.pfx','.zip','.7z','.rar')
PRIVATE_NAMES={'credentials.json','id_rsa','id_ed25519','.env','.env.local','.env.production'}


def sha(data):return hashlib.sha256(data).hexdigest()


def database_hashes_in_zip(z):
    return {n.removeprefix('MATH_WEB_GITHUB_READY/'):sha(z.read(n)) for n in z.namelist()
            if n.startswith('MATH_WEB_GITHUB_READY/') and n.endswith(('.db','.sqlite','.sqlite3'))}


def pack(project_root, source_zip, output_dir, version):
    project_root=Path(project_root).resolve(strict=True)
    source_zip=Path(source_zip).resolve(strict=True)
    output_dir=Path(output_dir).resolve()
    if project_root in output_dir.parents or project_root == output_dir:
        raise ValueError('Output must be outside project root')
    with ZipFile(source_zip) as source:
        if source.testzip() is not None:
            raise ValueError('Source ZIP failed integrity check')
        baseline=database_hashes_in_zip(source)
        if not baseline:
            raise ValueError('Source archive lacks legacy SQLite files; cannot certify preservation')
        # A nonempty WAL may contain committed data absent from the .db member.
        # Never create an apparently complete checkpoint in that situation.
        if any(i.filename.endswith('-wal') and i.file_size > 0 for i in source.infolist()):
            raise ValueError('Source ZIP contains nonempty SQLite WAL; take a consistent SQLite backup first')
    found={}
    included=[]
    source_only_excluded=[]
    for f in sorted(project_root.rglob('*')):
        if any(c in SKIP_DIRS for c in f.relative_to(project_root).parts):continue
        if f.is_symlink():
            raise ValueError(f'Refusing symlink in package: {f.relative_to(project_root)}')
        if not f.is_file():continue
        relative=f.relative_to(project_root).as_posix()
        # WAL and SHM files are runtime state, not a reproducible SQL snapshot.
        # Nonempty WAL must be backed up through SQLite before any release.
        if relative.endswith('-wal'):
            if f.stat().st_size > 0:
                raise ValueError(f'Nonempty SQLite WAL requires online backup: {relative}')
            continue
        if relative.endswith('-shm'):
            continue
        if relative.endswith(('.db','.sqlite','.sqlite3')):
            found[relative]=sha(f.read_bytes())
        included.append((relative,f))
    for name,digest in baseline.items():
        if found.get(name)!=digest:
            raise ValueError(f'Original SQLite not byte-preserved: {name}')
    if not set(baseline) <= set(found):
        raise ValueError('One or more original DBs missing from source')
    for name in baseline:
        # immutable read validates the on-disk DB without creating WAL/SHM.
        with sqlite3.connect((project_root/name).as_uri()+'?mode=ro&immutable=1',uri=True) as conn:
            if conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError(f'SQLite integrity_check failed: {name}')
    unexpected=set(found)-set(baseline)
    if unexpected:
        raise ValueError('Unexpected SQLite files need manual review: '+', '.join(sorted(unexpected)))
    output_dir.mkdir(parents=True,exist_ok=True)
    private_path=output_dir/f'MATH_WEB_GITHUB_READY_{version}_PRIVATE_CHECKPOINT.zip'
    source_path=output_dir/f'MATH_WEB_GITHUB_READY_{version}_GITHUB_SOURCE_ONLY.zip'
    for target,public in [(private_path,False),(source_path,True)]:
        if target.exists():
            raise FileExistsError(f'Refusing to overwrite an existing release: {target}')
        with ZipFile(target,'x',compression=ZIP_DEFLATED,compresslevel=6,allowZip64=True) as zipout:
            for rel,path in included:
                if public and (rel.lower().endswith(PRIVATE_SUFFIXES)
                               or path.name.lower() in PRIVATE_NAMES
                               or (path.name.lower().startswith('.env') and not path.name.lower().endswith('.example'))):
                    source_only_excluded.append(rel)
                    continue
                zipout.write(path,arcname='MATH_WEB_GITHUB_READY/'+rel)
    output={}
    for target,public in [(private_path,False),(source_path,True)]:
        with ZipFile(target) as z:
            bad=z.testzip()
            if bad: raise ValueError('Corrupt output ZIP: '+bad)
            paths=[i.filename for i in z.infolist() if not i.is_dir()]
            if public and any(n.endswith(('.db','.sqlite','.sqlite3','-wal','-shm')) for n in paths):
                raise ValueError('SQLite leaked into source-only ZIP')
            output[target.name]={'files':len(paths),'bytes':target.stat().st_size,'sha256':sha(target.read_bytes()),
                                 'sqlite_files':sum(n.endswith(('.db','.sqlite','.sqlite3')) for n in paths)}
    return {'baseline_source':source_zip.name,'baseline_sqlite_files':len(baseline),
            'sqlite_files_preserved_exactly':True,'source_only_filtered_files':len(source_only_excluded),
            'filtered_file_names':source_only_excluded,'output':output,
            'security_note':'This is file-extension filtering only, not a complete source secret audit.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--source-zip',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--version',required=True)
    args=parser.parse_args()
    result=pack(args.project_root,args.source_zip,args.output_dir,args.version)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
