"""Summarize all frozen discovery groups without promoting unresolved identities.
Only explicit decisions change accepted status. Fetch outcomes are not verification.
"""
import argparse,collections,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NOTES={
 'AgZen':'Reviewed official homepage, about and jobs pages do not establish a current Boston-area company location. MIT lab location is not substituted.',
 'Arculus Solutions':'Official recruiting page names an on-site Alexandria, Virginia role. No reviewed current Boston company location; do not infer absence of other offices.',
 'Area2.Ai':'Retrieved homepage exposes only a short title; identity, industry and current city need additional evidence.',
 'Artificial Axon Labs':'Official company science is identifiable, but reviewed page does not establish a current Boston-area company location.',
 'Avanti Battery Company':'Named directory domain redirects to an expired-domain sales page. Not accepted as a current company website.',
 'Bilayer Therapeutics':'Retrieved page has no usable body content; current identity and city remain unresolved.',
 'Cache DNA':'Official Find us page states San Carlos, California headquarters; a current Boston-area operation is not established by MIT affiliation.',
 'CoFlo Medical':'Official company site lacks a current city. Historic MIT competition and research affiliation are not current company occupancy evidence.',
 'Found Energy':'Directory domain redirects to Found Industries; current site has a Found Energy division. Corporate identity/rename relationship needs explicit reconciliation.',
 'Ikigai Labs':'Directory domain redirects to an acquisition announcement. Do not count an independently active Boston startup or substitute acquirer workforce/jobs.',
 'Nocturnal':'Previously fetched gzip bytes decoded offline, without refetch. Page names Kendall Square and a 2027 launch; technology details and present business status are not sufficiently corroborated for acceptance.',
 'OptiCore':'Linked domain shows a Korean public optical-transceiver company. Relationship to the MIT directory entity and Boston presence are unresolved.',
 'Perceptra':'Official careers page lists San Francisco and Eindhoven roles. No current Boston-region company place is established; MIT adviser affiliation is not substituted.',
 'RevelNext':'Directory name and current Revel Ostomy brand differ; current legal identity/brand relationship and Boston presence need corroboration.',
 'SiTration':'Company republishes a Watertown press headline, but reviewed contact/careers pages do not establish current local occupancy. Recruiting page links LinkedIn, which is not fetched.',
 'Sync Computing':'Directory domain redirects to an acquirer product. Current separate identity and Boston operation unresolved; no acquirer jobs substituted.',
 'Thiozen':'Official Join page points to LinkedIn; no destination extraction. Reviewed company pages do not establish current Boston-area office.',
 'TI Solutions':'Boston references describe scientific advisers academic affiliations, not company offices. No precise or city company location inferred.',
 'VasoRX':'Official contact gives San Diego, California and a private-mailbox label. No reviewed current Boston-area operation; no physical lab inferred.',
 'Xibus Systems':'Official site announces merger with Fluorityx. Historic Boston-region statement does not resolve current separate identity or operations.'
}
def build(site,root=ROOT):
 queue=json.loads((root/'data/discovery/company-review-queue.json').read_text());decisions=json.loads((root/'data/reviews/phase14-company-decisions.json').read_text());accepted={r['tlo_candidate_id']:r for r in decisions};existing={'Crabi Robotics':'crabi-robotics','Emvolon':'emvolon','Matrisome Bio':'matrisome-bio','Kano Therapeutics':'kano'}
 receipts={}
 for p in sorted((site/'data/ecosystem/expansion').glob('phase1[34]*manifest-receipts.jsonl')):
  for line in p.read_text().splitlines():
   r=json.loads(line);receipts[r['url']]=r
 out=[]
 for q in queue['candidates']:
  cards=q['directory_observations'];names=[r['name'] for r in cards];a=next((accepted[r['candidate_id']] for r in cards if r['candidate_id'] in accepted),None);status='pending-independent-company-domain';note='NSF award facts are discovery evidence; an independently explicit company domain and current operations/location remain unreviewed.';company=None
  if a:status='accepted-new-company';company=a['company_id'];note='Explicit MIT TLO plus company review accepted identity, sector and company-stated local place. No founding, ownership, staffing or live-vacancy inference. NSF UEI association remains a discovery suggestion, not independently verified.'
  elif any(n in existing for n in names):status='confirmed-existing-company';company=next(existing[n] for n in names if n in existing);note='Named TLO explicit domain and official website agree with existing canonical domain; stable company ID retained, no duplicate created.'
  elif q.get('policy_holds'):status='held-source-policy';note='; '.join(p['decision'] for p in q['policy_holds'])
  elif q['name_collision'] or q['shared_domain_candidates']:status='pending-identity-collision';note='Distinct UEIs or shared domains remain separate; no name-only merge.'
  elif q['existing_company_suggestions']:status='pending-existing-identity';note='Name-only match to an existing company is a suggestion, not identity confirmation.'
  elif cards and not q['website_candidates']:status='held-missing-official-link';note='Named MIT profile has no unique usable explicit external company link or could not be fetched. No URL guessed.'
  elif q['website_candidates']:
   rs=[receipts.get(w['url'],{}) for w in q['website_candidates']];failed=next((r for r in rs if r.get('status')=='blocked-or-failed'),None)
   if failed:status='held-fetch-failure';note=failed.get('reason','Fetch failed')+'; no retry or alternate-access bypass.'
   else:status='pending-company-corroboration';note=next((NOTES[n] for n in names if n in NOTES),'Official site still requires reviewed identity, sector, current city and careers evidence.')
  evidence=[]
  for w in q['website_candidates']:
   r=receipts.get(w['url'])
   if r:evidence.append({k:r[k] for k in ['url','final_url','checked_on','status','sha256','reason'] if k in r})
  out.append(dict(candidate_id=q['candidate_id'],names=q['names'],status=status,company_id=company,note=note,checked_on='2026-11-01',homepage_review_receipts=evidence))
 summary=dict(total_groups=len(out),status_counts=dict(collections.Counter(r['status'] for r in out)),new_verified_companies=sum(r['status']=='accepted-new-company' for r in out),existing_identities_confirmed=sum(r['status']=='confirmed-existing-company' for r in out),unresolved_groups=sum(r['company_id'] is None for r in out),limitations='Queue-wide status accounting is not full verification of every group. Most NSF-only groups still need independent official-domain discovery; no inaccessible or uncertain entity is promoted.')
 data=dict(summary=summary,reviews=out);(root/'data/reviews/phase14-candidate-status.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(summary,indent=2));return data
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('site',type=Path);build(p.parse_args().site)
