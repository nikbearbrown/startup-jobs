# startup-jobs

A growing, evidence-backed directory of startups and other companies with relevant ecosystem affiliations, beginning in greater Boston. Built on the [Research Jobs](https://github.com/nikbearbrown/research-jobs) model for the [Humanitarians AI startup and research map](https://jobs.humanitarians.ai/ecosystem).

The aim is broad discovery across regions and industries. **This is not a census or a complete list of Boston startups.** Names, websites, industries and city locations are useful without street addresses. Inclusion does not imply a current job opening, active business status, or sponsorship.

## Coverage — 2026-10-31

117 company records: **116 identity/site/sector reviews and one unresolved launch record**. The MassRobotics batch adds 78 reviewed identities from 97 candidates. The Engine Ventures review plus the phase6 follow-up adds 31 independently corroborated identities with qualified Boston-region evidence; other portfolio candidates remain separate. Investor membership never establishes a local office.

All 117 have source website references. The jobs-site review retrieved 113 of those sites; the remaining four retain prior source evidence. **76 companies have reviewed hiring navigation**, stored with source, date, scope and destination-check status in `data/enrichment/hiring-routes.json` and included in JSON/CSV exports. There are **zero verified live-vacancy counts**. A careers page is not a promise of hiring.

Forty-one companies have reviewed map locations in the jobs-site overlay, up from 16. The 29-company Engine batch contributes 18 mapped contact addresses. Other records retain qualified city-level evidence or unresolved relocation status; legal correspondence and future job locations are not current precise offices. The three earlier company geocode cases are resolved with municipal address data. Sixty MassRobotics records still retain resident affiliation only, without precise markers. This repository's location export remains city-level; precise decisions and evidence live in the [map evidence](https://github.com/nikbearbrown/jobs.humanitarians.ai/blob/feat/startup-research-map/docs/ecosystem-phase4-expansion.md). Boston Metal and Foundation Alloy have unresolved current cities. Pison's officially linked hiring board still returns 404; no official alternative was found.

The collection is selection-biased and does not establish current operations, founding age, ownership, hiring or total ecosystem coverage. MassRobotics descriptions may be member-supplied; cross-publisher corroboration is not an independent operational audit. Names/domains are deduplicated, and unknown fields stay null.

**Access update:** New YC automated collection is held because its legal terms prohibit scraping. New MassBio publication is held under its reuse terms; Greentown reuse conditions remain unresolved. No newly collected data from these three sources is in this expansion. The earlier YC discovery/launch evidence remains historical; it is not permission to resume scraping. See [source policy](data/source-policy.json).

The sixth batch adds Axoft (advertised Cambridge work region) and EVOLOH (Lowell manufacturing center), both with official hiring navigation. Neither has a verified street location or size observation. Lowell remains searchable without a fabricated city marker. DBOS, Formlabs and Biobot collection is now held under explicit extraction restrictions; VulcanForms reuse needs clarification. No new records from those held sources were published. See [the batch report](https://github.com/nikbearbrown/jobs.humanitarians.ai/blob/feat/startup-research-map/docs/ecosystem-phase6-expansion.md).

The seventh batch adds company-linked hiring routes for Cellino (LinkedIn destination not fetched) and Tatum Robotics (team inquiries including interns/volunteers), leaving 42 companies without a route. It adds one approximate Cellino company-team band, 11–50 from 37 named team cards, excluding board and investors. Five existing/new company-scoped observations are now mirrored in `data/enrichment/headcounts.json` and exported with ranges, reported/estimated status, scope, source, date and uncertainty. This is not local payroll or a vacancy total. Transcend Mechanics automated access is held under its terms; LabyrinthAI deeper collection is held because its policy page returned 500.

The eighth batch resolves MagLev Aero’s official SmartRecruiters route through visible browser navigation, leaving 41 company hiring-route gaps. The November 1 UTC review date is preserved; evidence-date validation now uses UTC to avoid rejecting valid observations around local midnight. No company identity or size estimate was added. Boston Dynamics and Lightmatter collection is held under explicit extraction restrictions; Liquid AI directory reuse needs clarification under its website-linked terms. See the [eighth batch report](https://github.com/nikbearbrown/jobs.humanitarians.ai/blob/feat/startup-research-map/docs/ecosystem-phase8-expansion.md).

The ninth batch adds QuEra Computing with official company and independently published Harvard identity/domain/industry evidence, its official careers route and a separately reviewed approximate Boston contact-address marker. Founding age, ownership, workforce and current vacancies remain unknown. The total is 117 companies with 76 hiring routes and 41 remaining route gaps. Themis AI and Pickle Robot remain held under their extraction terms; no company record from either is accepted. See the [ninth batch report](https://github.com/nikbearbrown/jobs.humanitarians.ai/blob/feat/startup-research-map/docs/ecosystem-phase9-expansion.md).

## Repository model

| Path | Purpose |
| --- | --- |
| `data/targets.csv` | Prioritized source collection scopes, status and remaining work |
| `data/discovery/` | Unverified company-profile queues; discovery is not acceptance |
| `data/sources/*.json` | Reviewed records with per-field source observations and dates |
| `data/companies.json`, `data/companies.csv` | Deterministic merged exports; do not edit |
| `data/coverage.json` | Generated counts and coverage limitations |
| `data/raw/fetch-receipts.jsonl` | Public fetch outcomes and hashes; full cached HTML stays ignored |
| `scripts/seed.py` | Reproduces the manual launch batch from documented observations; do not rerun over enriched records |
| `scripts/fetch.py` | Optional identified, robots-aware, rate-limited public-page collector |
| `scripts/discover.py` | Historical YC extractor; held under current access policy |
| `scripts/import-massrobotics-review.py` | Offline assembly from explicit review decisions and cached company evidence in the jobs-site checkout |
| `scripts/build.py` | Validation, duplicate rejection, JSON/CSV exports, coverage |
| `tests/test-build.py` | Source integrity, URL, precision and identity tests |

## Add companies

1. Read `AGENTS.md` and `CONVENTIONS.md`. Pick a target and establish its access/reuse conditions.
2. Discover candidate profile links, using a permitted public page or a manual review. Keep raw results separate from accepted companies.
3. Visit the company website and an independent publisher (accelerator, public agency, investor, university, or other source). Verify name, canonical domain, industry and place separately. Save URLs, dates, supported fields and short observations. Retain disagreements and nulls.
4. Add or enrich the company in a source JSON file. Use the launch file as the concrete schema example. Normalize the domain and reconcile duplicate identities before publishing.
5. Run the build and tests. Update target status and the coverage paragraph. Publish sources and generated exports together.

```sh
python3 scripts/build.py
python3 tests/test-build.py
# Optional permitted public-page collection; inspect terms first:
python3 scripts/fetch.py https://www.massrobotics.org/startups/massrobotics-resident-startups/
```

The fetcher fails closed when robots cannot be established (except an explicit 404), checks redirects, and records blocks. A blocked page remains a blocked target. It never rotates identities or circumvents restrictions. The extractor only queues links; it does not scrape hidden APIs or assert current company details.

## Scale and maintenance

Work source-by-source and region-by-region; avoid paying for a directory merely to discover names. Expand beyond accelerator-funded companies with university spinouts, incubators, public grant recipients and regional company sources. Keep source scopes and enumeration limits explicit. After resolving identities, enrich missing cities and industries before optional addresses. Recheck aging evidence and suspected closures; retain historical observations instead of erasing them. Shared company domains and renamed companies need human reconciliation. There is no automatic recurring crawl enabled in this repository.

The site imports a pinned research Git commit and a SHA-256 of the startup export through `scripts/import-ecosystem.py` in the jobs site repository. Review and rebuild the static snapshot when data changes; publishing this repository alone does not refresh the site.

Facts and source links are supplied for research. Source pages and third-party content remain with their owners; no license to republish their text is implied. This repository does not change those source terms.

## Reproduce the additional review

`python3 scripts/import-engine-review.py ../jobs-site` imports only the 29 explicit decisions in `data/engine-ventures-review.tsv`, using cached company and investor evidence. `python3 scripts/import-hiring-review.py ../jobs-site/public/ecosystem/directory.json` copies the reviewed company hiring routes. Run `python3 scripts/build.py` and `python3 tests/test-build.py` afterward. Raw HTML stays local; public receipts retain URLs, dates, hashes and failed/blocked outcomes. The separate Engine resident adapter is held pending its operative terms; it is not the source of this investor batch.
