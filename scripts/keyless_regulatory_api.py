"""Fetch metadata from keyless official public APIs; never infer legal compliance."""
import datetime,json,urllib.request,urllib.error,hashlib,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
catalog=json.loads((root/'regulatory-api-catalog.json').read_text())
out=root/'regulatory-api-snapshots.json'
old={}
if out.exists():
 try:old={x['id']:x for x in json.loads(out.read_text()).get('sources',[])}
 except Exception:pass
results=[]
for s in catalog['sources']:
 row={'id':s['id'],'country':s['country'],'authority':s['authority'],'access':s['access'],'endpoint':s.get('endpoint'),'status':'not_attempted','review_required':True}
 if s['access']=='no_key' and s.get('endpoint'):
  try:
   req=urllib.request.Request(s['endpoint'],headers={'User-Agent':'LabFlow360-Research-Pilot/0.1 (regulatory monitoring; contact via GitHub repository)','Accept':'application/json,application/atom+xml,application/xml;q=0.8,*/*;q=0.5'})
   with urllib.request.urlopen(req,timeout=18) as resp:
    body=resp.read(1000000)
    digest=hashlib.sha256(body).hexdigest()
    previous=old.get(s['id'],{}).get('sha256')
    row.update(status='fetched',http_status=resp.status,sha256=digest,changed=bool(previous and previous!=digest),content_type=resp.headers.get('Content-Type',''),bytes_sampled=len(body))
  except Exception as exc:row.update(status='error',error=str(exc)[:250])
 results.append(row)
out.write_text(json.dumps({'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'note':'Content changes are NOT confirmed legal amendments. No automatic legal activation.','sources':results},ensure_ascii=False,indent=2)+'\n')
print('fetched:',sum(x['status']=='fetched' for x in results),'errors:',sum(x['status']=='error' for x in results))
