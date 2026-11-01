"""Offline regression tests for candidate-only joins and provenance boundaries."""
import contextlib,hashlib,importlib.util,io,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
q=module('queue','build-discovery-queue.py');a=module('awards','collect-nsf-awards.py');f=module('fetch','fetch.py')
class DiscoveryTests(unittest.TestCase):
 def test_complete_documented_source_scopes(self):
  data=json.loads((ROOT/'data/discovery/nsf-ma-2023-awards.json').read_text())
  self.assertEqual([(r['status'],r['reported_total'],r['retrieved_unique']) for r in data['scope_results']],[('complete',122,122),('complete',17,17)])
  self.assertEqual(len({r['id'] for r in data['awards']}),135)
  for r in data['awards']:
   self.assertEqual(set(r),set(a.FIELDS)|{'source_url','source_sha256','checked_on','query'})
   self.assertNotIn('orgUrl',r);self.assertNotIn('piEmail',r);self.assertRegex(r['source_sha256'],r'^[a-f0-9]{64}$')
 def test_internal_profiles_are_not_company_websites(self):
  tlo=json.loads((ROOT/'data/discovery/mit-tlo.json').read_text());rows=json.loads((ROOT/'data/discovery/mit-tlo-resolved-links.json').read_text())
  self.assertEqual([p['cards'] for p in tlo['pages']],[20,20,20,2])
  self.assertEqual(sum(bool(r['website_candidates']) for r in rows),54)
  for r in tlo['candidates']:
   self.assertNotIn('website',r);self.assertNotIn('founded_year',r)
   self.assertEqual(r['link_kind']=='institutional-profile',q.domain(r['linked_url'])=='tlo.mit.edu')
  for r in rows:
   for w in r['website_candidates']:self.assertNotEqual(q.domain(w['url']),'tlo.mit.edu')
 def test_ambiguous_names_never_merge_different_ueis(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);p=root/'data/discovery';p.mkdir(parents=True)
   awards=[dict(id=str(i),awardeeStateCode='MA',title='SBIR Phase I',ueiNumber=u,awardeeName=n,date='2025-01-01') for i,(u,n) in enumerate([('AAAAAAAAAAAA','Example Inc.'),('BBBBBBBBBBBB','Example LLC')])]
   (p/'nsf-ma-2023-awards.json').write_text(json.dumps(dict(awards=awards,scope_results=[])))
   card=dict(candidate_id='tlo-example',name='Example',linked_url='https://tlo.mit.edu/startups/example')
   (p/'mit-tlo.json').write_text(json.dumps(dict(candidates=[card],pages=[])));(root/'data/companies.json').write_text('[]')
   (p/'mit-tlo-resolved-links.json').write_text('[]')
   with contextlib.redirect_stdout(io.StringIO()):out=q.build(root)
   self.assertEqual(len(out['candidates']),3);self.assertEqual(out['join_suggestions'],[])
   self.assertTrue(all(r['name_collision'] for r in out['candidates']))
   self.assertTrue(all(r['identity_status']=='candidate-only' for r in out['candidates']))
 def test_real_collision_and_policy_holds_remain_in_queue(self):
  data=json.loads((ROOT/'data/discovery/company-review-queue.json').read_text())
  self.assertEqual(len(data['candidates']),170);self.assertEqual(data['summary']['automatically_accepted'],0)
  kano=next(r for r in data['candidates'] if 'Kano Therapeutics' in r['names']);self.assertIn('kano',kano['existing_company_suggestions'])
  rstream=[r for r in data['candidates'] if r['name_collision']];self.assertEqual(len(rstream),2);self.assertEqual(len({r['uei'] for r in rstream}),2)
  for r in data['candidates']:
   self.assertEqual(r['identity_status'],'candidate-only')
   self.assertNotIn('coordinates',r);self.assertNotIn('headcount',r)
   if r['policy_holds']:self.assertEqual(r['next_review'],'held-source-policy')
 def test_known_restrictions_stop_before_network(self):
  for host in ['masscec.com','nona-technologies.com','glyphic.bio','syntis.bio','verticalsemi.com','groundtruth.ag']:
   with self.assertRaises(ValueError):f.check_url('https://'+host+'/')
 def test_queue_rebuild_does_not_modify_verified_exports(self):
  paths=[ROOT/'data/companies.json',ROOT/'data/companies.csv',ROOT/'data/coverage.json']
  before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
  with contextlib.redirect_stdout(io.StringIO()):q.build()
  self.assertEqual(before,[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])
if __name__=='__main__':unittest.main()
