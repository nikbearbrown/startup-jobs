import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def module(name,file):
 s=importlib.util.spec_from_file_location(name,R/'scripts'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('company_review','import-company-review.py');status=module('candidate_status','summarize-candidate-reviews.py')
@unittest.skipUnless((R.parent/'jobs-site/cache/expansion').exists() and (R/'cache/nsf').exists(),'Source replay requires ignored local evidence caches')
class ReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.decisions=json.loads((R/'data/reviews/phase15-company-decisions.json').read_text());cls.review=m.Review(R.parent/'jobs-site')
 def test_seven_sources_replay_without_invented_counts(self):
  results=[self.review.company(d) for d in self.decisions]
  self.assertEqual(len(results),7);self.assertEqual(sum(bool(r[2]) for r in results),4)
  for r,route,address in results:self.assertIsNone(r['ownership']);self.assertIsNone(r['founded_on']);self.assertNotIn('headcount',r);self.assertTrue(route['display_note'])
 def test_wrong_uei_and_unrelated_award_fail(self):
  q=next(d for d in self.decisions if d['company_id']=='quantivly')
  for change in [dict(uei='WRONG'),dict(award_id='0000000'),dict(identity_source='https://www.pearlbio.com/')]:
   with self.assertRaises(ValueError):self.review.company(dict(q,**change))
 def test_city_cannot_come_from_unrelated_board(self):
  q=next(d for d in self.decisions if d['company_id']=='mantel')
  with self.assertRaises(ValueError):self.review.company(dict(q,embedded_board='macrocycle-technologies'))
 def test_missing_independent_domain_or_unobserved_route_fail(self):
  q=self.decisions[0]
  for change in [dict(independent_url='https://engineventures.com/companies/mantel'),dict(careers_url='https://example.com/jobs'),dict(city_text='Unverified office')]:
   with self.assertRaises(ValueError):self.review.company(dict(q,**change))
 def test_new_policy_holds_reject_cached_pages(self):
  for url in ['https://www.lydianlabs.com/careers','https://gofourth.com/careers/']:
   with self.assertRaises(ValueError):self.review.page(url)
class LedgerTests(unittest.TestCase):
 def test_ledger_preserves_all_groups_and_unresolved_entries(self):
  a=json.loads((R/'data/reviews/phase14-candidate-status.json').read_text());b=json.loads((R/'data/reviews/phase15-candidate-status.json').read_text());self.assertEqual({r['candidate_id'] for r in a['reviews']},{r['candidate_id'] for r in b['reviews']});self.assertEqual(b['summary']['unresolved_groups'],143);self.assertEqual(b['summary']['phase15_reviewed_groups'],15)
  self.assertEqual(sum(not r.get('company_id') for r in b['reviews']),143)
 def test_ledger_rejects_unbacked_acceptance(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'data/reviews').mkdir(parents=True)
   for name in ['phase14-candidate-status.json','phase15-candidate-decisions.json']:(p/'data/reviews'/name).write_text((R/'data/reviews'/name).read_text())
   (p/'data/companies.json').write_text('[]')
   with self.assertRaises(ValueError):status.build(p)
if __name__=='__main__':unittest.main()
