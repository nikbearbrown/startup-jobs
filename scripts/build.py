"""Validate source records and generate deterministic JSON, CSV and coverage exports."""
import csv, datetime, io, json, re
from pathlib import Path
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parents[1]
def domain(url):
    p=urlsplit(url)
    if p.scheme not in ('https','http') or not p.hostname or p.username or p.password:
        raise ValueError(f'Invalid public URL: {url}')
    return p.hostname.lower().removeprefix('www.')
def date(value):
    if datetime.date.fromisoformat(value)>datetime.date.today(): raise ValueError('Future evidence date')
def validate_headcount(q):
    domain(q['source_url']);date(q['checked_on'])
    if q.get('as_of'):date(q['as_of'])
    low,high=q['minimum'],q['maximum']
    if type(low) is not int or low<1 or (high is not None and (type(high) is not int or high<low)):
        raise ValueError('Invalid headcount bounds')
    if q['scope_type']!='company' or q['kind'] not in ('reported','estimated') or q['status']!='reviewed':
        raise ValueError('Invalid company headcount scope or status')
    if not all(q.get(k) for k in ('scope','statement','method','uncertainty')):raise ValueError('Missing scoped size evidence')
def validate(row):
    if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',row['id']): raise ValueError('Invalid id')
    if not row['name'].strip() or not row['industries']: raise ValueError('Missing name/industry')
    domain(row['website']); date(row['checked_on'])
    if row['review_status'] not in ('reviewed','needs-review'): raise ValueError('Invalid review state')
    if row.get('careers_url'): domain(row['careers_url'])
    sources=row['evidence']
    for e in sources:
        domain(e['url']); date(e['checked_on'])
        if not e['note'] or not e['publisher'] or not e['fields']: raise ValueError('Incomplete evidence')
    if row['review_status']=='reviewed':
        if len({e['publisher'] for e in sources})<2 or not any(e['primary'] for e in sources):
            raise ValueError('Reviewed record needs company and independent evidence')
        for field in ('name','website','industries'):
            if len({e['publisher'] for e in sources if field in e['fields']})<2:
                raise ValueError(f'{field} requires two publishers')
    for loc in row['locations']:
        if not all(loc.get(k) for k in ('city','region','country','verification')): raise ValueError('Incomplete location')
        if not any('city' in e['fields'] for e in sources): raise ValueError('City has no evidence')
        if loc['precision']=='city':
            if loc.get('coordinates') is not None or loc.get('address') is not None: raise ValueError('City location cannot claim street coordinates/address')
        elif loc['precision']=='street':
            coords=loc.get('coordinates')
            if not loc.get('address') or not coords or not -180<=coords[0]<=180 or not -90<=coords[1]<=90 or not any('address' in e['fields'] and 'coordinates' in e['fields'] for e in sources): raise ValueError('Street location requires address and coordinate evidence')
        else: raise ValueError('Unknown precision')
    return row

def build(root=ROOT):
    records=[]; ids=set(); domains=set()
    for p in sorted((root/'data/sources').glob('*.json')):
        src=json.loads(p.read_text()); date(src['checked_on'])
        for row in src['companies']:
            validate(row)
            d=domain(row['website'])
            if row['id'] in ids or d in domains: raise ValueError(f'Duplicate identity: {row["id"]}; merge evidence before publishing')
            ids.add(row['id']); domains.add(d)
            records.append(dict(row,source_file=str(p.relative_to(root)),canonical_domain=d))
    overlay_path=root/'data/enrichment/hiring-routes.json'
    if overlay_path.exists():
        by_id={r['id']:r for r in records};seen=set()
        for entry in json.loads(overlay_path.read_text()):
            eid=entry['company_id']
            if eid not in by_id or eid in seen:raise ValueError('Unknown/duplicate hiring entity')
            seen.add(eid);routes=entry['routes']
            for q in routes:
                domain(q['url']);domain(q['source_url']);date(q['checked_on'])
                if q['scope']!='company' or q['vacancy_status']!='not-verified' or not q['method']:raise ValueError('Invalid hiring evidence/scope')
            by_id[eid]['hiring_routes']=routes
    size_path=root/'data/enrichment/headcounts.json'
    if size_path.exists():
        by_id={r['id']:r for r in records};seen=set()
        for entry in json.loads(size_path.read_text()):
            eid=entry['company_id'];q=entry['observation']
            if eid not in by_id or eid in seen:raise ValueError('Unknown/duplicate size entity')
            seen.add(eid);validate_headcount(q);by_id[eid]['headcount']=q
    records.sort(key=lambda r:r['id'])
    (root/'data/companies.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
    size_fields=['statement','kind','minimum','maximum','scope','as_of','checked_on','source_url','method','uncertainty']
    out=io.StringIO(); fields=['id','name','website','industries','cities','review_status','checked_on','source_urls','notes','careers_url','reviewed_hiring_urls','hiring_checked_on','hiring_review_notes']+['headcount_'+k for k in size_fields]
    writer=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for r in records:
        values={k:r[k] for k in ('id','name','website','review_status','checked_on','notes')}
        values.update({'headcount_'+k:r.get('headcount',{}).get(k) for k in size_fields})
        values.update(hiring_review_notes='; '.join(q.get('review_note','') for q in r.get('hiring_routes',[]) if q.get('review_note')),careers_url=r.get('careers_url'),reviewed_hiring_urls='; '.join(q['url'] for q in r.get('hiring_routes',[])),hiring_checked_on='; '.join(q['checked_on'] for q in r.get('hiring_routes',[])),industries='; '.join(r['industries']),cities='; '.join(f'{l["city"]}, {l["region"]}, {l["country"]}' for l in r['locations']),source_urls='; '.join(e['url'] for e in r['evidence']))
        # Neutralize spreadsheet formula injection while retaining canonical JSON text.
        writer.writerow({k:("'"+v if isinstance(v,str) and v.startswith(('=','+','-','@')) else v) for k,v in values.items()})
    (root/'data/companies.csv').write_text(out.getvalue())
    coverage=dict(with_reviewed_hiring_route=sum(bool(r.get('hiring_routes')) for r in records),live_vacancies_verified=0,total=len(records),reviewed=sum(r['review_status']=='reviewed' for r in records),needs_review=sum(r['review_status']=='needs-review' for r in records),with_city=sum(bool(r['locations']) for r in records),street_verified=sum(any(l['precision']=='street' for l in r['locations']) for r in records),latest_check=max((r['checked_on'] for r in records),default=None),scope='Growing Boston-area and directory-affiliated company collection; affiliation is not a verified office or active-startup assertion. No estimate of total ecosystem coverage.')
    coverage['with_scoped_size_observation']=sum(bool(r.get('headcount')) for r in records)
    coverage['estimated_size_observations']=sum(r.get('headcount',{}).get('kind')=='estimated' for r in records)
    (root/'data/coverage.json').write_text(json.dumps(coverage,indent=2)+'\n'); return coverage
if __name__=='__main__': print(json.dumps(build(),indent=2))
