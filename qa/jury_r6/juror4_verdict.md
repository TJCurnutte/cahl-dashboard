# JURY R6 — 4/5 (INTERACTION LENS) — v59, Chrome-free

Method: byte-audit of deployed `app.js?v=59` (151,365B) + `style.css?v=59` (85,364B) + index.html,
fetched 2026-09-04 ~12:35 ET. Version triad in sync: JS_VERSION 59 (app.js:10) = APP_VERSION 59
(index:131) = asset `?v=59`. No browser automation, no git (owner constraints); ~20 greps, 8 section
dumps, 5 timed API single-shots, WCAG contrast math in Python. Timings: /api/version 0.25s,
/api/today/scores 0.24s, /api/teams 0.37s, **/api/players 23.4s (worst measurement across all rounds
— R4 10.3s, R5 19.2s, now 23.4s, and the cron-warm window evidently missed it)**.

## Headline: v59 self-recursion fix VERIFIED

app.js:2460-2464 ships `window.loadTeamContent = loadTeamContent;` — direct function binding, no
wrapper arrow, plus a comment documenting the no-IIFE shadowing trap. Team tab is alive again for
saved-team users (fix confirmed in deployed bytes, matching the jsdom repro claim).

## Standing-defect ledger (R5 → v59 re-verification)

| Carry | v59 status |
|---|---|
| api() no timeout/AbortController | **FIXED** — app.js:850-885: 30s AbortController ceiling, retry-once on network/5xx (700ms backoff), honest copy on abort ("This took too long — tap Refresh"), cache only on res.ok, clearTimeout in finally |
| live-pill hidden checkbox, zero :checked feedback | **FIXED** — style.css:245-246: `.live-pill:has(#autoToggle:checked)` lifts color/border + dot flips to var(--win); "click to toggle" title now honest |
| League/Players/Analytics sub-skeletons watchdog-less | **PARTIAL** — generic api() 30s ceiling now guarantees every sub-skeleton resolves to data or an error card (the infinite-hang class is dead); but per-tab 8s/20s nudges (team-only, app.js:1912-1923) never spread, so League/Players/Analytics sit on a bare skeleton up to 30s with no "still loading" acknowledgment |
| window.loadTeamContent self-recursion (dead Team tab) | **FIXED** — app.js:2460-2464, direct binding |
| count-ups unguarded behind prefers-reduced-motion | **STILL OPEN** — animateNumbers (app.js:772-787) drives JS rAF with no matchMedia gate; the CSS reduced-motion blocks (1193, 1277, 1383) kill every CSS animation but cannot stop JS-driven ones |
| dataStamp = page-load time not data age | unchanged (app.js:2823 — `new Date()` at render, minor) |
| button:hover #3a8fe0 off-token | unchanged (style.css:511, minor) |

## Dimension table

| # | Dimension | Evidence (one line) | Score |
|---|-----------|--------------------|-------|
| 1 | Visual identity | Rink-lines watermark + LIVE breathe bar + hockey grammar intact; v57 tonight-KPI strip adds a broadcast-style front door (27px Saira numerals, red live tile) — strongest identity round since v49 | 8.7 |
| 2 | Typographic system | Saira 600/700/800 + JetBrains Mono in href; tonight-num is display+tabular-nums; kpi-num in the mono/tlation cluster; count-up easing math is sound; remaining mono scale stragglers (8.5px tonight-label floor) | 8.7 |
| 3 | Color system | Dark --accent #e8253c = 4.47:1 on #070b12 and **3.96:1 on --panel #0e1420** — sub-AA on the v57 red KPI tile + all small red labels; #ef3d54 = 5.13:1 at near-identical hue is the one-token fix; hover #3a8fe0 off-token | 8.4 |
| 4 | Layout & hierarchy | v59 kills the last full-tab dead state (Team); render-token guard, hashchange re-entrancy guard, boot-hash-before-setTab ordering all verified; sub-skeleton ack gap (30s bare skeleton worst-case) is the remaining layout defect | 8.6 |
| 5 | Density & data presentation | data-sort/data-rt headers (app.js:573/653) + keyboard Enter/Space activation incl. th[data-sort] (L2532-2539); tnum/zebra/sticky from R1-F held; partial-index retry ladder (state.playersRetries ≤4 @8s) is new resilience; no column-jiggle found | 8.4 |
| 6 | Interaction & micro-feedback | THE round for this lens: api() 30s ceiling + retry-once, :has(:checked) pill state, btn-press pointerdown/up, pull-to-refresh with opacity-feedback hint, 180ms debounce + taClearStale, toast feedback; every finding this round was a resolution — residual: skeletons give zero progress acknowledgment between 0-30s on 3 tabs | 8.9 |
| 7 | Motion design | CSS reduced-motion coverage broad (3 blocks + transitions clamp); animateNumbers still runs rAF with no gate — the exact carry, third round; heat bars snap instantly under RM (L2430 comment, good) | 8.5 |
| 8 | Depth & material | Watermark whisper opacities, hairlines, flat panels untouched; tonight-kpi gradient is panel-2→panel (tint-based, in-system) | 8.6 |
| 9 | Consistency & component quality | autoToggle finally inside the component system (:has feedback); focus-visible on brand/buttons/pills/nav/typeahead (7 rules); palette input 16px + focus reset kept; typeahead combobox aria-expanded wired; hover off-token and dataStamp semantics remain the outliers | 8.6 |
| 10 | Mobile ergonomics | ≤430px 44px floors verified on kpalBtn/live-pill/themeToggle/refreshBtn (padding-only squeeze); pal-input 16px (iOS zoom fixed); ptr hint non-interactive + pointer-events:none; residual = cell-network 23s players wait with no ack until abort copy | 8.8 |

**WEIGHTED TOTAL: 8.6/10** (8.62 exact; lineage 8.1 → 8.4 → 8.5 → **8.6**)

## 3 cheapest fixes toward 9.7-per-dimension

1. **Gate count-ups behind `matchMedia('(prefers-reduced-motion: reduce)')`** — 3 lines at the top of
   `animateNumbers` (app.js:772): `const rm = matchMedia('(prefers-reduced-motion: reduce)').matches;
   if (rm) return;` (or set final text and return). Third round carrying this; it is the single
   remaining motion defect. **delta ≈ +0.8 motion (8.5→9.3), +0.1 total.**
2. **One dark-theme accent token: `--accent: #ef3d54`** (5.13:1 on bg, ~4.5:1 on panel at identical
   hue) — fixes sub-AA red on the v57 KPI tile, status chips, and small red labels in one line;
   style.css:36. **delta ≈ +0.8 color (8.4→9.2), +0.08 total.**
3. **Skeleton progress acknowledgment on League/Players/Analytics** — reuse the existing team-tab
   pattern (app.js:1912-1923): an 8s "Still loading…" swap inside each sub-load. With api()'s 30s
   ceiling in place this is now a 6-line copy change per tab, not a watchdog system. **delta ≈ +0.5
   interaction (8.9→9.4), +0.13 total (lifts layout +0.2, mobile +0.2 as well).**

Projected combined: ~8.8/10. The gate demands ≥9.7 per dimension; the three fixes above clear
motion and color toward it, but identity/type/density sit at 8.4-8.7 with no single cheap lever —
that gap is design work (signature data-viz depth, broadcast identity surface), not bug fixes.

## Score honesty check

- 9+ means no defect findable at effort: ~20 greps + 8 section dumps + 5 timed API calls + contrast
  math found 1 open systemic carry (count-ups), 1 sub-AA token, 1 ack gap, 2 minors — no dimension
  reaches 9.
- Scores move only where v57/v58/v59 bytes moved vs my R5 table: interaction +0.7 (api ceiling, pill
  state, btn-press/ptr polish), mobile +0.7 (44px floors held + pal 16px + ptr), layout/identity/
  consistency +0.1 each (v57 KPI strip, autoToggle in-system, Team-tab revival); color −0.2 (new
  concrete 3.96:1 panel measurement against v57's red tile); others held.
- v59's flagship fix verified byte-exact at app.js:2460-2464; /api/players 23.4s measured — worse
  than every prior round, cron warm evidently missing the players index this cycle.

VERDICT: 8.6/10
