"""Capture actual pages in isolated Edge browser contexts, after uc05_verify.py."""
from playwright.sync_api import sync_playwright
import json,pathlib
root=pathlib.Path(__file__).resolve().parents[1]; local=json.loads((root.parent/'runtime/uc05-local.json').read_text()); out=root/'docs/phase-1/assets'; base='http://127.0.0.1:15230'; results=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',headless=True)
 contexts={}; pages={}
 for who in ['a','b','anon']:
  contexts[who]=b.new_context(viewport={'width':1440,'height':1000},locale='en-US'); page=contexts[who].new_page(); pages[who]=page
  if who!='anon':
   page.goto(base+'/auth/signin'); page.get_by_placeholder('Username',exact=True).fill(local['credentials'][who]['username']); page.get_by_placeholder('Password',exact=True).fill(local['credentials'][who]['password']); page.get_by_role('button',name='Sign in',exact=True).click(); page.wait_for_timeout(900)
 def snap(who,path,file,expected=None):
  page=pages[who]; page.goto(base+path); page.wait_for_timeout(1400); body=page.locator('body').inner_text()
  if expected: assert expected in body,(file,body)
  page.screenshot(path=str(out/file),full_page=True); results.append({'actor':who,'url':page.url,'screenshot':file,'body':body})
 snap('a','/'+local['memo'],'uc05-a-private.png','UC05 谢宇轩')
 snap('b','/'+local['memo'],'uc05-b-denied.png')
 snap('anon','/'+local['memo'],'uc05-anon-normal.png')
 sharepath='/memos/shares/'+local['share'].split('/')[-1]
 snap('anon',sharepath,'uc05-anon-share.png','UC05 谢宇轩')
 page=pages['a']; page.get_by_role('button',name='Share',exact=True).click(); page.get_by_role('menuitem',name='Manage share links').click(); page.wait_for_timeout(700)
 page.screenshot(path=str(out/'uc05-share-panel.png'),full_page=True)
 results.append({'actor':'a','screenshot':'uc05-share-panel.png','body':page.locator('body').inner_text()})
 # Revoke the long-lived link through the app UI.
 page.get_by_title('Revoke',exact=True).last.click(); page.wait_for_timeout(600)
 snap('anon',sharepath,'uc05-anon-revoked.png','Sign in')
 # Show the available audience choices in the editor.
 page.get_by_role('button',name='Close',exact=True).click(); page.get_by_role('button',name='Edit',exact=True).click(); page.wait_for_timeout(600)
 page.get_by_role('button',name='Private',exact=True).click(); page.wait_for_timeout(300)
 page.screenshot(path=str(out/'uc05-audience-options.png'),full_page=True)
 (out/'uc05-browser.json').write_text(json.dumps({'browser':b.version,'contexts':'A, B and anonymous use three independent BrowserContexts','results':results},ensure_ascii=False,indent=2)); b.close()
