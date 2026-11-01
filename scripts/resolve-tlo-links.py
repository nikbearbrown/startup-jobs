"""Resolve explicit Visit Website fields from TLO profile cards; no guessed domains."""
import argparse,hashlib,json
from pathlib import Path
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]
def main(site):
 cache=site/'cache/expansion';rows=json.loads((R/'data/discovery/mit-tlo.json').read_text())['candidates'];out=[];manifest=[]
 for q in rows:
  u=q['linked_url'];k=hashlib.sha256(u.encode()).hexdigest();m=json.loads((cache/(k+'.json')).read_text());web=[];reason=None
  if urlsplit(u).hostname=='tlo.mit.edu':
   if m['status']=='fetched':
    s=BeautifulSoup((cache/(k+'.html')).read_bytes(),'html.parser');links={urljoin(m['final_url'],a['href']) for a in s.select('a[href]') if a.get_text(' ',strip=True)=='Visit Website'}
    if len(links)==1:
     target=links.pop();p=urlsplit(target)
     if p.scheme in ('http','https') and p.hostname and p.hostname!='tlo.mit.edu' and not p.username:web=[dict(url=target,source_url=m['final_url'],source_sha256=m['sha256'],checked_on=m['checked_on'],method='Single explicit Visit Website link in the named MIT TLO profile; not identity verification')]
     else:reason='Visit Website target is not an external public company URL'
    else:reason='Missing or ambiguous Visit Website field'
   else:reason=m.get('reason','Profile not retrieved')
  else:web=[dict(url=u,source_url=q['source_url'],source_sha256=q['source_sha256'],checked_on=q['checked_on'],method='Explicit external link in named MIT TLO card; not identity verification')]
  out.append(dict(candidate_id=q['candidate_id'],name=q['name'],website_candidates=web,reason=reason))
  for w in web:manifest.append(dict(url=w['url'],candidate_id=q['candidate_id'],company_name=q['name'],source_url=w['source_url'],purpose='Company homepage identity and public careers navigation review; candidate only'))
 (R/'data/discovery/mit-tlo-resolved-links.json').write_text(json.dumps(out,indent=2)+'\n');(site/'data/ecosystem/expansion/phase13-company-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Resolved explicit company links',len(manifest),'held',sum(not q['website_candidates'] for q in out))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('site',type=Path);main(p.parse_args().site)
