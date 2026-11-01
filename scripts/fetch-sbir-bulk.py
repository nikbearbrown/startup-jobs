"""Download the explicitly offered SBIR no-abstract CSV once; no API/private endpoint.
Raw file stays ignored. Fail closed on robots, redirects, HTTP errors, type or size.
A failed receipt prevents automatic retry; acquisition is separate from acceptance.
"""
import datetime,hashlib,json,time,urllib.request
from pathlib import Path
from fetch import ROOT,UA,allowed,check_url,opener
URL='https://data.www.sbir.gov/mod_awarddatapublic_no_abstract/award_data_no_abstract.csv'
RECEIPT=ROOT/'data/raw/sbir-bulk-receipt.json'
FILE=ROOT/'cache/sbir-awards-no-abstract.csv'
def main():
 if RECEIPT.exists():
  old=json.loads(RECEIPT.read_text());print(json.dumps(old,indent=2));return
 q=dict(url=URL,documentation_url='https://www.sbir.gov/data-resources',checked_on=datetime.datetime.now(datetime.timezone.utc).date().isoformat(),method='Single documented public bulk CSV; robots-aware identified client; no retries',status='blocked-or-failed')
 tmp=FILE.with_suffix('.partial');FILE.parent.mkdir(exist_ok=True)
 try:
  delay=allowed(URL)
  if delay>60:raise ValueError('Crawl delay exceeds interactive collection window; held')
  time.sleep(delay);check_url(URL)
  with opener.open(urllib.request.Request(URL,headers={'User-Agent':UA}),timeout=45) as res,tmp.open('wb') as f:
   if res.status!=200 or 'csv' not in res.headers.get('Content-Type','').lower():raise ValueError('Expected HTTP 200 CSV; no redirects accepted')
   digest=hashlib.sha256();total=0
   while chunk:=res.read(1024*1024):
    total+=len(chunk)
    if total>150_000_000:raise ValueError('Bulk file exceeds documented-source safety limit')
    digest.update(chunk);f.write(chunk)
   q.update(status='fetched',bytes=total,sha256=digest.hexdigest(),last_modified=res.headers.get('Last-Modified'),content_type=res.headers.get('Content-Type'))
  tmp.replace(FILE)
 except Exception as e:q['reason']=str(e)
 RECEIPT.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))
if __name__=='__main__':main()
