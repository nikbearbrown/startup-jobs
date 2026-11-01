"""Polite, opt-in public-page collector. Fetches one URL; never bypasses a block.
python3 scripts/fetch.py URL
Cache is local/ignored. A public metadata receipt records outcomes and content hashes.
"""
import datetime,hashlib,ipaddress,json,socket,sys,time,urllib.error,urllib.parse,urllib.request,urllib.robotparser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
UA='StartupJobsResearch/0.1 (+https://github.com/nikbearbrown/startup-jobs)'
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
opener=urllib.request.build_opener(NoRedirect)
def check_url(url):
 p=urllib.parse.urlsplit(url)
 if any(p.hostname==h or (p.hostname or '').endswith('.'+h) for h in ('ycombinator.com','massbio.org','greentown.org','linkedin.com','dbos.dev','formlabs.com','biobot.io','vulcanforms.com','transcendmechanics.com','labyrinthai.co','bostondynamics.com','lightmatter.com','lightmatter.co','liquid.ai','themisai.io','picklerobot.com','biodevek.com','vicarioussurgical.com','cogniteam.com','masscec.com','verticalsemi.com','nona-technologies.com','glyphic.bio','syntis.bio','groundtruth.ag','dmat.co','sesamesustainability.com','lydianlabs.com','gofourth.com')):raise ValueError('Source held by reviewed access/reuse policy; no automated collection')
 if p.scheme not in ('http','https') or not p.hostname or p.username or p.password:raise ValueError('Only public HTTP(S) URLs allowed')
 if p.port not in (None,80,443):raise ValueError('Non-web port')
 for a in socket.getaddrinfo(p.hostname,p.port or 443):
  if not ipaddress.ip_address(a[4][0]).is_global:raise ValueError('Non-public network target')
 return p

def get(url):
 check_url(url)
 try:
  with opener.open(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=25) as response:
   content=response.read(5_000_001)
   if len(content)>5_000_000:raise ValueError('Page exceeds 5 MB limit')
   return response.status,response.headers,content
 except urllib.error.HTTPError as e:return e.code,e.headers,b''

def allowed(url):
 p=check_url(url);robots=f'{p.scheme}://{p.netloc}/robots.txt'
 # Redirects on robots are unresolved; fail closed rather than assume permission.
 status,_,body=get(robots)
 if status==404:return 1
 if status!=200:raise ValueError(f'robots.txt unavailable ({status}); manual review required')
 robot=urllib.robotparser.RobotFileParser();robot.parse(body.decode('utf-8','replace').splitlines())
 if not robot.can_fetch(UA,url):raise ValueError('Disallowed by robots.txt')
 return max(1,robot.crawl_delay(UA) or 1)

def main(url):
 receipt={'requested_url':url,'checked_on':datetime.date.today().isoformat(),'method':'identified-http-client'}
 cache=ROOT/'cache';cache.mkdir(exist_ok=True)
 key=hashlib.sha256(url.encode()).hexdigest();file=cache/(key+'.html');meta=cache/(key+'.json')
 if file.exists() and meta.exists():
  check_url(url)
  print(json.dumps(json.loads(meta.read_text())));return
 try:
  current=url
  for _ in range(6):
   delay=allowed(current);time.sleep(delay);status,headers,body=get(current)
   if status in (301,302,303,307,308):current=urllib.parse.urljoin(current,headers['Location']);continue
   receipt.update(final_url=current,http_status=status)
   if status!=200:raise ValueError(f'HTTP {status}; stop, no bypass')
   if 'html' not in headers.get('Content-Type',''):raise ValueError('Expected HTML')
   file.write_bytes(body);receipt.update(status='fetched',sha256=hashlib.sha256(body).hexdigest(),bytes=len(body),cache_path=str(file.relative_to(ROOT)));meta.write_text(json.dumps(receipt,indent=2)+'\n');break
  else:raise ValueError('Too many redirects')
 except Exception as e:receipt.update(status='blocked-or-failed',reason=str(e))
 out=ROOT/'data/raw/fetch-receipts.jsonl'
 with out.open('a') as f:f.write(json.dumps(receipt)+'\n')
 print(json.dumps(receipt,indent=2))
 if receipt['status']!='fetched':sys.exit(1)
if __name__=='__main__':main(sys.argv[1])
