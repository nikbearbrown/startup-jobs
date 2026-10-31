"""Copy reviewed company hiring navigation from the site audit, preserving scope/evidence.
Usage: python3 scripts/import-hiring-review.py ../jobs-site/public/ecosystem/directory.json
No network; candidate companies are never introduced by this importer.
"""
import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];d=json.loads(Path(sys.argv[1]).read_text());rows=[]
for r in d['records']:
 if r['kind']=='startup' and r.get('hiring_routes'):
  assert all(q['scope']=='company' and q['vacancy_status']=='not-verified' for q in r['hiring_routes'])
  rows.append(dict(company_id=r['id'].removeprefix('startup:'),routes=r['hiring_routes']))
(R/'data/enrichment/hiring-routes.json').write_text(json.dumps(sorted(rows,key=lambda r:r['company_id']),indent=2)+'\n');print('Company hiring routes',len(rows))
