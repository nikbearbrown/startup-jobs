import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('tlo_review',ROOT/'scripts/import-tlo-review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
@unittest.skipUnless((ROOT.parent/'jobs-site/cache/expansion').exists(),'Source replay requires local ignored evidence cache; published source checks run in test-build.py')
class TLOReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rows=json.loads((ROOT/'data/reviews/phase14-company-decisions.json').read_text());cls.review=m.Review(ROOT.parent/'jobs-site')
 def test_only_reviewed_companies_pass_evidence_replay(self):
  for r in self.rows:
   company,route=self.review.company(r);self.assertIsNone(company['founded_on']);self.assertIsNone(company['ownership']);self.assertIsNone(company['locations'][0]['coordinates']);self.assertNotIn('headcount',company)
  self.assertEqual(len(self.rows),16)
 def test_reject_candidate_unknown_domain_and_unsubstantiated_city(self):
  for change in [dict(decision='candidate'),dict(homepage_requested='https://example.com/'),dict(city='San Diego'),dict(city='Cambridge'),dict(city_text='Unsubstantiated location')]:
   with self.assertRaises(ValueError):self.review.company(dict(self.rows[0],**change))
 def test_reject_invented_careers_url(self):
  r=copy.deepcopy(self.rows[0]);r['careers_url']='https://example.com/jobs'
  with self.assertRaises(ValueError):self.review.company(r)
 def test_metro_and_hiring_caveats_survive(self):
  v=next(r for r in self.rows if r['name']=='VectorWave');r,_=self.review.company(v)
  self.assertEqual(r['locations'][0]['place_scope'],'metropolitan-area');self.assertEqual(r['locations'][0]['city'],'Greater Boston')
  with self.assertRaises(ValueError):self.review.company(dict(v,city_scope='municipality'))
  for name,word in [('SanaHeal','template'),('Cambridge Terahertz','future')]:
   _,route=self.review.company(next(r for r in self.rows if r['name']==name));self.assertIn(word,route['display_note'])
 def test_existing_kano_identity_not_duplicated_and_crabi_history_retained(self):
  rows=json.loads((ROOT/'data/companies.json').read_text());self.assertEqual([r['id'] for r in rows if 'kanotherapeutics.com' in r['website']],['kano'])
  crabi=next(r for r in rows if r['id']=='crabi-robotics');self.assertEqual(crabi['locations'][0]['city'],'Medford');self.assertEqual(crabi['location_history'][0]['city'],'Boston')
if __name__=='__main__':unittest.main()
