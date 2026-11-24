"""UC-05: isolated local HTTP verification; run against a fresh Memos 26.11.0 instance."""
import json, urllib.request, urllib.error, secrets, pathlib, datetime, time
BASE='http://127.0.0.1:15230'
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/phase-1/assets'; OUT.mkdir(parents=True,exist_ok=True)
records=[]; tokens={}; users={}; creds={}
def req(actor,method,path,body=None,expect=None,label=''):
    headers={'Content-Type':'application/json'}
    if actor in tokens: headers['Authorization']='Bearer '+tokens[actor]
    r=urllib.request.Request(BASE+path,data=json.dumps(body).encode() if body is not None else None,headers=headers,method=method)
    try:
        with urllib.request.urlopen(r) as f: status=f.status; data=json.load(f)
    except urllib.error.HTTPError as e: status=e.code; data=json.load(e)
    if '/auth/' not in path and path!='/api/users': records.append(dict(label=label,actor=actor,method=method,path=path,request=body,status=status,response=data,expected=expect))
    if expect is not None: assert status==expect,(label,status,data)
    return data
for who in ['admin','a','b']:
    username='uc05'+who; password=secrets.token_urlsafe(18); creds[who]={'username':username,'password':password}
    users[who]=req('admin' if who!='admin' else 'anon','POST','/api/users',{'username':username,'password':password,'displayName':'UC05 '+who.upper(),'role':'USER' if who!='admin' else 'ADMIN'},200)
    login=req('anon','POST','/api/auth/signin',{'passwordCredentials':creds[who]},200); tokens[who]=login['accessToken']
assert users['admin']['role']=='ADMIN' and users['a']['role']==users['b']['role']=='USER'
memo=req('a','POST','/api/memos',{'content':'UC05 谢宇轩：可见性与分享测试笔记。','visibility':'PRIVATE'},200,'create-private'); name=memo['name']
for visibility in ['PRIVATE','PROTECTED','PUBLIC']:
    if visibility!='PRIVATE': req('a','PATCH','/api/'+name+'?updateMask=visibility',{'name':name,'visibility':visibility},200,'set-'+visibility)
    for actor,status in [('a',200),('b',403 if visibility=='PRIVATE' else 200),('anon',401),('admin',200)]:
        req(actor,'GET','/api/'+name,expect=status,label='private-instance-'+visibility)
req('admin','PATCH','/api/instance/settings/ACCESS',{'name':'instance/settings/ACCESS','accessSetting':{'accessMode':'INSTANCE_ACCESS_MODE_PUBLIC'}},200,'instance-public')
req('anon','GET','/api/'+name,expect=200,label='public-instance-PUBLIC')
for visibility in ['PROTECTED','PRIVATE']:
    req('a','PATCH','/api/'+name+'?updateMask=visibility',{'name':name,'visibility':visibility},200,'set-'+visibility)
    req('anon','GET','/api/'+name,expect=401,label='public-instance-'+visibility)
req('admin','PATCH','/api/instance/settings/ACCESS',{'name':'instance/settings/ACCESS','accessSetting':{'accessMode':'INSTANCE_ACCESS_MODE_PRIVATE'}},200,'instance-private')
req('b','POST','/api/'+name+'/shares',{},403,'nonowner-create-share')
req('a','POST','/api/'+name+'/shares',{'expireTime':'2020-01-01T00:00:00Z'},400,'past-expiry')
share=req('a','POST','/api/'+name+'/shares',{},200,'create-share'); token=share['name'].split('/')[-1]
for actor in ['a','b','anon']: req(actor,'GET','/api/shares/'+token+'/memo',expect=200,label='private-shared')
req('b','DELETE','/api/'+share['name'],expect=403,label='nonowner-revoke')
req('b','PATCH','/api/'+name+'?updateMask=content',{'name':name,'content':'unauthorized'},403,'nonowner-write')
req('a','DELETE','/api/'+share['name'],expect=200,label='revoke')
req('anon','GET','/api/shares/'+token+'/memo',expect=404,label='revoked-share')
req('anon','GET','/api/shares/invalid-test-token/memo',expect=404,label='invalid-share')
expiry=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=3)).isoformat().replace('+00:00','Z')
short=req('a','POST','/api/'+name+'/shares',{'expireTime':expiry},200,'create-short-share'); time.sleep(4)
req('anon','GET','/api/shares/'+short['name'].split('/')[-1]+'/memo',expect=404,label='expired-share')
# Leave one live link for browser verification; revoked links remain recorded above.
live=req('a','POST','/api/'+name+'/shares',{},200,'browser-share')
req('a','GET','/api/'+name+'/shares',expect=200,label='list-shares-includes-expired')
(OUT/'uc05-requests.json').write_text(json.dumps({'date':datetime.datetime.now().astimezone().isoformat(),'base':BASE,'version':req('anon','GET','/api/instance/profile'),'users':users,'records':records},ensure_ascii=False,indent=2))
local=ROOT.parent/'runtime/uc05-local.json'; local.write_text(json.dumps({'credentials':creds,'memo':name,'share':live['name']},ensure_ascii=False)); local.chmod(0o600)
print(json.dumps({'checks':len(records),'memo':name,'share':live['name'],'roles':{k:v['role'] for k,v in users.items()}},ensure_ascii=False))
