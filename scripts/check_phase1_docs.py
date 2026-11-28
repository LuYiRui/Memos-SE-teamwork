"""核对文档的固定源码链接、相对资源及既有UC-05证据；不启动Memos。"""
import argparse, hashlib, json, re, subprocess
from pathlib import Path
from urllib.parse import unquote
SHA = 'b40d8a7b573774c52b022c8d6537d6baf2129dc0'
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]; docs=root/'docs/phase-1'; assets=docs/'assets'
    actual=subprocess.check_output(['git','-C',str(args.source),'rev-parse','HEAD'],text=True).strip()
    if actual != SHA: raise SystemExit('源码提交与26.11.0不符')
    files=[]; errors=[]
    for md in sorted((root/'docs').rglob('*.md')):
        text=md.read_text(); links=re.findall(r'https://github\.com/usememos/memos/blob/'+SHA+r'/([^\s)#]+)(#[^\s)]+)?',text)
        for name,frag in links:
            target=args.source/unquote(name)
            if not target.is_file(): errors.append(f'{md.name}: 源码路径不存在: {name}'); continue
            line=re.search(r'L(\d+)(?:-L(\d+))?',frag)
            if line and int(line.group(2) or line.group(1))>len(target.read_text().splitlines()): errors.append(f'{md.name}: 行号超界: {name}{frag}')
        for name in re.findall(r'\]\(([^)\s]+)\)',text):
            if name.startswith(('http:','https:','#')): continue
            if not (md.parent/unquote(name.split('#')[0])).exists(): errors.append(f'{md.name}: 相对文件不存在: {name}')
        files.append({'file':md.relative_to(root).as_posix(),'fixed_source_links':len(links)})
    manifest=json.loads((assets/'uc05-sha256.json').read_text()); hashes=[]
    for name,expected in manifest.items():
        ok=hashlib.sha256((assets/name).read_bytes()).hexdigest()==expected
        hashes.append({'file':name,'matches':ok})
        if not ok: errors.append('UC05证据摘要不一致: '+name)
    archived=[]
    for name in ['uc05-requests.json','uc05-boundaries.json']:
        data=json.loads((assets/name).read_text()); records=data if isinstance(data,list) else data['records']
        checks=[r for r in records if r.get('expected') is not None]; mismatches=[i for i,r in enumerate(records) if r.get('expected') is not None and r['expected']!=r['status']]
        archived.append({'file':name,'records':len(records),'assertions':len(checks),'mismatches':mismatches})
        if mismatches: errors.append(name+': 归档断言不一致')
    result={'date':'2026-11-28','upstream_commit':actual,'method':'文档、固定提交及既有证据静态核对；非运行复验','documents':files,'uc05_sha256':hashes,'uc05_archived_assertions':archived,'errors':errors}
    out=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output: args.output.write_text(out)
    print(out)
    raise SystemExit(bool(errors))
if __name__=='__main__': main()
