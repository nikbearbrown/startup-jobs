"""Import an explicitly reviewed factual Boston-region subset of Engine Ventures.
Offline: source profiles and company pages are cached by the site's robots-aware collector.
No investor address is inherited. Unreviewed/global/acquired candidates remain discovery only.
"""
import csv,hashlib,json,re,sys
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1];S=Path(sys.argv[1]);E=S/'data/ecosystem/expansion';C=S/'cache/expansion';DATE='2026-10-31'
def cached(u):return json.loads((C/(hashlib.sha256(u.encode()).hexdigest()+'.json')).read_text())
profiles={}
for r in map(json.loads,(E/'phase2-company-profile-manifest-receipts.jsonl').read_text().splitlines()):
 if r['status']=='fetched':
  s=BeautifulSoup((C/(r['cache_key']+'.html')).read_text(),'html.parser');h=s.find('h1')
  if h:profiles[h.get_text(' ',strip=True)]=r
websites={r['name']:r['url'] for r in json.loads((E/'phase2-company-website-manifest.json').read_text())}
existing={urlsplit(r['website']).netloc.lower().removeprefix('www.'):r['id'] for r in json.loads((R/'data/companies.json').read_text()) if r.get('source_file')!='data/sources/engine-ventures-reviewed.json'}
rows=[];observations=[]
for d in csv.DictReader((R/'data/engine-ventures-review.tsv').open(),delimiter='\t'):
 name=d['name'];p=profiles[name];w=cached(websites[name]);a=cached(d['address_source']);assert w['status']==a['status']=='fetched'
 domain=urlsplit(w['final_url']).netloc.lower().removeprefix('www.')
 if domain in existing:raise ValueError('Requires manual duplicate reconciliation: '+name)
 eid=re.sub('[^a-z0-9]+','-',name.lower()).strip('-');links=json.loads((C/(w['cache_key']+'-links.json')).read_text());career=next((l['url'] for l in links if re.fullmatch(r'careers?|jobs|join us|work at finwave',l['text'],re.I) and l['url'].startswith(('https://','http://'))),None)
 evidence=[dict(url=p['final_url'],publisher='Engine Ventures',primary=False,fields=['name','website','industries'],checked_on=DATE,note='Investor profile corroborates identity, technical activity and official website. Portfolio statements may be company-supplied; investor affiliation does not prove local presence.'),dict(url=w['final_url'],publisher=name,primary=True,fields=['name','website','industries']+(['careers_url'] if career else []),checked_on=DATE,note='Official company page corroborates identity and technical activity. Career navigation is not evidence of a live vacancy.'),dict(url=a['final_url'],publisher=name,primary=True,fields=(['city'] if d['city'] else ['regional_presence'])+(['address'] if d['address'] else []),checked_on=DATE,note=d.get('location_note') or 'Official company page explicitly identifies '+(d['address'] or d['city']+' local presence')+'. Presence does not establish headquarters or the full operating footprint.')]
 notes='Identity, official website and sector reviewed against company and Engine Ventures pages. Location evidence is qualified below. Ownership, founding date and current vacancies are unverified. '
 if name=='Terrestrial Bio':notes+='Contact page lists 30 and 11 Cummings Park Drive; selected main contact address 30. Both are retained in local source evidence. '
 if name=='Axiomatic AI':notes+='The company describes a team across Boston, Barcelona and Toronto; this verifies city-level team presence, not a Boston office address. '
 if name=='Pascal':notes+='The official careers page says the company is based in Watertown; no street address has been verified. '
 if name=='WoHo':notes+='The official contact page labels the Cambridge address headquarters and spells Massachusetts as Massachussetts. The normalized street spelling is used for address matching; the source observation is retained. '
 if d.get('location_note'):notes+=d['location_note']+' '
 rows.append(dict(id=eid,name=name,website=w['final_url'],careers_url=career,industries=[d['industry']],summary=d['summary'],founded_on=None,ownership=None,locations=[dict(city=d['city'],region='MA',country='US',precision='city',verification=d.get('location_verification') or 'company-stated',address=None,coordinates=None)] if d['city'] else [],review_status='reviewed',checked_on=DATE,notes=notes,evidence=evidence))
 if d['address']:observations.append(dict(entity_id='startup:'+eid,address=d['address'],location_role='Company-listed contact address; not necessarily headquarters or a surveyed laboratory',source_url=a['final_url'],checked_on=DATE,source_sha256=a['sha256'],method='manual review of company-stated address',confidence='company-stated address; occupancy not independently surveyed'))
(R/'data/sources/engine-ventures-reviewed.json').write_text(json.dumps(dict(id='engine-ventures-reviewed',checked_on=DATE,companies=rows),indent=2)+'\n')
(E/'engine-company-address-observations.json').write_text(json.dumps(observations,indent=2)+'\n')
accepted={r['name'] for r in rows};candidates=[]
for name,p in profiles.items():
 reason='Reviewed Boston-region company and explicit official local presence' if name in accepted else 'Needs review: local presence, identity, access or lifecycle not sufficiently resolved'
 if name in ('Form Energy','Boston Metal'):reason='Already in collection; no duplicate added'
 if name=='Sync Computing':reason='Official website redirects to Capital One Software; acquisition/lifecycle reconciliation required'
 candidates.append(dict(name=name,website=websites.get(name),source_url=p['url'],checked_on=DATE,status='accepted-identity' if name in accepted else 'needs-review',reason=reason))
(R/'data/discovery/engine-ventures.json').write_text(json.dumps(candidates,indent=2)+'\n')
(R/'data/raw/engine-verification-receipts.json').write_text(json.dumps([json.loads(l) for f in ['phase2-company-profile-manifest-receipts.jsonl','phase2-company-website-manifest-receipts.jsonl','phase2-company-contact-manifest-receipts.jsonl','phase3-engine-presence-manifest-receipts.jsonl','phase4-company-presence-manifest-receipts.jsonl'] for l in (E/f).read_text().splitlines()],indent=2)+'\n')
print('New reviewed companies',len(rows),'address observations',len(observations),'career navigation links',sum(bool(r['careers_url']) for r in rows))
