"""Additional SPACE and archived memo checks, using local credentials from the first run."""
import pathlib,json,urllib.request,urllib.error,sqlite3
root=pathlib.Path(__file__).resolve().parents[1]; out=root/'docs/phase-1/assets'; local=json.loads((root.parent/'runtime/uc05-local.json').read_text()); tokens={}; records=[]
def req(actor,method,path,body=None,expect=200,label=''):
 h={'Content-Type':'application/json'}
 if actor in tokens: h['Authorization']='Bearer '+tokens[actor]
 r=urllib.request.Request('http://127.0.0.1:15230'+path,data=json.dumps(body).encode() if body is not None else None,headers=h,method=method)
 try:
  with urllib.request.urlopen(r) as f: status=f.status; data=json.load(f)
 except urllib.error.HTTPError as e: status=e.code; data=json.load(e)
 if '/auth/' not in path: records.append(dict(label=label,actor=actor,method=method,path=path,request=body,status=status,response=data,expected=expect))
 assert status==expect,(label,status,data)
 return data
for who in ['admin','a','b']: tokens[who]=req('anon','POST','/api/auth/signin',{'passwordCredentials':local['credentials'][who]})['accessToken']
space=req('a','POST','/api/spaces',{'title':'UC05 test space'},label='create-space')
m=req('a','POST','/api/memos',{'content':'UC05 SPACE boundary','space':space['name'],'visibility':'SPACE'},label='create-space-memo')
req('a','GET','/api/'+space['name']+'/members',label='space-members')
for actor,status in [('a',200),('b',403),('anon',401),('admin',200)]: req(actor,'GET','/api/'+m['name'],expect=status,label='SPACE-'+actor)
req('a','POST','/api/'+m['name']+'/shares',{},400,'space-share-rejected')
n=req('a','POST','/api/memos',{'content':'UC05 archive boundary','visibility':'PRIVATE'},label='create-archive-sample')
s=req('a','POST','/api/'+n['name']+'/shares',{},label='archive-share-created')
req('a','PATCH','/api/'+n['name']+'?updateMask=state',{'name':n['name'],'state':'ARCHIVED'},label='archive-memo')
req('anon','GET','/api/shares/'+s['name'].split('/')[-1]+'/memo',expect=404,label='archive-share-inaccessible')
req('a','POST','/api/'+n['name']+'/shares',{},400,'archive-new-share-rejected')
# API data is saved without passwords or access tokens.
(out/'uc05-boundaries.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
db=sqlite3.connect('file:'+str(root.parent/'runtime/uc05-data/memos_prod.db')+'?mode=ro',uri=True); db.row_factory=sqlite3.Row
snapshot={}
for table,cols in [('memo','id,uid,creator_id,visibility,row_status,content,space_id'),('memo_share','id,uid,memo_id,creator_id,expires_ts')]:
 snapshot[table]=[dict(r) for r in db.execute('SELECT '+cols+' FROM '+table)]
(out/'uc05-sqlite.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)); print('Boundary checks:',len(records))
