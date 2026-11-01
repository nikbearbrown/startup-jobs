# Phase15: official websites and hiring routes from the NSF candidate queue

Seven company identities are accepted after current company-page review and independent domain/technology corroboration. All seven have explicit official hiring navigation; four have separately reviewed approximate contact-location map markers. No staffing, founding-year, ownership or active-vacancy counts were added.

| Company | Company-stated place | Corroboration | Hiring route / map scope |
|---|---|---|---|
| Adden Energy | Waltham | Harvard OTD named domain and battery licensing article | Company careers; approximate contact address |
| MacroCycle Technologies | Cambridge | MIT Orbit named domain and polymer technology | Linked Polymer board; approximate contact address |
| Robigo | Cambridge | MIT News named domain and engineered crop-protection microbes | Careers says Coming soon; approximate contact address |
| Pearl Bio | Cambridge | Khosla Ventures named domain and biotechnology profile | Company careers; approximate contact address |
| Quantivly | Somerville | Official legal page UEI exactly matches NSF award 2304514 and technology | Engineering expressions of interest; postal head office kept city-only |
| Mantel | Cambridge | Engine Ventures named domain and carbon-capture profile | Official embedded Polymer board identifies Cambridge recruiting; no office pin |
| Dynocardia | Newton | Luminate accelerator domain and medical-device profile | Official careers states Newton; historical Cambridge origin preserved in qualification; no office pin |

[Acceptance decisions](../data/reviews/phase15-company-decisions.json) carry source URLs and short reviewed text anchors. The [accepted source](../data/sources/nsf-candidates-phase15-reviewed.json) carries publisher, date, hashes, supported fields and uncertainty. Institutional/investor pages may repeat company-provided information; they are not independent occupancy audits. Quantivly uses an exact company-published UEI, not a name-only guess. Other NSF group-to-company associations remain name/technology discovery matches; this does not establish independently verified ownership of those UEIs.

This batch reviews 15 previously unresolved groups: seven accepted, six pending further corroboration, and two held by policy. The [complete ledger](../data/reviews/phase15-candidate-status.json) preserves all 170 groups: 23 accepted additions across phases14–15 plus four confirmed existing companies; **143 unresolved**. These are 83 needing independent domain discovery, 26 requiring company/place/identity corroboration, eight existing-identity suggestions, two UEI collisions, eight missing links, nine policy holds and seven earlier fetch failures. The other 135 groups were carried forward without a claim of new review.

Allium, Wild Microbes and Fluent Metal official pages lack sufficient current local place evidence in this review. RevivBio and XL Batteries have company-stated locations and useful pages but still need independent domain-owner corroboration. Labby's retrieved homepage, contact and careers pages contain template bodies and placeholder address/phone fields; none are imported. A company-stated Harvard spotlight is not accepted as independent corroboration until the report itself is reviewed.

Lydian terms prohibit manual/automated extraction; collection stopped after reading them, and the domain is now denied by both collectors. Fourth Power terms limit use to internal business/personal purposes; directory reuse is held pending clarification, with no accepted data. Bayer returned robots HTTP403; no retry or bypass occurred. Robigo was independently corroborated using an unrelated, permitted MIT News article. OneCyte's terms lookup timed out and no company-page collection or acceptance followed. Prior source restrictions remain intact. Full page HTML stays in ignored local cache; only factual observations, decisions and public fetch receipts are published.

## Counts and reproducibility

Startup Jobs now has **158 companies: 157 reviewed identities and one earlier unresolved record**, 158 website references (154 retrieved by the site workflow), 105 reviewed hiring routes, 53 route gaps, and 63 reviewed map contact locations. Seven additions all have routes, so the 53 existing route gaps are unchanged. Company locations still awaiting review: 95. Research website coverage is unchanged at 5,077/5,629 (552 gaps).

The integrated map has 6,179 entities and 987 reviewed location records at 153 unique coordinate pairs: 500 MIT buildings, 295 municipal address points, 192 approximate Census matches. Default >10 plus unknown matches 5,920 entities and maps 976 (932 unknown-size), leaving 4,944 awaiting location review. All-size location gaps: 5,192. The four new mapped companies share three contact addresses; only one coordinate pair is new to the existing map. These are street-range interpolations, not surveyed entrances or rooms. Quantivly's explicitly postal head-office address is deliberately not promoted to a physical office marker.

Replay: `python3 scripts/import-company-review.py ../jobs-site`, build reviewed locations and import the site, synchronize hiring using `scripts/import-hiring-review.py`, rebuild exports, then reimport the site. `scripts/summarize-candidate-reviews.py` validates acceptance against the reviewed export and preserves the prior immutable ledger. No successful fetch or name match alone can promote a company. Tests reject wrong UEIs, unrelated government awards, unrelated recruiting boards, missing domain corroboration, fabricated careers links and held cached pages.

**171 tests pass**: 86 site TypeScript, 56 site Python, 11 startup exports, six discovery, five earlier source replay and seven new review/ledger tests. The Next.js build passes. Ten cached-source replay tests (five prior and five new) require ignored local caches and explicitly skip without them; all ten ran locally. The two new portable ledger tests run without caches. No production merge or promotion.
