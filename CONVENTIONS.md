# Conventions

- Use lower kebab-case file names and stable company IDs. Match Research Jobs: source files are edited; merged exports are generated.
- One file per collection source/batch in `data/sources/`. `companies` entries carry their own evidence so merged sources do not erase provenance.
- Record facts only. Unknowns are `null` or an empty collection; do not invent headquarters, funding, operating status, hiring, or addresses.
- `reviewed` means company identity, website and industry have company + independent-publisher evidence. It does **not** verify every field, current job openings, or independent editorial quality. A portfolio directory can repeat company-supplied information; record that limitation.
- Each evidence item includes URL, publisher, checked date, fields supported, and a short observation in your own words. `public-page-review` launch evidence was inspected through web search/open, not through the local fetcher. Search crawl dates can lag the current page; evidence is not a guarantee of freshness.
- City evidence has its own status: company-stated, directory-reported, or corroborated-directories. Preserve disagreements in notes. A Boston regional directory does not prove Boston city limits. Prefer a more specific company statement and retain the broader source label.
- A company can have several locations. An office is not necessarily headquarters. This initial sample records only the reviewed Boston-area presence.
- City precision has no organization coordinates or street address. Street precision requires explicit address AND coordinate evidence. Missing or conflicted locations remain unlocated.
- Canonical website host (lowercase, leading www removed) catches duplicates. Merge manually, retaining evidence and aliases; shared-host edge cases require a documented identity decision, never silent merging.
- `needs-review` retains contradictory or incomplete candidates. Never convert `todo` to `done` just because a page was fetched. `done` means the defined source scope has been enumerated and reviewed; `partial` records remaining work.
- Collection scope includes startups and private growth companies. Do not silently mix listed, acquired or closed organizations into an active-startup total; retain lifecycle evidence when found. This launch sample makes no active-status assertion.
- Automated collection is opt-in. Inspect source terms, honor robots.txt and rate limits, use the identifying client, stop on access restrictions. No bypasses, login scraping, or republishing full page/article text. Raw HTML is local and ignored; receipts store hashes/outcomes.
- Rebuild and run tests before publishing. Source evidence, not generated output, is the review boundary.
