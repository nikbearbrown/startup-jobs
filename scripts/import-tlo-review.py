"""Accept explicit human-reviewed MIT TLO/company decisions; no automatic promotion.
Revalidates cached source hashes, named directory links, text anchors, city scope,
source holds and careers navigation. Never infers founding, workforce or geometry.
"""
import argparse,hashlib,json,re,unicodedata
from pathlib import Path
from urllib.parse import urlsplit,urldefrag,urljoin
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
def host(u):return (urlsplit(u).hostname or '').lower().removeprefix('www.')
def normalized(s):return ' '.join(unicodedata.normalize('NFKC',s).casefold().split())
class Review:
 def __init__(self,site,root=ROOT):
  self.site=site;self.root=root;self.cache=site/'cache/expansion';self.receipts={}
  for p in self.cache.glob('*.json'):
   if p.name.endswith('-links.json'):continue
   try:m=json.loads(p.read_text())
   except (ValueError,OSError):continue
   if not isinstance(m,dict) or 'requested_url' not in m:continue
   self.receipts[m['requested_url']]=m
   if m.get('final_url'):self.receipts.setdefault(m['final_url'],m)
  self.tlo={q['candidate_id']:q for q in json.loads((root/'data/discovery/mit-tlo.json').read_text())['candidates']}
  self.links={q['candidate_id']:q for q in json.loads((root/'data/discovery/mit-tlo-resolved-links.json').read_text())}
  self.holds={d for q in json.loads((root/'data/source-policy.json').read_text()) if q['status']=='held' for d in q.get('applies_to_domains',[host(q['url'])])}
 def page(self,url):
  u=urldefrag(url)[0];m=self.receipts.get(u)
  if not m or m['status']!='fetched':raise ValueError('Missing or failed reviewed page: '+url)
  if host(u) in self.holds or host(m['final_url']) in self.holds:raise ValueError('Held source: '+url)
  k=hashlib.sha256(m['requested_url'].encode()).hexdigest();b=(self.cache/(k+'.html')).read_bytes()
  if hashlib.sha256(b).hexdigest()!=m['sha256']:raise ValueError('Evidence hash mismatch')
  soup=BeautifulSoup(b,'html.parser')
  for el in soup(['script','style','noscript']):el.decompose()
  return m,soup,normalized(soup.get_text(' ',strip=True))
 def evidence(self,u,publisher,primary,fields,note):
  m,_,_=self.page(u);return dict(url=m['final_url'],publisher=publisher,primary=primary,fields=fields,checked_on=m['checked_on'],source_sha256=m['sha256'],note=note)
 def company(self,q):
  if q['decision']!='accept':raise ValueError('Only explicit accepted decisions can enter verified data')
  t=self.tlo[q['tlo_candidate_id']];links=self.links[t['candidate_id']]['website_candidates']
  if len(links)!=1 or links[0]['url']!=q['homepage_requested']:raise ValueError('Official company URL lacks unique named TLO link')
  w=links[0];home,_,text=self.page(q['homepage_requested'])
  if home['final_url']!=q['website'] or host(home['final_url'])!=host(w['url']):raise ValueError('Renamed/acquired host requires separate review, never automatic acceptance')
  independent,_,_=self.page(w['source_url'])
  if independent['sha256']!=w['source_sha256']:raise ValueError('TLO link provenance changed')
  _,_,citytext=self.page(q['city_source'])
  if normalized(q['city_text']) not in citytext or normalized(q['home_text']) not in text:raise ValueError('Reviewed city or sector text anchor missing')
  if q['city'] not in {'Boston','Cambridge','Woburn','Waltham','Lexington','Brookline','Newton','Somerville','Greater Boston'}:raise ValueError('City outside this explicitly reviewed Boston-region batch')
  if normalized(q['city']) not in normalized(q['city_text']) and not (q['city']=='Boston' and 'charlestown' in normalized(q['city_text'])):raise ValueError('Declared city differs from reviewed place text')
  if q['city_scope'] not in ['municipality','metropolitan-area']:raise ValueError('Unresolved geography scope')
  if q['city']=='Greater Boston' and q['city_scope']!='metropolitan-area':raise ValueError('Metro hiring area cannot become Boston city limits')
  ev=[self.evidence(q['homepage_requested'],q['name'],True,['name','website','industries'],'Official company identity and technology reviewed; short factual fields only.'),self.evidence(w['source_url'],'MIT Technology Licensing Office',False,['name','website','industries'],'Named MIT startup card/profile explicitly links the company domain; technology taxonomy: '+', '.join(t['technology_areas'])+'. Directory year is not founding year and MIT affiliation is not an office address.'),self.evidence(q['city_source'],q['name'],True,['city'],'Company contact or on-site team/careers statement supports '+q['city']+' at '+q['city_scope']+' scope; not an independent occupancy audit.')]
  careers=q['careers_url'];observation=None
  if careers:
   source,soup,_=self.page(q['careers_source']);observed={urljoin(source['final_url'],a['href']) for a in soup.select('a[href]')}
   if careers not in observed and urldefrag(careers)[0]!=source['final_url']:raise ValueError('Careers URL is not an explicit observed company link')
   target,_,_=self.page(careers)
   observation=dict(entity_id='startup:'+q['company_id'],company_name=q['name'],source_url=source['final_url'],source_sha256=source['sha256'],target_url=careers,label=q['name']+' — Careers',checked_on=q['reviewed_on'],method='explicit company navigation and target review',display_note=q['careers_note'] or 'Official company recruiting navigation; availability and vacancy count are not independently verified.')
   ev.append(self.evidence(careers,q['name'],True,['careers_url'],observation['display_note']))
  note='Official company and MIT TLO sources corroborate identity, website and broad industry. Current location is company-stated, not independently surveyed. No founding date, ownership, workforce or live-vacancy count inferred. MIT directory year is retained only in discovery evidence.'
  if q['city_scope']=='metropolitan-area':note+=' Greater Boston is a metropolitan hiring area; no municipality or map point is asserted.'
  if q['name']=='Electrified Thermal Solutions':note+=' Company says Charlestown, a Boston neighborhood; Amsterdam is a separate company location.'
  if q['careers_note']:note+=' '+q['careers_note']
  row=dict(id=q['company_id'],name=q['name'],website=q['website'],careers_url=careers,industries=[q['industry']],summary=q['summary'],founded_on=None,ownership=None,locations=[dict(city=q['city'],region='MA',country='US',precision='city',place_scope=q['city_scope'],verification='company-stated '+('metropolitan on-site hiring area; municipality unresolved' if q['city_scope']=='metropolitan-area' else 'contact or on-site team/careers city'),address=None,coordinates=None)],review_status='reviewed',checked_on=q['reviewed_on'],notes=note,evidence=ev)
  return row,observation
 def run(self):
  decisions=json.loads((self.root/'data/reviews/phase14-company-decisions.json').read_text());rows=[];hiring=[]
  for q in decisions:
   r,o=self.company(q);rows.append(r)
   if o:hiring.append(o)
  (self.root/'data/sources/mit-tlo-phase14-reviewed.json').write_text(json.dumps(dict(id='mit-tlo-phase14-reviewed',checked_on='2026-11-01',companies=rows),indent=2)+'\n')
  (self.site/'data/ecosystem/expansion/phase14-hiring-link-observations.json').write_text(json.dumps(hiring,indent=2)+'\n')
  print('Accepted',len(rows),'companies;',len(hiring),'reviewed hiring routes')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('site',type=Path);Review(p.parse_args().site).run()
