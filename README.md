# startup-jobs

A growing, evidence-backed directory of startups and private growth companies, beginning in greater Boston. Built on the [Research Jobs](https://github.com/nikbearbrown/research-jobs) model for the [Humanitarians AI startup and research map](https://jobs.humanitarians.ai/ecosystem).

The aim is broad discovery across regions and industries. **This is not a census or a complete list of Boston startups.** Names, websites, industries and city locations are useful without street addresses. Inclusion does not imply a current job opening, active business status, or sponsorship.

## Coverage — 2026-10-31

50 company-profile links discovered from the permitted public YC Boston HTML (a partial page, not full enumeration), with 5 already reviewed and 45 awaiting review.

7 initial company records; 6 cross-source identity/website/industry reviews; 6 city-level locations; 0 verified street locations; 1 unresolved location held off the map (Boston Metal). Boston Metal's official location pages conflict with a facility-closure report; evidence and the unresolved decision are retained. Research data is imported separately from Research Jobs, never counted as startups.

The launch sample intentionally spans biotech, AI, robotics, energy storage and metals. It is small and selection-biased; no total ecosystem coverage percentage is justified. Some city labels come from directories, not company statements. See each record and `data/coverage.json`.

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
| `scripts/discover.py` | YC profile-link extractor from permitted local HTML |
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
python3 scripts/fetch.py https://www.ycombinator.com/companies/location/boston
# Then pass the printed cache_path to scripts/discover.py.
```

The fetcher fails closed when robots cannot be established (except an explicit 404), checks redirects, and records blocks. A blocked page remains a blocked target. It never rotates identities or circumvents restrictions. The extractor only queues links; it does not scrape hidden APIs or assert current company details.

## Scale and maintenance

Work source-by-source and region-by-region; avoid paying for a directory merely to discover names. Expand beyond accelerator-funded companies with university spinouts, incubators, public grant recipients and regional company sources. Keep source scopes and enumeration limits explicit. After resolving identities, enrich missing cities and industries before optional addresses. Recheck aging evidence and suspected closures; retain historical observations instead of erasing them. Shared company domains and renamed companies need human reconciliation. There is no automatic recurring crawl enabled in this repository.

The site imports a pinned research Git commit and a SHA-256 of the startup export through `scripts/import-ecosystem.py` in the jobs site repository. Review and rebuild the static snapshot when data changes; publishing this repository alone does not refresh the site.

Facts and source links are supplied for research. Source pages and third-party content remain with their owners; no license to republish their text is implied. This repository does not change those source terms.
