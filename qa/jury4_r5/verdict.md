# JURY R5 — 4/5 (INTERACTION LENS) — v55, Chrome-free

Method: byte-audit of deployed `/static/js/app.js?v=55` (145,172B), `style.css?v=55` (82,825B), index.html
(APP_VERSION 55 = JS_VERSION 55 = asset ?v=55 — version triad in sync). Deployed-equivalence chain: my fetch
sha256 c29e999f6173 == juryR5/v55_js.js == qa/jury4_r5/app.js (both fetched independently 2026-09-03 20:50).
app.js v54->v55 diff = version-bump only; CSS diff = 2 blocks (<=430px 44px hit-area restore + tap-highlight/:active
parity). One urllib timing pass: 4 single-shots + one 4-parallel burst (1.76s of the 60s budget). No browser
automation, no git (owner constraints). 15+ greps + 6 section dumps.

## Dimension table

| # | Dimension | Evidence (one line) | Score |
|---|-----------|--------------------|-------|
| 1 | Visual identity | Unchanged from R4: rink-lines watermark, LIVE breathe bar, hockey grammar; v55 adds no identity surface | 8.5 |
| 2 | Typographic system | Saira Condensed 600/700/800 + JetBrains Mono 400/500/600 in fonts href (index:28); t-score/live-badge mono verified in bytes | 8.7 |
| 3 | Color system | No color changes in v55; R3 faint-AA held; v55 :active uses opacity (0.7) not off-palette tints — discipline kept | 8.6 |
| 4 | Layout & hierarchy | Render-token guard real (L951-974, stale() after every await + in catch); hashchange re-entrancy guard (L930-935); BUT League/Players/Analytics sub-skeletons still watchdog-less (L1301-1305) | 8.5 |
| 5 | Density & data presentation | sortTh data-sort+data-rt headers (L545, L1370-1378), keyboard Enter/Space activation (L2422-2429), tnum/zebra/sticky from R1-F — all present in v55 bytes | 8.4 |
| 6 | Interaction & micro-feedback | NEW :active parity (nav/today-row/typeahead/pal-item opacity 0.7 + tap-highlight transparent); refreshAll try/finally (L844-857); 180ms debounce + taClearStale (L415/L377); BUT api() (L824-838) still has NO timeout/AbortController and live-pill autoToggle still answers clicks with nothing | 8.2 |
| 7 | Motion design | No new animation in v55; :active is instant (<100ms); count-ups still unguarded for reduced-motion (JS rAF) | 8.5 |
| 8 | Depth & material | Watermark whisper opacities, hairlines, flat panels — untouched by v55 diff | 8.6 |
| 9 | Consistency & component quality | :active now consistent across all 5 interactive classes; pal items grouped w/ ArrowUp/Down/Enter/Escape (L2922-2944); autoToggle checkbox remains the one control outside the system | 8.4 |
| 10 | Mobile ergonomics | R2 bug class KILLED at source: <=430px pass now min-height/width:44px on kpalBtn/live-pill/themeToggle/refreshBtn (css L1872-1881) + iOS gray tap-flash removed; BUT flaky-network mobile still gets silent skeleton-hang (no api() timeout) | 8.1 |

**WEIGHTED TOTAL: 8.5/10**

## R4 -> R5 defect ledger (re-verified against v55 bytes)

| R4 defect | v55 status |
|---|---|
| api() no timeout/AbortController (League/Players/Analytics infinite skeleton) | STILL PRESENT (app.js L824-838, catch returns error only on network throw; a stalled-but-open fetch hangs forever) |
| live-pill autoToggle checkbox w/ zero checked-state feedback | STILL PRESENT (index L95-99; 0 `input:checked` rules in style.css; $auto wired app.js) |
| shared _renderToken minor | unchanged (minor) |
| count-ups unguarded reduced-motion | unchanged (minor) |
| <=430px tap-target zeroing (R2 bug class) | **FIXED** (css L1868-1884: min-height/min-width 44px, padding compaction only) |
| iOS tap-highlight gray flash | **FIXED** (css L1886-1890: transparent + :active opacity parity) |

## Live timing (urllib, 2026-09-04 09:21 ET, warm cron)

Single-shot: /api/today 0.35s, /api/teams 0.36s (253 teams, 85KB), /api/leaders 0.32s, /api/version 0.33s.
4-parallel burst: 0.37/0.40/0.34/0.25s, wall 0.40s — no serialization stall. Pass total 1.76s (budget 60s).
Cron warm is doing its job; the interaction risk is now purely client-side (api() hang), not backend latency.

## 3 cheapest fixes, ranked by delta

1. **AbortController + timeout in generic api()** (~10 lines) -> League/Players/Analytics get the team-tab's
   error-card behavior; kills the last systemic hang incl. flaky-mobile. **delta ~= +0.3** (interaction 8.2->8.5,
   mobile 8.1->8.5, layout +0.2).
2. **Make live-pill toggle honest**: 3-line CSS `#livePill:has(input:checked) .live-pill-dot` + pressed tint, or
   delete the checkbox + handler. **delta ~= +0.2** (interaction, consistency).
3. **Guard count-ups behind matchMedia('(prefers-reduced-motion: reduce)')** (3 lines). **delta ~= +0.1** (motion).

## Score honesty check
- 9+ requires no defect at effort: 15+ greps, 6 full-section dumps, byte-diff v54->v55, timing pass — found
  2 systemic interaction defects + 2 minors still open; no dimension reaches 9.
- All 10 scores carry their concrete defect line above. Scores move only where v55 bytes moved (interaction
  +0.2, consistency +0.1, mobile +0.3); all others held from my R4 table.

VERDICT: 8.5/10
