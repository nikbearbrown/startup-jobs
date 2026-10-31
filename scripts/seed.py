"""Reproduce the manually reviewed launch records from the cited public pages.
Evidence notes are short paraphrases, not full copied page text. No network requests.
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-10-31'
def evidence(url, publisher, fields, note, primary=False):
    return dict(url=url, publisher=publisher, fields=fields.split(','), checked_on=DATE, note=note, primary=primary, method='public-page-review')
def company(id, name, website, city, industries, summary, evidence, notes='', review='reviewed', city_status='company-stated'):
    return dict(id=id,name=name,website=website,industries=industries,summary=summary,locations=[dict(city=city,region='MA',country='US',precision='city',address=None,coordinates=None,verification=city_status)] if city else [],careers_url=None,operating_status=None,stage=None,checked_on=DATE,review_status=review,evidence=evidence,notes=notes)
yc='https://www.ycombinator.com/companies/location/boston'
rows=[
company('volta-labs','Volta Labs','https://www.voltalabs.com/','Boston',['Biotechnology','Lab automation'],'Develops automated sample preparation systems for genomics.',[
evidence(yc,'Y Combinator','name,website,industries,city','Lists Volta Labs as an active Boston genomics company.'),
evidence('https://www.voltalabs.com/about-us','Volta Labs','name,website,industries,city','Describes genomics automation and lists its Boston office.',True)]),
company('nabla-bio','Nabla Bio','https://www.nabla.bio/','Cambridge',['Biotechnology','Artificial intelligence'],'Combines AI and experimental testing to design protein medicines.',[
evidence('https://www.ycombinator.com/companies/nabla-bio','Y Combinator','name,website,industries','Lists an active antibody-design company under Boston.'),
evidence('https://www.nabla.bio/','Nabla Bio','name,website,industries,city','Describes drug design; states the team is based in Cambridge, MA.',True)],'YC uses Boston; the company explicitly identifies Cambridge. Company city takes precedence.'),
company('postera','PostEra','https://postera.ai/','Boston',['Biotechnology','Artificial intelligence'],'Uses machine learning for medicinal chemistry and drug discovery.',[
evidence('https://www.ycombinator.com/companies/postera/jobs','Y Combinator','name,website,industries,city','Lists PostEra in Boston with a medicinal chemistry focus.'),
evidence('https://postera.ai/','PostEra','name,website,industries','Describes its AI platform for medicinal chemistry.',True)],'Boston is directory-reported; the company homepage reviewed did not establish an office city.',city_status='directory-reported'),
company('kernal-biologics','Kernal Biologics','https://www.kernalbio.com/','Cambridge',['Biotechnology','RNA therapeutics'],'Develops targeted mRNA delivery and selective cell therapies.',[
evidence('https://www.kernalbio.com/','Kernal Biologics','name,website,industries','Describes targeted mRNA therapeutics and selective translation.',True),
evidence('https://jobs.massdigitalhealth.org/companies/kernal-biologics','Mass Digital Health','name,website,industries,city','Lists Cambridge and biotechnology/therapeutics.'),
evidence('https://www.builtinboston.com/company/kernal-biologics-inc','Built In Boston','name,industries,city','Lists Cambridge headquarters and biotech.')], 'Cambridge is corroborated by two directories; no street location verified.',city_status='corroborated-directories'),
company('boost-robotics','Boost Robotics','https://www.boostrobotics.ai/','Boston',['Robotics','Artificial intelligence'],'Builds autonomous robots for data-center inspection and maintenance.',[
evidence(yc,'Y Combinator','name,website,industries,city','Lists Boost Robotics in Boston and describes data-center robotics.'),
evidence('https://www.boostrobotics.ai/','Boost Robotics','name,website,industries','Describes autonomous inspection and maintenance robots.',True),
evidence('https://jobs.aihub.masstech.org/companies/boost-robotics','MA AI Hub','name,website,industries,city','Lists both Boston and San Francisco.')], 'Boston presence is directory-reported; MA AI Hub also lists San Francisco. Headquarters not established.',city_status='corroborated-directories'),
company('form-energy','Form Energy','https://formenergy.com/','Somerville',['Energy storage','Climate technology'],'Develops iron-air batteries for multi-day grid energy storage.',[
evidence('https://formenergy.com/contact/','Form Energy','name,website,industries,city','Lists Somerville alongside Weirton and Berkeley and describes iron-air storage.',True),
evidence('https://arpa-e.energy.gov/programs-and-initiatives/search-all-projects/regenerative-metal-fuels-energy-transmission-without-wires','ARPA-E','name,website,industries,city','Lists Form Energy in Somerville for an active energy storage project.')], 'Somerville is one company office, not the sole operating location. Includes a later-stage private company.'),
company('boston-metal','Boston Metal','https://www.bostonmetal.com/',None,['Metals manufacturing','Climate technology'],'Develops molten oxide electrolysis for metals production.',[
evidence('https://www.bostonmetal.com/contact-us/','Boston Metal','name,website,city','Contact page lists Woburn.',True),
evidence('https://www.bostonmetal.com/news/boston-metal-scaling-the-future-of-critical-metals/','Boston Metal','name,industries,city','June 2026 company update describes critical metals focus and Woburn headquarters.',True),
evidence('https://www.boston.com/news/business/2026/02/24/layoffs-hit-boston-metal-as-company-plans-woburn-shutdown/','Boston.com','name,city,operating_status','February 2026 report describes planned Woburn facility closures.')], 'Location held out of map pending review: official pages list Woburn, but a February 2026 closure report conflicts. Later company update does not explicitly resolve which facilities remain open.',review='needs-review')
]
(ROOT/'data/sources/boston-launch.json').write_text(json.dumps(dict(id='boston-launch',checked_on=DATE,scope='Boston area launch sample; selected manually across sectors, not exhaustive',companies=rows),indent=2)+'\n')
