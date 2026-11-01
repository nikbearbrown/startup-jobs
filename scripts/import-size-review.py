"""Copy company-scoped source observations, never research or local-office counts.
Usage: python3 scripts/import-size-review.py ../jobs-site/data/ecosystem/headcounts.json
"""
import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
rows=[]
for r in json.loads(Path(sys.argv[1]).read_text()):
 if not r['entity_id'].startswith('startup:'):continue
 assert r['scope_type']=='company'
 q=dict(r);eid=q.pop('entity_id').removeprefix('startup:')
 rows.append(dict(company_id=eid,observation=q))
(R/'data/enrichment/headcounts.json').write_text(json.dumps(sorted(rows,key=lambda r:r['company_id']),indent=2)+'\n')
print('Company-scoped size observations',len(rows))
