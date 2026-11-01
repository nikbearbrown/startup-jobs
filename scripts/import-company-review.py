"""Replay explicit multi-source decisions against cached evidence; never auto-promote.
Supports exact named domain links or a company-published UEI corroborated by NSF.
Current geography, careers and precise address review remain separate decisions.
"""
import argparse,hashlib,importlib.util,json
from pathlib import Path
from urllib.parse import urljoin,urlsplit
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('tlo',ROOT/'scripts/import-tlo-review.py');tlo=importlib.util.module_from_spec(spec);spec.loader.exec_module(tlo)
class Review(tlo.Review):
 def company(self,q):
  if q['decision']!='accept':raise ValueError('Explicit acceptance required')
  home,soup,text=self.page(q['website'])
  if tlo.host(home['final_url'])!=tlo.host(q['website']):raise ValueError('Unreviewed domain change')
  if tlo.normalized(q['home_text']) not in text:raise ValueError('Company technology anchor missing')
  queue=json.loads((self.root/'data/discovery/company-review-queue.json').read_text())['candidates']
  candidate=next(x for x in queue if x['candidate_id']==q['candidate_id'])
  ev=[self.evidence(q['website'],q['name'],True,['name','website','industries'],'Official named company identity, domain and technology. Short factual fields only; no performance claims endorsed.')]
  if q['identity_method']=='named independent page with explicit company-domain link':
   source,ind,text2=self.page(q['independent_url'])
   links={tlo.host(urljoin(source['final_url'],a['href'])) for a in ind.select('a[href]')}
   if tlo.host(q['website']) not in links or tlo.host(q['website'])==tlo.host(q['independent_url']):raise ValueError('Independent explicit company-domain link required')
   if tlo.normalized(q['independent_text']) not in text2 or tlo.normalized(q['name'].split()[0]) not in text2:raise ValueError('Named independent sector anchor required')
   ev.append(self.evidence(q['independent_url'],q['independent_publisher'],False,['name','website','industries'],'Named institutional or investor page explicitly links company domain and corroborates broad technology. Portfolio evidence may repeat company information. Historical city, size and founding fields are not adopted.'))
  elif q['identity_method']=='exact company-published UEI matched to NSF award':
   _,_,identity=self.page(q['identity_source'])
   if tlo.host(q['identity_source'])!=tlo.host(q['website']) or q['uei'].lower() not in identity:raise ValueError('UEI must be explicitly published on company domain')
   award=next((a for a in candidate['award_observations'] if a['id']==q['award_id'] and a['ueiNumber']==q['uei']),None)
   if not award or candidate['uei']!=q['uei'] or tlo.normalized(q['independent_text']) not in tlo.normalized(award['title']):raise ValueError('Exact NSF UEI/technology match required')
   raw=(self.root/'cache/nsf'/(hashlib.sha256(award['source_url'].encode()).hexdigest()+'.json')).read_bytes()
   if hashlib.sha256(raw).hexdigest()!=award['source_sha256']:raise ValueError('NSF evidence hash mismatch')
   original=next((a for a in json.loads(raw)['response']['award'] if a['id']==q['award_id']),None)
   if not original or any(original.get(k)!=award.get(k) for k in ['id','title','awardeeName','ueiNumber']):raise ValueError('NSF observation differs from original evidence')
   # Public sanitized award observations preserve original API URL/hash; no private contact fields.
   ev.append(dict(url=award['source_url'],publisher='National Science Foundation',primary=False,fields=['name','website','industries'],checked_on=award['checked_on'],source_sha256=award['source_sha256'],note='Award '+award['id']+' names Quantivly and radiology digital-twin work. Its UEI exactly matches the official company legal page, establishing domain-owner identity; NSF does not itself publish a website link. Award city is historical, not current office proof.'))
   ev.append(self.evidence(q['identity_source'],q['name'],True,['name','website'],'Official legal page publishes the exact UEI used for the NSF identity match.'))
  else:raise ValueError('Unsupported identity method')
  _,_,citytext=self.page(q['city_source'])
  if tlo.normalized(q['city_text']) not in citytext or q['city'].lower() not in tlo.normalized(q['city_text']):raise ValueError('Explicit company city anchor required')
  if q['city'] not in {'Waltham','Cambridge','Somerville','Newton'}:raise ValueError('City outside explicitly reviewed batch')
  if tlo.host(q['city_source'])!=tlo.host(q['website']):
   navmeta,_,_=self.page(q['city_navigation_source']);board=q['embedded_board']
   nav=tlo.BeautifulSoup((self.cache/(hashlib.sha256(navmeta['requested_url'].encode()).hexdigest()+'.html')).read_bytes(),'html.parser')
   if not nav.select_one('script[jobboard="'+board+'"]') or urlsplit(q['city_source']).hostname!='jobs.polymer.co' or urlsplit(q['city_source']).path!='/'+board:raise ValueError('External city evidence lacks exact official embedded board')
  ev.append(self.evidence(q['city_source'],q['name'],True,['city'],'Company-stated '+q['city']+' contact or recruiting location; not an independent occupancy audit.'))
  source,nav,_=self.page(q['careers_source']);urls={urljoin(source['final_url'],a['href']) for a in nav.select('a[href]')}
  if q['careers_url'] not in urls:raise ValueError('Unobserved careers navigation')
  self.page(q['careers_url'])
  ev.append(self.evidence(q['careers_url'],q['name'],True,['careers_url'],q['careers_note']))
  row=dict(id=q['company_id'],name=q['name'],website=q['website'],careers_url=q['careers_url'],industries=[q['industry']],summary=q['summary'],founded_on=None,ownership=None,locations=[dict(city=q['city'],region='MA',country='US',precision='city',verification='company-stated contact or recruiting city',address=None,coordinates=None)],review_status='reviewed',checked_on=q['reviewed_on'],notes='Company and independent institutional/investor/government evidence corroborate identity, domain and broad technology. NSF candidate matching does not imply independently verified UEI ownership except where an exact company-published UEI is documented. No founding date, workforce, ownership, office footprint or live vacancy count inferred. '+q['careers_note'],evidence=ev)
  hiring=dict(entity_id='startup:'+q['company_id'],company_name=q['name'],source_url=source['final_url'],source_sha256=source['sha256'],target_url=q['careers_url'],label=q['name']+' — Careers',checked_on=q['reviewed_on'],method='explicit company navigation and target review',display_note=q['careers_note'])
  address=None
  if q.get('address'):
   # Decision must identify a source street as well as city; coordinate generation is downstream.
   street=q['address'].split(',')[0].replace('Street','St')
   if tlo.normalized(street) not in citytext.replace('street','st'):raise ValueError('Street anchor absent')
   m,_,_=self.page(q['city_source'])
   address=dict(entity_id='startup:'+q['company_id'],address=q['address'],source_url=m['final_url'],source_sha256=m['sha256'],checked_on=m['checked_on'],location_role=q['location_role'],observation='Explicit official company contact address; not an independent occupancy audit.',confidence='Company-stated contact address; geocoder only locates the street address')
  return row,hiring,address
 def run(self):
  decisions=json.loads((self.root/'data/reviews/phase15-company-decisions.json').read_text());results=[self.company(q) for q in decisions]
  (self.root/'data/sources/nsf-candidates-phase15-reviewed.json').write_text(json.dumps(dict(id='nsf-candidates-phase15-reviewed',checked_on='2026-11-01',companies=[r[0] for r in results]),indent=2)+'\n')
  for suffix,items in [('hiring-link-observations',[r[1] for r in results]),('address-observations',[r[2] for r in results if r[2]])]:
   (self.site/('data/ecosystem/expansion/phase15-'+suffix+'.json')).write_text(json.dumps(items,indent=2)+'\n')
  print('Accepted',len(results),'companies and hiring routes;',sum(bool(r[2]) for r in results),'address review inputs')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('site',type=Path);Review(p.parse_args().site).run()
