"""Join permitted bulk discovery facts conservatively; never writes verified exports.
UEI groups awards. Exact normalized names suggest links only, and collisions are held.
Institutional directory URLs are not company domains. No funding-to-headcount inference.
"""
import collections,hashlib,json,re,unicodedata
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data/discovery'
def name_key(s):
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower();words=re.findall(r'[a-z0-9]+',s)
 while words and words[-1] in ('inc','incorporated','llc','corp','corporation','co','company','ltd','limited'):words.pop()
 return ' '.join(words)
def domain(u):
 p=urlsplit(u)
 if p.scheme not in ('http','https') or not p.hostname or p.username or p.password:return None
 return p.hostname.lower().removeprefix('www.')
def build(root=ROOT):
 D=root/'data/discovery'
 nsf=json.loads((D/'nsf-ma-2023-awards.json').read_text());tlo=json.loads((D/'mit-tlo.json').read_text());existing=json.loads((root/'data/companies.json').read_text());groups=collections.defaultdict(list);excluded=[]
 for a in nsf['awards']:
  if a['awardeeStateCode']!='MA' or not re.match(r'^(?:SBIR|STTR)\b',a['title']):excluded.append(dict(award_id=a['id'],name=a['awardeeName'],reason='Query mention is not a title-qualified Massachusetts SBIR/STTR award'));continue
  if not re.fullmatch(r'[A-Z0-9]{12}',a['ueiNumber'] or ''):excluded.append(dict(award_id=a['id'],reason='Missing/malformed UEI; do not guess company grouping'));continue
  groups[a['ueiNumber']].append(a)
 names=collections.defaultdict(set)
 for u,rs in groups.items():
  for a in rs:names[name_key(a['awardeeName'])].add(u)
 existing_names=collections.defaultdict(list)
 for r in existing:existing_names[name_key(r['name'])].append(r['id'])
 resolved=json.loads((D/'mit-tlo-resolved-links.json').read_text()) if (D/'mit-tlo-resolved-links.json').exists() else []
 websites={r['candidate_id']:r for r in resolved};candidates={};matches=[]
 for u,rs in sorted(groups.items()):
  rs.sort(key=lambda x:(x['date'],x['id']));aliases=sorted({r['awardeeName'] for r in rs});keys={name_key(n) for n in aliases};collision=any(len(names[k])>1 for k in keys)
  candidates['nsf-uei-'+u]=dict(candidate_id='nsf-uei-'+u,uei=u,names=aliases,website_candidates=[],directory_observations=[],award_observations=rs,existing_company_suggestions=sorted({eid for k in keys for eid in existing_names.get(k,[])}),identity_status='candidate-only',name_collision=collision,geography='Massachusetts awardee city only; current Boston-region presence requires review',size_status='unknown; award value is not workforce')
 for q in tlo['candidates']:
  key=name_key(q['name']);possible=names.get(key,set());cid='nsf-uei-'+next(iter(possible)) if len(possible)==1 else q['candidate_id']
  r=candidates.setdefault(cid,dict(candidate_id=cid,uei=None,names=[q['name']],website_candidates=[],directory_observations=[],award_observations=[],existing_company_suggestions=existing_names.get(key,[]),identity_status='candidate-only',name_collision=len(possible)>1,geography='MIT affiliation only; Boston-region presence requires review',size_status='unknown'))
  if q['name'] not in r['names']:r['names'].append(q['name'])
  r['directory_observations'].append(q)
  if cid!=q['candidate_id']:matches.append(dict(candidate_id=cid,tlo_candidate_id=q['candidate_id'],method='Unique exact normalized legal-name agreement; suggestion only, not identity acceptance'))
  w=websites.get(q['candidate_id'])
  if w:r['website_candidates'].extend(w['website_candidates'])
  elif domain(q['linked_url'])!='tlo.mit.edu':r['website_candidates'].append(dict(url=q['linked_url'],source_url=q['source_url'],source_sha256=q['source_sha256'],checked_on=q['checked_on'],method='Explicit named official TLO card external link; company identity unverified'))
 policies=json.loads((root/'data/source-policy.json').read_text()) if (root/'data/source-policy.json').exists() else []
 holds={h:p for p in policies if p['status']=='held' for h in p.get('applies_to_domains',[domain(p['url'])])}
 domains=collections.defaultdict(set)
 for r in candidates.values():
  r['website_candidates']=list({x['url']:x for x in r['website_candidates']}.values())
  for w in r['website_candidates']:domains[domain(w['url'])].add(r['candidate_id'])
 for r in candidates.values():
  r['shared_domain_candidates']=sorted({cid for w in r['website_candidates'] for cid in domains[domain(w['url'])] if cid!=r['candidate_id']})
  r['policy_holds']=[holds[domain(w['url'])] for w in r['website_candidates'] if domain(w['url']) in holds]
  r['next_review']='held-source-policy' if r['policy_holds'] else 'resolve-name/domain-collision' if r['name_collision'] or r['shared_domain_candidates'] else 'compare-existing-record' if r['existing_company_suggestions'] else 'review-official-site-policy-identity-sector-city-careers' if r['website_candidates'] else 'find-independent-explicit-company-domain'
 out=sorted(candidates.values(),key=lambda r:(r['next_review'],r['names'][0].lower()))
 summary=dict(nsf_query_scopes=nsf['scope_results'],nsf_unique_awards=len(nsf['awards']),nsf_title_qualified_awards=sum(len(x) for x in groups.values()),nsf_company_uei_groups=len(groups),excluded_query_matches=len(excluded),tlo_cards=len(tlo['candidates']),tlo_pages=len(tlo['pages']),exact_name_cross_source_suggestions=len(matches),candidate_groups=len(out),with_website_candidate=sum(bool(r['website_candidates']) for r in out),with_existing_record_suggestion=sum(bool(r['existing_company_suggestions']) for r in out),name_collision_groups=sum(r['name_collision'] for r in out),shared_domain_groups=sum(bool(r['shared_domain_candidates']) for r in out),review_queue=dict(collections.Counter(r['next_review'] for r in out)),policy_held_groups=sum(bool(r['policy_holds']) for r in out),automatically_accepted=0,limitations='Discovery groups are not verified companies or a startup census. Exact name/domain matches are review suggestions only. NSF orgUrl is not a company website; grant cities and MIT affiliation do not establish current offices. No private contact data or PitchBook data retained.')
 (D/'company-review-queue.json').write_text(json.dumps(dict(summary=summary,candidates=out,excluded=excluded,join_suggestions=matches),indent=2)+'\n');print(json.dumps(summary,indent=2));return dict(summary=summary,candidates=out,excluded=excluded,join_suggestions=matches)
if __name__=='__main__':build()
