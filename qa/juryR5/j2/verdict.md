# Jury R5 — Juror 2/5 — MOBILE lens (390×844) — v55

Chrome-free per owner rule. Evidence = deployed bytes fetched 2026-09-03
(`style.css?v=55` 82,825B / `app.js?v=55` 145,172B / index 8,484B; byte-identical
diff vs sibling copies `../v55_css.css|v55_js.js|v55_index.html`), urllib API
probes, and computed WCAG math. Mobile lens: every finding evaluated at ≤430px.

## R4 defect re-verification (my 8.6-round hard failure)

**FIXED — verified in deployed bytes.** `@media (max-width:430px)` (css:1863)
now squeezes visually only: `#themeToggle/#refreshBtn { min-height:44px;
min-width:44px; padding:0 10px }`, `#kpalBtn/.live-pill { min-height:44px }`,
`#kpalBtn kbd display:none`, comment "hit areas stay >=44px (a11y floor)".
Global `-webkit-tap-highlight-color: transparent` on a/.nav-link/.link/
.typeahead-item/.pal-item (css:1885) + `:active` states (opacity .7, css:1887),
`button:active scale(0.97)` (css:509). Zero `min-height/min-width: 0` inside any
`@media(max-width)` tap-target rule — the R2/R4 regression class is closed at
source. Cron warm also verified: `.github/scripts/refresh_cache.py` + workflow
`*/30 * * * *`, hourly baseline warms `/api/players?full=1` (420s headroom) and
`/api/teams`; live burst today 0.3–1.5s.

## 10-dimension scores

| # | Dimension | Evidence (mobile lens) | Score |
|---|---|---|---|
| 1 | Visual identity | Rink-lines watermark + CBJ hues + Saira Condensed/JetBrains hold at 390px (watermark shrinks to 130px <480, brand 19px, status-bar meta + theme-color sync per theme); withheld 1.0 — watermark is hero-card-only, the Today sb-card strip carries no signature asset | 9.0 |
| 2 | Typographic system | Saira 800 genuinely loaded (wght@600;700;800), tabular-nums at `table` level kills column jiggle, display sizes step down cleanly (sb-num 34, t-home/away 17); defect: mono scale STILL append-only round 3 — `--mono-md` dead (0 uses), xs/sm only 5 selectors migrated, ~60 hardcoded px sizes remain (9.5×16, 10×15, 11×15…) | 8.3 |
| 3 | Color system | Goal Red = live/interactive discipline verified (live rows `--accent-dim`, score-flash, ppg tick, pos-chips CBJ-coded); dark muted 5.97–6.39:1, light muted 4.77:1, both pass AA; hairline defect: dark `--accent` text 4.47:1 on bg — 0.03 under 4.5 for 10.5px mono labels (.pacemakers-label) | 8.9 |
| 4 | Layout & hierarchy | <479 today rows re-grid into designed cards (time/board/home/away/rink areas); cols-head hidden <900 ("hidden beats smashed"); header wraps <700 with max-width guards; main clears nav 72px + safe-area; cost of the 44px floor: controls wrap to 2nd row → ~100–110px header cluster before content at 390 | 8.8 |
| 5 | Density & data presentation | Touch block: sticky first column, th/td min-width 44 (132 first col), 14px pads, zebra both themes (color-mix), "swipe ›" pill + self-hiding right-edge fade (background-attachment local/scroll trick); th.num right-aligned; no crushed columns at 390 | 8.7 |
| 6 | Interaction & micro-feedback | :active everywhere (new), tap-highlight parity, 48px touch pads, kbd hidden on coarse pointers, typeahead stale-aborts + 180ms debounce; **carried defect: generic `api()` (app.js:824) still has NO timeout/AbortController — cell-network hang = infinite skeleton on League/Players/Analytics** (only team 22s/typeahead 40s protected); /api/players/lookup 6.4s cold for a 3-char query | 8.2 |
| 7 | Motion design | Inventory small and purposeful: live-dot pulse, score-flash 0.9s, heat-bar 0.7s, pal-pop; 4 prefers-reduced-motion blocks; sb-card hover disabled on touch; static watermark | 8.9 |
| 8 | Depth & material | Luminance stack bg/panel/panel-2/panel-3/inset/bg-raise, hairline border-soft, token shadows; grepped blur inventory: exactly 1 backdrop-filter (palette overlay); no fake shadows found | 9.0 |
| 9 | Consistency & component quality | One scorecell anatomy (sb-side/sb-num) reused, chips/pills from one mono system, zebra unified; carried defects: hidden `#autoToggle` checkbox still functional with zero checked-state feedback (no `input:checked` CSS anywhere; title says "click to toggle"), mono scale append-only (see dim 2) | 8.4 |
| 10 | Mobile ergonomics | 44px floor verified at source: nav links 44×56, header controls 44 (padding-only), kpal/live-pill 44, touch-query block pads pills/typeahead/cmp-picker/cal-cell to 48, `.tl-game::after inset -11px` extends timeline hits, today-row link padding-extension; safe-area-inset on nav+toast+main, 100dvh, viewport-fit=cover; stacked cards <480. Defects: palette input 15px <16px → iOS focus auto-zoom (only sub-16 input; team/players inputs are 16px); 2-game today at 390 still fine but lookup latency 6.4s makes first search feel dead vs instant local filter | 8.6 |

## WEIGHTED TOTAL

identity 9.0×.12 + type 8.3×.12 + color 8.9×.10 + layout 8.8×.12 +
density 8.7×.12 + interaction 8.2×.10 + motion 8.9×.08 + depth 9.0×.08 +
consistency 8.4×.08 + mobile 8.6×.08 = **8.678 → 8.7**

(My lens trajectory: R2 7.7 → R4 8.6 → R5 8.7 — v55 closed the tap-target
regression; remaining weight sits in carried interaction/consistency debt.)

## 3 cheapest fixes

1. **AbortController + timeout in generic `api()`** (~10 lines, copy the
   typeahead's pattern): hung cell-network fetch currently = infinite skeleton
   on 3 tabs. Δ ≈ +0.3 (interaction 8.2→8.5; mobile inherits).
2. **`.pal-input-row input { font-size: 16px }`** (one declaration): kills iOS
   Safari focus auto-zoom on the only sub-16px input. Δ ≈ +0.15 (mobile).
3. **autoToggle checked-state feedback** (~6 lines: `#livePill:has(#autoToggle:checked)`
   dot/label state + title swap): turns an invisible-but-functional checkbox
   into legible control state; closes R4-4's partial fix. Δ ≈ +0.12
   (consistency + interaction).

Combined ≈ +0.55 → ~9.2 on this lens. (Non-cheap, flagged for the fix-swarm
anyway: rewrite the mono-scale original rule bodies — 3rd append would repeat
the R3 mistake — and warm `/api/players/lookup` in the cron's baseline path.)

**VERDICT: 8.7/10**
