"""Apply explicit reviewed decisions to the previous immutable 170-group ledger."""
import collections,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def build(root=R):
 previous=json.loads((root/'data/reviews/phase14-candidate-status.json').read_text());rows={r['candidate_id']:r for r in previous['reviews']}
 decisions=json.loads((root/'data/reviews/phase15-candidate-decisions.json').read_text());companies={r['id']:r for r in json.loads((root/'data/companies.json').read_text())};seen=set()
 for d in decisions:
  key=d['candidate_id']
  if key not in rows or key in seen:raise ValueError('Unknown or repeated candidate decision')
  seen.add(key)
  if rows[key].get('company_id'):raise ValueError('Cannot silently overwrite a previously resolved identity')
  if d['status']=='accepted-new-company':
   c=companies.get(d.get('company_id'))
   if not c or c['review_status']!='reviewed' or c['website']!=d['website_candidate']:raise ValueError('Acceptance requires matching reviewed export')
  elif d['status'] not in ('held-source-policy','pending-company-corroboration') or d.get('company_id'):raise ValueError('Unsupported unresolved status')
  rows[key]=dict(rows[key],**d)
 out=list(rows.values());counts=dict(collections.Counter(r['status'] for r in out));data=dict(summary=dict(total_groups=len(out),status_counts=counts,new_verified_companies=counts.get('accepted-new-company',0),existing_identities_confirmed=counts.get('confirmed-existing-company',0),unresolved_groups=sum(not r.get('company_id') for r in out),phase15_reviewed_groups=len(decisions),phase15_added_companies=sum(d['status']=='accepted-new-company' for d in decisions),limitations='Explicit review accounting, not a full verification of every NSF identity. Name-only NSF associations remain provisional except documented exact UEI matches.'),reviews=out)
 (root/'data/reviews/phase15-candidate-status.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data['summary'],indent=2));return data
if __name__=='__main__':build()
