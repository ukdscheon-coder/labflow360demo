import hashlib,json,datetime,urllib.request,urllib.error,pathlib,re
root=pathlib.Path(__file__).resolve().parents[1]
data=json.loads((root/'regulatory-sources.json').read_text())
out=root/'regulatory-monitor.json'
previous={}
if out.exists():
 try: previous={x['id']:x for x in json.loads(out.read_text()).get('sources',[])}
 except Exception: pass
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
results=[]
for s in data['sources']:
 row={**s,'checked_at':now,'status':'error','changed':False,'review_status':'requires_human_review'}
 try:
  req=urllib.request.Request(s['url'],headers={'User-Agent':'LabFlow360-RegulatoryMonitor/0.1 (public sources only)','Accept':'text/html,application/xhtml+xml,text/plain'})
  with urllib.request.urlopen(req,timeout=20) as response:
   content=response.read(2000000)
   typ=response.headers.get('Content-Type','')
   digest=hashlib.sha256(content).hexdigest()
   old=previous.get(s['id'],{}).get('sha256')
   row.update(status='fetched',http_status=response.status,content_type=typ,sha256=digest,changed=bool(old and old!=digest),previous_sha256=old)
 except Exception as e: row['error']=str(e)[:300]
 results.append(row)
out.write_text(json.dumps({'generated_at':now,'sources':results},indent=2,ensure_ascii=False)+'\n')
print('Checked',len(results),'sources; changed',sum(x['changed'] for x in results),'errors',sum(x['status']=='error' for x in results))
