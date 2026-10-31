"""Extract YC company-profile links from an already permitted cached HTML page.
python3 scripts/discover.py cache/<hash>.html
Discovery is a queue, NOT a verified company record. No network requests.
"""
import csv,datetime,html.parser,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Links(html.parser.HTMLParser):
 def __init__(self):super().__init__();self.urls=set()
 def handle_starttag(self,tag,attrs):
  href=dict(attrs).get('href','')
  if tag=='a' and re.fullmatch(r'/companies/[a-z0-9-]+',href) and href not in ('/companies/industry','/companies/location'):
   self.urls.add('https://www.ycombinator.com'+href)
p=Links();p.feed(Path(sys.argv[1]).read_text())
path=ROOT/'data/discovery/yc-boston.csv';path.parent.mkdir(exist_ok=True)
existing={r['profile_url']:r for r in csv.DictReader(path.open())} if path.exists() else {}
for url in p.urls:existing.setdefault(url,dict(profile_url=url,discovered_on=datetime.date.today().isoformat(),status='todo',notes='Discovery only. Confirm name, current company website, sector and city with independent sources.'))
with path.open('w') as f:
 w=csv.DictWriter(f,fieldnames=['profile_url','discovered_on','status','notes']);w.writeheader();w.writerows(existing[k] for k in sorted(existing))
print(f'{len(p.urls)} links found; {len(existing)} queued. This does not establish Boston presence.')
