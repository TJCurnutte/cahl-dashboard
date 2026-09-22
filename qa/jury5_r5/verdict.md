# Jury R5 — Juror 5/5 — PRODUCT CREDIBILITY lens (v55, deployed bytes)

Method (Chrome-free, per constraint): fetched deployed `app.js?v=55` (145,172 B), `style.css?v=55` (82,825 B), `index.html`, plus live API calls `/api/version` → `{"js":55}` (confirms v55 is live), `/api/today`, `/api/today/scores`, `/api/teams` (85 KB), `/api/league/<Sunday B East id>`, `/api/players` (19.2s, 2.9 MB), `/api/players/lookup?q=ackley` (0.27s). All claims below are byte-verified against the deployed assets — no source-tree assumptions.

## R5 defect ledger — claimed dead in v55 — verification results (9/9 confirmed dead)

| # | Old defect | Verification | Status |
|---|---|---|---|
| 1 | Literal `\u2026` escape in "match…" | `grep -c '\\u2026'` = 0 double-backslash occurrences; all 12 `u2026` are single-escape (render as `…`); "No teams match…" at app.js:685 is a correct render | DEAD |
| 2 | TONIGHT'S PACEMAKERS | app.js:595 ships `LEAGUE LEADERS`; zero "PACEMAKERS" in deployed bytes | DEAD |
| 3 | Em-dashes in copy | 38 em-dashes in app.js; every one is a code comment except 3 legitimate prose hints (picker/typeahead copy). CSS has 33, all in comments/content rules | DEAD |
| 4 | "MATCH" as score header | zero `>MATCH<`/"MATCH" literals; cols-head ships `Time Home Match Away Rink` — "Match" is the middle-column label (5-col grid, correct position, not the score header) | DEAD (replaced) |
| 5 | verBadge element+JS+CSS | 0 hits for `verBadge` in app.js, style.css, index.html; version now lives in `/api/version` self-heal + `dataStamp` | DEAD |
| 6 | 'vs @' dangle | both next_game render sites guarded: hero (app.js:1246–1253: `opp`/`fac` empty-checks suppress separators and 'vs/@') and team page (app.js:1918–1921: ternary drops the vs span). 0 `vs @` in bytes or API payloads | DEAD |
| 7 | 'Tonight' palette group | kpal groups are only `Players/Teams/Pages` (app.js:2876); zero 'Tonight' group | DEAD |
| 8 | dead .switch CSS | 0 `.switch` rules in style.css | DEAD |
| 9 | UPDATED HH:MM stamp | index.html:105 `DATA · CHILLERSTATS.COM · UPDATED <span id="dataStamp">` + app.js:2710 sets `hour12:false` 24h HH:MM; no "tonight"/AM-PM | DEAD |
| 10 | Bye Week + Team Blue/Red in /api/today | live call: 2 real games (Brewskies–Trash Pandas, Whalers–Stepbros); 0 occurrences of `Bye`/`Team Blue`/`Team Red`/`vs @` in today, scores, teams, and league payloads; league standings (6 rows, Fall 2026) also clean; app.js:2266 additionally filters `/^bye\s*week$/i` at render | DEAD |

## NEW scorecard (v55)

| Dimension | Evidence (one line) | Score |
|---|---|---|
| 1. Visual identity | CBJ palette locked end-to-end (Union Blue/Goal Red/Silver tokens; light-theme variants all on-hue); Saira Condensed display numerals + JetBrains Mono labels on every surface incl. cols-head and pal-grp | 9.0 |
| 2. Typographic system | tnum block (style.css:134–138) covers tables/scores/hero/palette; Saira 600/700/800 all loaded in fonts href (faux-bold era over); mono consolidated at tokens — but 2 raw `JetBrains Mono` declarations and `.tl-game.otl{font-size:8px}` residue survive | 9.0 |
| 3. Color system | win/loss/tie state colors are deliberate semantic set; BUT `button:hover{background:#3a8fe0}` (style.css:508) is an off-token generic blue on the primary control — the one visible palette leak | 8.0 |
| 4. Layout & hierarchy | Live Now scoreboard → hero card → Finals → Upcoming ordering; empty states all designed ("No games posted yet.", gd-empty, "Loading the full leaderboard… with hint that PTS/G is ready"); hash deep-links + palette Pages nav | 8.5 |
| 5. Density & data presentation | sticky theads, zebra rows, sortable th, tap-friendly 44px floors in ≤430 block; scrimmage rows muted non-clickable at source; heat/gd viz have separate value cells (name-fusion class of bugs dead) | 8.5 |
| 6. Interaction & micro-feedback | typeahead has debounce+stale-clear+retry rows; team/players/lookup all have abort+timeout; BUT live-pill autoToggle still has zero checked-state feedback (no `input:checked`/`:has` CSS, no body class — v55 ships the R4 defect verbatim), and generic `api()` (app.js:824) still has no timeout → League/Team/Players/Analytics can skeleton forever | 7.5 |
| 7. Motion design | has-live pulse, entrance fades, reduced-motion respected (4 blocks); live-badge tint swap; nothing decorative found | 8.5 |
| 8. Depth & material | solid panels (backdrop-filter era over), hairline borders, watermark at opacity ≤0.06; consistent surface stack in both themes | 8.5 |
| 9. Consistency & component quality | 25 inline `onclick=` handlers coexist with delegated systems (nav, palette, league picker) — two interaction idioms; ~6 inline `style="margin-top:18px"` h3s bypass tokens; button hover off-token | 7.8 |
| 10. Mobile ergonomics | ≤479 today-rows stack to 4-area grid cards; header squeeze is padding-only with 44px floors (R4 regression fixed, verified in bytes); tap-highlight handled; nav min 44×56 | 8.6 |

## WEIGHTED TOTAL

identity 1.08 + type 1.08 + color 0.80 + layout 1.02 + density 1.02 + interaction 0.75 + motion 0.68 + depth 0.68 + consistency 0.624 + mobile 0.688 = **8.4/10**

## 3 cheapest fixes that raise the score most

1. **autoToggle on-state feedback** — one CSS rule using existing markup: `.live-pill:has(input:checked) .live-pill-dot{background:var(--accent); animation:pulse…}` + label swap in the existing `change` listener (state.auto already tracked, app.js:2686). Kills the only "clicked it, nothing happened" control in the product. Δ ≈ +0.15 (interaction 7.5→8.8).
2. **Token the button hover** — replace `button:hover{background:#3a8fe0}` with a Union Blue mix token (e.g. `color-mix(in srgb, var(--union) 82%, white)`), and sweep the ~6 inline `style=` h3 margins into one `.section-h` class. Δ ≈ +0.18 (color 8.0→9.0, consistency 7.8→8.4).
3. **Give `api()` the 25s abort+timeout the other fetches already have** (copy the `loadAllTeams` pattern onto app.js:824) + render a one-line error card on catch. Removes the infinite-skeleton hang class from 4 of 5 tabs. Δ ≈ +0.15 (interaction, layout).

Combined ceiling with these three: ≈ 8.9 — the remaining gap to 9.7 is live-data seasoning (all-zero Fall 2026 season renders leaders with value 0, which no amount of CSS can hide from a credibility lens).

## Residual credibility risks (static verification limits)

- `/api/players` measured 19.2s single-shot — the client aborts at 20s and shows "Player index timed out". Cron warm evidently didn't cover this hit; a fresh visitor's first leaderboard search is a coin flip between 19s wait and timeout message.
- `dataStamp` is the page-load time, not the data's actual update time — if the backend cache is stale, the stamp still claims "UPDATED <now>". Minor semantic fib a data-journalism reader could catch.
- Live detection remains a client-side time heuristic (today-only guard verified); a postponed game in the ≤100min window could show LIVE (static analysis; needs live data to confirm).
- (static) — all findings are from deployed bytes + API responses; no visual/rendering verification was possible under the no-Chrome constraint.

VERDICT: 8.4/10
