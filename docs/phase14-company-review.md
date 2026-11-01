# Company review from the structured MIT/NSF queue

Sixteen new companies pass explicit company-plus-MIT Technology Licensing Office identity, website and broad-sector review. Each has company-stated Boston-region presence: fifteen have a municipality, and VectorWave states only Greater Boston. Ten have reviewed official recruiting routes. These additions bring the directory to **151 companies and 98 hiring routes**; six newly accepted companies lack a reviewed hiring route, so total route gaps grow from 47 to 53. No existing missing route is claimed resolved by this batch.

| Company | Officially stated place | Recruiting route |
|---|---|---|
| Active Surfaces | Woburn | Official careers page |
| AeroShield | Waltham | Company-linked JobScore board |
| Cambridge Terahertz | Cambridge | Official careers page; asks visitors to check back |
| Cartesian Systems | Cambridge | Careers page describes Kendall Square in-person team |
| Cellarray | Lexington | Not established |
| Electrified Thermal Solutions | Charlestown, Boston | Company-linked Lever board; also includes European roles |
| Elementium Materials | Woburn | No dedicated reviewed route accepted |
| G5 Labs | Boston | Homepage careers section; Boston/Silicon Valley/hybrid |
| IDX20 | Brookline | Not established |
| InnDura Therapeutics | Cambridge | Not established |
| Magnendo | Newton | Official on-site Newton recruiting page |
| Neurobionics | Cambridge | Not established |
| SanaHeal | Somerville | Official careers page; template job entries remain qualified |
| Skyline Therapeutics | Cambridge | Company-wide Join Us page; not exclusively US opportunities |
| VectorWave | Greater Boston, municipality unresolved | Official on-site Greater Boston recruiting page |
| Window Therapeutics | Boston | Not established |

The map separately accepts six company contact addresses: Active Surfaces, Elementium, InnDura, SanaHeal, Skyline and Window Therapeutics. Each reviewed street/city input matches a cached Census response. These are **approximate street-range coordinates**, not surveyed entrances, rooms or laboratory footprints. The source locations are company-stated contact sites and are not independent occupancy audits. The startup export remains city-level; exact-address decisions live in jobs-site. Company map coverage rises from 53 to 59.

Kano Therapeutics is the existing `kano` record, identified by its explicit domain. The source builder rejected an attempted duplicate before any new merged export was written. Its stable ID and earlier evidence remain intact. The discovery matcher now includes exact canonical-domain suggestions as well as exact names, without automatically merging or accepting either. CRABI retains its identity but its current company-stated place becomes Medford; the previous Boston resident-affiliation observation remains in `location_history` and original source evidence.

## All 170 groups remain accounted for

The [review ledger](../data/reviews/phase14-candidate-status.json) contains 16 newly accepted company groups, four confirmed existing company identities and 150 unresolved groups:

- 98 need an independently explicit company domain.
- Eight name-only suggestions need existing-identity verification; two distinct-UEI collisions remain separate.
- Eight MIT profiles lack a usable unique external company link; seven website fetches failed or were blocked; seven groups are held by reviewed source policy.
- Twenty have company/lifecycle/place evidence still requiring corroboration.

This is queue-wide accounting, not a claim that every NSF-only company has received a full website review. The original NSF UEI joins remain name-based discovery suggestions even when a TLO/company identity is accepted; no independently verified UEI ownership is asserted.

Examples of deliberate holds: Avanti's old domain is for sale; Ikigai and Sync redirect to acquisition/acquirer pages; Found Energy now appears as a division under Found Industries; Xibus announces a merger. Cache DNA states a San Carlos headquarters; VasoRX gives a San Diego private mailbox; Perceptra lists San Francisco and Eindhoven roles; Arculus lists Alexandria, Virginia. Those facts do not prove the absence of Boston operations, but they do not establish one. TI Solutions' Boston references identify academic advisers, not company offices. MIT institutional footers are never substituted for a startup address.

Nocturnal's existing compressed response was decoded offline with a size bound and source hash, not refetched. It names Kendall Square and a 2027 launch, but technical and present business evidence remains insufficient. Restrictions on SBIR bulk CSV, NSF Seed Fund static history/PitchBook, MassCEC and company domains remain unchanged. Failed pages are not retried through alternate access.

## Reproduce and validate

`data/reviews/phase14-company-decisions.json` is the explicit acceptance boundary. `python3 scripts/import-tlo-review.py ../jobs-site` validates source hashes, unique named TLO links, original/final domains, reviewed text anchors, geography scope and explicit careers navigation against the local evidence cache. It writes a reviewed source batch and qualified hiring observations. No founding date, ownership or headcount is derived from MIT years, awards, reputation or incomplete team rosters.

Run the jobs-site location merge/import, then `python3 scripts/import-hiring-review.py ../jobs-site/public/ecosystem/directory.json`, `python3 scripts/build.py`, and repeat the site import to synchronize its startup hash. `scripts/review-candidate-status.py ../jobs-site` rebuilds the status ledger offline from explicit decisions and public receipts.

Tests: existing 11 source/export tests, six discovery-boundary tests and five source-replay tests. Source-replay tests require the local ignored jobs-site evidence cache and explicitly skip on clean checkouts without it. All five ran in this batch. The site adds regression checks for metro-only places, unknown workforce, approximate contact locations, hiring caveats, preserved Kano identity and CRABI's city change. Live vacancy counts and new size estimates remain zero.
