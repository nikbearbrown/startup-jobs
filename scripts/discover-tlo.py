"""Freeze complete explicit MIT TLO startup-card pagination from reviewed cache.
Factual name, linked website and technology taxonomy only; no founding/local-office inference.
"""
import argparse,hashlib,json,re
from pathlib import Path
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
def main(site):
 cache=site/'cache/expansion';pages=['https://tlo.mit.edu/index.php/industry-entrepreneurs/startups']+['https://tlo.mit.edu/industry-entrepreneurs/startups?page='+str(n) for n in [1,2,3]];out=[];known=set(pages);pageaudit=[]
 for u in pages:
  k=hashlib.sha256(u.encode()).hexdigest();m=json.loads((cache/(k+'.json')).read_text());assert m['status']=='fetched';s=BeautifulSoup((cache/(k+'.html')).read_bytes(),'html.parser');cards=s.select('.startup-teaser')
  for a in s.select('.pager a[href]'):
   target=urljoin(m['final_url'],a['href'])
   assert target in known or target in ['https://tlo.mit.edu/industry-entrepreneurs/startups','https://tlo.mit.edu/industry-entrepreneurs/startups?page=0'],'Unenumerated pagination: '+target
  for card in cards:
   a=card.select_one('.startup-teaser__link');name=' '.join(a.stripped_strings);url=urljoin(m['final_url'],a['href']);p=urlsplit(url);assert p.scheme in ['https','http'] and p.hostname and not p.username
   tech=' '.join(card.select_one('.startup-teaser__technologies').stripped_strings).removeprefix('Technology Areas:').strip();year=card.select_one('.startup-teaser__date').get_text(strip=True)
   out.append(dict(candidate_id='mit-tlo-'+hashlib.sha256((name+'|'+url).encode()).hexdigest()[:16],name=name,linked_url=url,link_kind=('institutional-profile' if p.hostname=='tlo.mit.edu' else 'external-company-candidate'),technology_areas=[x.strip() for x in tech.split(',')],directory_year=year,source_url=m['final_url'],source_sha256=m['sha256'],checked_on=m['checked_on'],status='candidate',limitations='MIT licensing-showcase affiliation only. Directory year is not verified founding year. No current location, ownership, workforce or hiring inferred.'))
  pageaudit.append(dict(url=m['final_url'],cards=len(cards),sha256=m['sha256']))
 assert len({r['candidate_id'] for r in out})==len(out),'Repeated cards require review'
 (ROOT/'data/discovery/mit-tlo.json').write_text(json.dumps(dict(source='MIT Technology Licensing Office',pages=pageaudit,enumeration='All explicitly linked listing pages in this snapshot',candidates=out),indent=2)+'\n');print('TLO candidates',len(out),[q['cards'] for q in pageaudit])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('site',type=Path);main(p.parse_args().site)
