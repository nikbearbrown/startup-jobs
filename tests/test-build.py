import copy,datetime,importlib.util,json,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
spec=importlib.util.spec_from_file_location('build',Path(__file__).resolve().parents[1]/'scripts/build.py'); b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
class BuildTests(unittest.TestCase):
 def setUp(self): self.row=json.loads((b.ROOT/'data/sources/boston-launch.json').read_text())['companies'][0]
 def test_evidence_date_uses_utc_at_local_midnight_boundary(self):
  class PreviousLocalDay(datetime.date):
   @classmethod
   def today(cls):return cls(2026,10,31)
  class UTCNow(datetime.datetime):
   @classmethod
   def now(cls,tz=None):return cls(2026,11,1,1,0,tzinfo=tz)
  with patch.object(b.datetime,'date',PreviousLocalDay),patch.object(b.datetime,'datetime',UTCNow):
   b.date('2026-11-01')
   with self.assertRaises(ValueError):b.date('2026-11-02')
 def test_sources_validate(self):
  for p in (b.ROOT/'data/sources').glob('*.json'):
   for row in json.loads(p.read_text())['companies']: b.validate(row)
 def test_no_single_source_verified(self):
  self.row['evidence']=self.row['evidence'][:1]
  with self.assertRaises(ValueError): b.validate(self.row)
 def test_no_false_street_precision(self):
  self.row['locations'][0]['coordinates']=[-71,42]
  with self.assertRaises(ValueError): b.validate(self.row)
 def test_unsafe_url(self):
  self.row['website']='javascript:alert(1)'
  with self.assertRaises(ValueError): b.validate(self.row)
 def test_identity_canonicalization(self): self.assertEqual(b.domain('https://www.Example.com/path/'),'example.com')
 def test_duplicate_domain_fails(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'data/sources').mkdir(parents=True)
   other=copy.deepcopy(self.row);other['id']='other-company'
   (root/'data/sources/test.json').write_text(json.dumps(dict(checked_on='2026-10-31',companies=[self.row,other])))
   with self.assertRaises(ValueError): b.build(root)
 def test_hiring_routes_do_not_claim_live_vacancies(self):
  rows=json.loads((b.ROOT/'data/companies.json').read_text())
  self.assertEqual(sum(bool(r.get('hiring_routes')) for r in rows),98)
  for r in rows:
   for q in r.get('hiring_routes',[]):
    self.assertEqual(q['scope'],'company');self.assertEqual(q['vacancy_status'],'not-verified');b.domain(q['source_url']);b.date(q['checked_on'])
 def test_unknown_hiring_entity_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'data/sources').mkdir(parents=True);(root/'data/enrichment').mkdir()
   (root/'data/sources/test.json').write_text(json.dumps(dict(checked_on='2026-10-31',companies=[self.row])))
   (root/'data/enrichment/hiring-routes.json').write_text(json.dumps([dict(company_id='unknown-company',routes=[])]))
   with self.assertRaises(ValueError):b.build(root)
 def test_scoped_size_estimate_is_not_local_payroll(self):
  rows=json.loads((b.ROOT/'data/companies.json').read_text());r=next(r for r in rows if r['id']=='cellino');q=r['headcount']
  b.validate_headcount(q);self.assertEqual(q['kind'],'estimated');self.assertEqual((q['minimum'],q['maximum']),(11,50));self.assertIn('not a complete workforce census',q['scope'])
  self.assertEqual(q['observed_roster_entries'],37)
 def test_headcount_rejects_invalid_bounds_and_lab_scope(self):
  q=json.loads((b.ROOT/'data/enrichment/headcounts.json').read_text())[0]['observation']
  for change in [dict(minimum=0),dict(minimum=100,maximum=50),dict(minimum=True),dict(scope_type='lab'),dict(uncertainty='')]:
   with self.assertRaises(ValueError):b.validate_headcount(dict(q,**change))
if __name__=='__main__':unittest.main()
