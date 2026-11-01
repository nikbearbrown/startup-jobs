# Structured discovery, separate from verified companies

This pass builds a reproducible review queue, not a new verified-company batch. Accepted coverage remains 135 companies, 88 hiring routes and five scoped company size observations. No new companies, hiring routes, headcounts or map locations were accepted in this pass. Raw source HTML and API responses remain local and ignored; public factual observations retain URLs, check dates and response hashes.

| Source | Scope and actual result | Review boundary |
|---|---|---|
| NSF documented Awards API | Massachusetts, award dates from 2023, separate SBIR and STTR keyword queries; 122 + 17 results, 135 unique awards | 133 title-qualified awards, 113 UEI groups; two incidental keyword matches excluded |
| MIT Technology Licensing Office | All four explicit showcase pages, 20 + 20 + 20 + 2 cards | 62 candidates, 54 explicit external company links, eight unresolved profile links |
| Combined queue | 170 groups after five unique exact-name suggestions across sources | Candidate-only; no automatic verification or verified-export writes |
| SBIR official bulk CSV | Advertised no-abstract CSV | Robots returned HTTP 403; no CSV downloaded |
| NSF Seed Fund history / company data | Public navigation inspected | History JSON robots-disallowed; proprietary PitchBook data not fetched |
| MassCEC | Public portfolio navigation and policy inspected | Automated gathering prohibited; collection stopped |

The two NSF keyword scopes are complete for the observed API totals. They are not all Massachusetts companies, all NSF funding or all SBIR agencies. Awardee cities and active-award flags describe the award, not current operations or office occupancy. No grant-to-staff conversion is made. NSF `orgUrl` is a directorate link, never a company website. Public exports exclude PI names, email, phone, address and abstracts.

MIT listing years are retained as directory years, not founding years. Institutional profile links have an explicit `link_kind`; only external card links or a single named profile's “Visit Website” field become website candidates. MIT affiliation does not establish Boston presence. Some links redirect to renamed or acquired brands; those need lifecycle and identity review, not silent replacement with an acquirer.

The queue retains two distinct Rstream UEIs despite normalized-name collision. Eleven groups suggest comparison against existing accepted companies, 106 need an independently explicit company-domain source, two require name-collision review, seven are held under reviewed source policy, and 44 remain in the official-site identity/sector/city/careers review lane. These are work queues, not 170 additional employers. Broad domain matching does not automatically merge or accept entities.

## Replay and review

1. `python3 scripts/collect-nsf-awards.py` uses the documented public API with robots checks, 25-result pages, cache hashes, bounded responses and fail-closed pagination. Cached failed outcomes are not retried. Preserve complete receipts before refreshing a source snapshot.
2. The jobs-site collector acquires explicit permitted MIT page/profile manifests. `python3 scripts/discover-tlo.py ../jobs-site` freezes card pagination; `python3 scripts/resolve-tlo-links.py ../jobs-site` follows only explicit company fields from the cache.
3. `python3 scripts/build-discovery-queue.py` rebuilds the review queue offline. It does not touch verified exports. Source-policy holds take precedence over further review.
4. Review current official company identity, sector, city and explicit careers links against the independent directory source. Distinguish a researcher profile, institutional unit, company, acquisition and parent board. Promote only explicit reviewed decisions into `data/sources/`; then rebuild accepted exports normally.
5. Run `python3 tests/test-discovery.py`, `python3 scripts/build.py` and `python3 tests/test-build.py`.

Six new offline tests cover query completeness and field allowlisting, institutional versus company links, ambiguous UEI names, policy holds, denied domains before network access, and verified-export immutability. The existing eleven source/export tests also pass.

Practical limits: the 54 company destinations and 35 explicit policy-navigation URLs have fetch receipts in jobs-site, but fetched pages are not verified identities. Failed robots, missing operative terms, changed brands and incomplete current city evidence remain held. Nona, Glyphic and Syntis explicitly prohibit extraction; Ground Truth Ag also prohibits automated/equivalent manual extraction; Vertical's reuse language, DMAT's inaccessible linked policy and Sesame's homepage in place of operative terms require clarification. No restricted source is bypassed.
