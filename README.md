# startup-jobs

A growing, evidence-backed directory of startups and other companies with relevant ecosystem affiliations, beginning in greater Boston. Built on the [Research Jobs](https://github.com/nikbearbrown/research-jobs) model for the [Humanitarians AI startup and research map](https://jobs.humanitarians.ai/ecosystem).

The aim is broad discovery across regions and industries. **This is not a census or a complete list of Boston startups.** Names, websites, industries and city locations are useful without street addresses. Inclusion does not imply a current job opening, active business status, or sponsorship.

## Coverage — 2026-10-31

85 company records: **84 identity/site/sector reviews and one unresolved launch record**. This expansion adds 78 reviewed identities from 97 MassRobotics directory candidates; 19 remain pending. The reviewed batch includes 35 career-navigation links, not verified open jobs.

Eighteen new companies state local addresses; the jobs-site evidence overlay maps 15 of them with approximate Census geocodes and holds three ambiguous/unmatched addresses. Sixty new records retain only a directory-reported resident affiliation: Boston is not a verified office or headquarters for those records, and they have no precise map pin. This repository's location export remains city-level; precise location decisions live in the [jobs-site expansion evidence](https://github.com/nikbearbrown/jobs.humanitarians.ai/blob/feat/startup-research-map/docs/ecosystem-expansion.md). Across both batches, 84 records have some city/affiliation evidence and Boston Metal remains unresolved.

The collection is selection-biased and does not establish current operations, founding age, ownership, hiring or total ecosystem coverage. MassRobotics descriptions may be member-supplied; cross-publisher corroboration is not an independent operational audit. Names/domains are deduplicated, and unknown fields stay null.

**Access update:** New YC automated collection is held because its legal terms prohibit scraping. New MassBio publication is held under its reuse terms; Greentown reuse conditions remain unresolved. No newly collected data from these three sources is in this expansion. The earlier YC discovery/launch evidence remains historical; it is not permission to resume scraping. See [source policy](data/source-policy.json).

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
