"""Build the explicitly reviewed MassRobotics batch from cached official evidence.
Run with jobs-site checkout path. Requires manually reviewed data/massrobotics-review.tsv.
No live requests; no YC/MassBio/Greentown data is imported.
"""
import csv,json,re,sys,hashlib
from pathlib import Path
from urllib.parse import urlsplit,urljoin
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1];S=Path(sys.argv[1]);E=S/'data/ecosystem/expansion';C=S/'cache/expansion';today='2026-10-31'
receipt=next(r for r in map(json.loads,(E/'company-directory-manifest-receipts.jsonl').read_text().splitlines()) if r['source']=='massrobotics')
soup=BeautifulSoup((C/(receipt['cache_key']+'.html')).read_text(),'html.parser');directory={}
for el in soup.select('.content-wrap'):
 a=el.select_one('h1 a[href]')
 if a and len(el.select('h1'))==1:directory[a.get_text(' ',strip=True)]=urljoin(receipt['final_url'],a['href'])
rs={r['name']:r for r in json.loads((R/'data/raw/massrobotics-verification-receipts.json').read_text()) if r.get('source')=='massrobotics'}
contacts={r['name']:r for r in json.loads((R/'data/raw/massrobotics-verification-receipts.json').read_text()) if r.get('source')=='company-contact' and r['status']=='fetched'}
addresses={r['name']:r for r in csv.DictReader((E/'company-addresses.tsv').open(),delimiter='\t')}
old=json.loads((R/'data/companies.json').read_text());old_domains={urlsplit(r['website']).netloc.removeprefix('www.') for r in old if r.get('source_file')!='data/sources/massrobotics-reviewed.json'}
rows=[];locs=[]
for d in csv.DictReader((R/'data/massrobotics-review.tsv').open(),delimiter='\t'):
 name=d['name'];r=rs[name]
 if r['status']!='fetched' or name not in directory:raise ValueError('Unreviewable company '+name)
 domain=urlsplit(r['final_url']).netloc.removeprefix('www.')
 if domain in old_domains:raise ValueError('Existing domain requires explicit reconciliation '+domain)
 eid=re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-');links=json.loads((C/(r['cache_key']+'-links.json')).read_text());careers=next((a['url'] for a in links if re.fullmatch(r'careers?|jobs|join (?:our |the )?team',a['text'],re.I) and a['url'].startswith(('https://','http://'))),None)
 address=addresses.get(name);city=address['city'] if address else 'Boston'
 evidence=[dict(url=receipt['final_url'],publisher='MassRobotics',checked_on=today,primary=False,fields=['name','website','industries']+([] if address else ['city']),note='Resident directory identifies this company and links its website. Company descriptions may be supplied by members; this is not an independent operational audit.'),dict(url=r['final_url'],publisher=name,checked_on=today,primary=True,fields=['name','website','industries']+(['careers_url'] if careers else []),note='Official website corroborates identity and technical activity. Career link, when present, is navigation evidence, not a verified current vacancy.')]
 notes='Identity, website and sector cross-checked against official site and MassRobotics listing. Founding, ownership, payroll and current hiring remain unverified. '
 if address:
  source=contacts.get(name,r);evidence.append(dict(url=source['final_url'],publisher=name,checked_on=today,primary=True,fields=['city','address'],note=f"Official page lists {address['address']}. {address['location_role']}."));notes+='Company-stated local address; geocoding is reviewed separately.'
  locs.append(dict(entity_id='startup:'+eid,address=address['address'],location_role=address['location_role'],source_url=source['final_url'],checked_on=today,source_sha256=source['sha256'],method='manual review of company-stated address',confidence='company-stated office; occupancy not independently surveyed'))
 else:notes+='Boston denotes the directory-reported MassRobotics resident affiliation, not independently confirmed headquarters or a current physical office. Other offices may be outside Massachusetts; no precise marker assigned.'
 rows.append(dict(id=eid,name=name,website=r['final_url'],careers_url=careers,industries=[d['industry']],summary=d['summary'],founded_on=None,ownership=None,locations=[dict(city=city,region='MA',country='US',precision='city',verification='company-stated' if address else 'directory-reported resident affiliation; physical office unverified',address=None,coordinates=None)],review_status='reviewed',checked_on=today,notes=notes,evidence=evidence))
(R/'data/sources/massrobotics-reviewed.json').write_text(json.dumps(dict(id='massrobotics-reviewed',checked_on=today,companies=rows),indent=2)+'\n')
(E/'company-address-observations.json').write_text(json.dumps(locs,indent=2)+'\n')
accepted={r['name'] for r in rows};candidates=[dict(name=name,website=url,source_url=receipt['final_url'],checked_on=today,status='accepted-identity' if name in accepted else 'needs-review',reason='See reviewed source record' if name in accepted else 'Official content incomplete, inaccessible, ambiguous identity/lifecycle, or not reviewed sufficiently') for name,url in sorted(directory.items())]
(R/'data/discovery/massrobotics.json').write_text(json.dumps(candidates,indent=2)+'\n');print('Reviewed companies',len(rows),'Company-stated local addresses',len(locs),'Career links',sum(bool(r['careers_url']) for r in rows))
