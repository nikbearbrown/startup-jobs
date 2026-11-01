"""Acquire documented NSF API pages for MA SBIR/STTR awards since 2023.
Public award facts only in exports; raw API pages stay local. Failed page receipts
are not retried. Pagination stops on errors, changing totals or repeated award IDs.
"""
import datetime,hashlib,json,time,urllib.parse,urllib.request
from pathlib import Path
from fetch import ROOT,UA,allowed,opener,check_url
BASE='https://api.nsf.gov/services/v1/awards.json'; CACHE=ROOT/'cache/nsf';OUT=ROOT/'data/discovery/nsf-ma-2023-awards.json';RECEIPTS=ROOT/'data/raw/nsf-api-pages.json'
FIELDS=['id','title','awardeeName','awardeeCity','awardeeStateCode','ueiNumber','date','startDate','expDate','activeAwd','fundProgramName']
def main():
 CACHE.mkdir(parents=True,exist_ok=True);old=json.loads(RECEIPTS.read_text()) if RECEIPTS.exists() else [];byurl={x['url']:x for x in old};receipts=[];awards={};scopes=[];date=datetime.datetime.now(datetime.timezone.utc).date().isoformat()
 for keyword in ['SBIR','STTR']:
  offset=0;total=None;seen=set();status='partial';reason=None
  while offset<3000:
   params=dict(keyword=keyword,awardeeStateCode='MA',dateStart='01/01/2023',rpp=25,offset=offset);u=BASE+'?'+urllib.parse.urlencode(params);k=hashlib.sha256(u.encode()).hexdigest();p=CACHE/(k+'.json');q=byurl.get(u)
   try:
    if q and q['status']!='fetched':raise ValueError('Previously failed page retained; no retry: '+q['reason'])
    if not q:
     # Reuse the authorized first-query probe without downloading it twice.
     probe_path=ROOT/'data/raw/nsf-api-probe.json';probe=json.loads(probe_path.read_text()) if probe_path.exists() else {}
     if probe.get('url')==u and probe.get('status')=='fetched' and (ROOT/'cache/nsf-api-probe.json').exists():b=(ROOT/'cache/nsf-api-probe.json').read_bytes()
     else:
      delay=allowed(u)
      if delay>60:raise ValueError('Crawl-delay limit; held')
      time.sleep(delay);check_url(u)
      with opener.open(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=35) as res:
       b=res.read(5_000_001)
       if res.status!=200 or len(b)>5_000_000:raise ValueError('Response status/size limit')
      json.loads(b)
     p.write_bytes(b);q=dict(url=u,status='fetched',checked_on=date,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),cache_key=k)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=q['sha256']:raise ValueError('Cached page hash mismatch; held without retry')
    data=json.loads(p.read_text())['response'];rows=data.get('award',[]);meta=data['metadata'];n=int(meta['totalCount'])
    if total is None:total=n
    if n!=total or int(meta['offset'])!=offset or len(rows)>25:raise ValueError('Pagination metadata changed or exceeded documented page size')
    for r in rows:
     if r['id'] in seen:raise ValueError('Repeated award ID across pages; incomplete pagination')
     seen.add(r['id']);clean={k:r.get(k) for k in FIELDS};clean.update(source_url=u,source_sha256=q['sha256'],checked_on=q['checked_on'],query=keyword)
     awards.setdefault(r['id'],clean)
    receipts.append(q);print(keyword,offset,len(rows),'of',total,flush=True)
    if len(seen)>=total:status='complete';break
    if len(rows)!=25:raise ValueError('Short page before reported total')
    offset+=25
   except Exception as e:
    reason=str(e)
    if not q:q=dict(url=u,status='blocked-or-failed',checked_on=date,reason=reason)
    receipts.append(q);break
  scopes.append(dict(keyword=keyword,awardee_state='MA',date_start='2023-01-01',reported_total=total,retrieved_unique=len(seen),status=status,reason=reason))
  RECEIPTS.write_text(json.dumps(receipts,indent=2)+'\n')
 OUT.write_text(json.dumps(dict(documentation_url='https://resources.research.gov/common/webapi/awardapisearch-v1.htm',checked_on=date,scope_results=scopes,limitations='Historical award observations, not company operational status, current website, current office, workforce or vacancies. orgUrl is the NSF directorate URL and is deliberately NOT a company domain.',awards=sorted(awards.values(),key=lambda x:x['id'])),indent=2)+'\n')
 print('Unique awards',len(awards),scopes)
if __name__=='__main__':main()
