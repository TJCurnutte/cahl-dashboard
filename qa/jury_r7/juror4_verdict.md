# JURY R7 — 4/5 (INTERACTION LENS) — v61, Chrome-free — VERIFY-AND-SCORE

Method: byte-audit of deployed `app.js?v=61` (153,328B) + `style.css?v=61` (86,371B) + index.html
(`/static/js|css/` paths this round), fetched 2026-09-04 ~14:01 ET. Version triad in sync:
JS_VERSION 61 (app.js:10) = APP_VERSION 61 (index:131) = `?v=61` on both assets. No browser
automation, no git (owner constraints). ~30 greps + 14 section dumps + 6 timed API single-shots +
WCAG contrast math. Timings: /api/version 0.15s, /api/today 1.65s, /api/today/scores 1.54s,
/api/league 1.97s, /api/leaders 1.56s, **/api/players 26.9s raw / 9.4s gzipped (1.55MB) —
trend 10.3 → 19.2 → 23.4 → 26.9s, now 3.1s from the client's own 30s ceiling**. Zero-data
September slate (0 games today): live/final paths verified byte-level, not pixel-level.

## Verification of R6-cited fixes in deployed v61 bytes — ALL LANDED

| R6 citation | v61 status |
|---|---|
| count-ups unguarded behind prefers-reduced-motion (3rd-round carry) | **FIXED** — app.js:772-779: `matchMedia('(prefers-reduced-motion: reduce)')` gate at fn top; RM users get final value painted, rAF loop never starts (L779 comment). CSS RM blocks (1198/1282/1388) + JS gate = no unguarded motion left |
| League/Analytics sub-skeletons watchdog-less | **FIXED** — app.js:1403-1414 `armSkeletonWatchdog($el,label,retryExpr)`: 8s "Still loading …" nudge, 20s "timed out" card with Retry; wired into League (1419, retryExpr `loadLeagueContent(...)`) and Analytics (2387, `loadActiveTab(true)`); `disarm()` in finally both sites |
| api() retry-once (v58) | **HELD** — app.js:868-876: 2-attempt loop, 700ms backoff, AbortError propagates immediately, 30s total ceiling intact (858-886) |
| By-Rink mixed-slate finals drop (R6-1's self-cancelling ternary) | **FIXED** — app.js:1183-1188: comment documents the mixed-slate case; `upcoming.concat(finals)` feeds every rink group; finals section (1201-1203) unchanged |
| window.loadTeamContent direct binding (v59) | **HELD** — app.js:2496-2500: direct binding + no-IIFE shadowing comment |
| tab-error Retry button | **HELD** — app.js:1025: `onclick="loadActiveTab(true)"` with client-error telemetry on recursion-class crashes (79-81 sendBeacon) |
| dark accent sub-AA (#e8253c, 3.96:1 on panel) | **FIXED** — style.css:37 `--accent: #ef3d54`; measured 5.13:1 on bg, **4.80:1 on panel #0e1420**, 5.06:1 on inset, 4.53:1 on panel-2 KPI gradient — all AA; light theme #ce1126 = 5.63:1 on white |
| button:hover #3a8fe0 off-token (3rd round) | **FIXED** — style.css:35 `--union-hover: #3a8fe0` (tokened, comment "R6: off-token hover hue retokened"); light: `--union-hover-deep: #0d3a73` (97); consumers 516/520 use the tokens |
| coarse-pointer 44px floors | **FIXED** — style.css:2087-2092 second coarse block: `.pill` min-height 44, `.pal-item` 14px pad, `#kpalBtn` min-width 44 — padding-only, no layout squeeze; joins the ≤430px block's kpalBtn/live-pill/themeToggle/refreshBtn floors (1951-1967) |
| scored-chip one-line truncation | **FIXED** — style.css:1679-1705: two-line grid anatomy (home line / away line, score right-aligned), ellipsis never eats scores; away line muted + 16px numerals matches sb-card hierarchy |
| cols-head ::after duplicate labels (R6-1) | **FIXED** — style.css:2046-2050: pseudo-labels deleted, spans auto-placed on the 11 tracks |
| .scrim class with no CSS | **FIXED** — style.css:436-438: muted italic, `:has(.scrim)` cursor:default |
| tonight-label 8.5px straggler (R6-3) | **FIXED** — 9.5px `--mono-xs` token (1711, 1947); type census 28 → 14 sizes |
| dataStamp = page-load time not data age | **OPEN (minor)** — app.js:2858 still `new Date()` at render; the label says UPDATED HH:MM with no "tonight" contradiction (index:105), so the residual is only that a 5-min-stale cache page claims a fresh timestamp |

New carry found this round: **watchdog/api contract race** — the 20s watchdog (1408-1412) fires
"timed out" while api() legitimately still has 10s of its 30s ceiling left (measured /api/players
26.9s proves it happens); when the response then lands, content replaces the retry card (best
case) — but if a user taps Retry first, the retryExpr call stacks a second identical request
against the same cold endpoint. Not user-visible today except on the players index, but it is a
contract mismatch: watchdog promises "timed out" 10s before the client gives up.

## Dimension table

| # | Dimension | Evidence (one line) | Score |
|---|-----------|--------------------|-------|
| 1 | Visual identity | Rink watermark + LIVE breathe + hockey grammar intact; tonight-KPI strip front door holds; brand/union hover now token-consistent; identity ceiling unchanged by this round's fixes | 8.7 |
| 2 | Typographic system | Type census 28 → 14 sizes (mono-xs 9.5 / mono-md 12 canonical); Saira display + JetBrains Mono href intact; scored-nums 20/16px two-line anatomy; RM-safe count-ups preserve painted numerals | 8.8 |
| 3 | Color system | Accent #ef3d54 = 5.13/4.80/4.53:1 on bg/panel/panel-2, light 5.63:1 — every accent consumer ≥AA measured; hover hues tokened both themes; residual = score-flash keyframe rgba hardcoded (same hue) + watch 3:1 UI-component floor | 9.1 |
| 4 | Layout & hierarchy | Zero dead states: watchdogs guarantee League/Analytics resolve (8s ack, 20s retry), players renders immediately with retry ladder, Team revived (v59); hashchange re-entrancy + boot-hash-before-setTab verified; residual = watchdog 20s vs api 30s contract mismatch | 8.9 |
| 5 | Density & data presentation | tnum on `table`, zebra (2014-2017), sticky corner both axes (492, 1161), sortable th with Enter/Space (L2532-2539 region held), playersRetries ≤4 @8s ladder (319-325); /api/players 5.6MB/26.9s is now the density story's weakest link | 8.7 |
| 6 | Interaction & micro-feedback | api() 30s ceiling + retry-once (868-876), watchdogs 1403-1414, :has(:checked) pill (247-248), btn-press pointerdown/up, ptr hint opacity feedback, taClearStale + typeahead retry chips, toasts, tab Retry (1025) — every tap now resolves to feedback ≤30s, most ≤2s | 9.2 |
| 7 | Motion design | RM gate on count-ups (772-779) closes the last unguarded JS motion; CSS RM coverage broad (3 blocks); LIVE pulse/score-flash/entrances purposeful; only decorative item = pal-fade/pal-pop, gated under RM? — pal-ov animation NOT in RM blocks (minor) | 9.3 |
| 8 | Depth & material | One backdrop-filter left (palette overlay blur(3px), 748) — justified for a modal scrim, not a card soup; luminance stack bg/panel/panel-2/panel-3 + hairlines intact; tonight-kpi gradient in-system | 8.8 |
| 9 | Consistency & component quality | scored-chip now matches sb-card anatomy; scrim in-system; mono tokens canonical; focus-visible 7 rules; hover tokens both themes; residual = dataStamp semantics + watch hardcoded rgba in keyframes | 8.9 |
| 10 | Mobile ergonomics | Coarse-pointer 44px floors second block (2087-2092) + ≤430px block; pal input 16px global (595); cols-head hidden <900px by design (1554-1556); scored-chip two-line kills chip truncation; residual = 26.9s players wait on cell network, ack at 8s but no cancel affordance | 9.0 |

**WEIGHTED TOTAL: 8.9/10** (8.92 exact; lineage 8.1 → 8.4 → 8.6 → **8.9**)

## 3 cheapest fixes toward 9.7-per-dimension

1. **Add a cache-status line to the typeahead + players empty state ("Index cold — 10-25s on
   first load of the day · runs once, then instant")** and print the same copy inside the 8s
   watchdog nudge when the pending request is `/api/players`. The 26.9s measurement (worse every
   round for four rounds) is the last "is it broken?" moment in the product; the copy already
   exists in spirit (app.js:525 "Index still filling — tap to retry") but only surfaces on
   lookup-empty, not during the wait. ~4 lines. **delta ≈ +0.4 interaction (9.2→9.6), +0.3
   mobile, +0.2 layout ≈ +0.10 total.**
2. **Reconcile watchdog vs api(): pass the api() deadline into armSkeletonWatchdog (or lower the
   ceiling to 20s for sub-section fetches)** so "timed out" can never print while the request is
   still in flight, and debounce retryExpr taps (`if ($el.dataset.retrying) return`). ~5 lines in
   1403-1414 + one flag. **delta ≈ +0.3 layout, +0.2 consistency ≈ +0.05 total — and it removes
   the double-request footgun before a real slate night.**
3. **Close the two last motion/color stragglers: put `.pal-ov.open` + `.pal` under the RM blocks
   (one selector each in 1198/1388), and swap the two hardcoded `rgba(42,127,212,…)` keyframe
   stops (1268-1270) for a `--union-glow` token.** ~4 lines. **delta ≈ +0.2 motion (9.3→9.5),
   +0.2 color (9.1→9.3) ≈ +0.04 total.**

Projected combined: ~9.1/10. The gate demands ≥9.7 **per dimension**: interaction and motion are
now within one cheap pass of it; identity (8.7), type (8.8), density (8.7) sit below with no
bug-shaped lever left — that gap is signature-surface design work (a real data-viz moment, a
broadcast-grade scoreboard face) plus the players-index payload (5.6MB, 26.9s cold, gzip only by
negotiation — a server-side cap/paginate is the honest fix, not a client patch).

## Score honesty check

- 9+ means no defect findable at effort: this round found 1 new systemic carry (watchdog 20s vs
  api 30s contract), 1 open minor (dataStamp render-time), 1 perf trend worse four rounds
  straight (/api/players 26.9s), 2 cosmetic stragglers (palette RM, keyframe rgba). No dimension
  reaches 9.7; three reach 9+ and every one has a cited concrete defect or an unexercised
  surface (zero-data September: live pulse, score flash, By-Rink finals recovery are byte-verified
  only — the slate will not let me see them move).
- Score deltas vs my R6 table trace to byte changes: interaction +0.3 (watchdogs landed), motion
  +0.8 (RM gate closed the 3rd-round carry), color +0.7 (accent 4.80:1 on panel measured, hovers
  tokened), layout +0.3 (all sub-skeleton states now resolve), mobile +0.2 (coarse floors +
  scored-chip), type +0.1 (census halved), consistency +0.3 (scrim/chip/cols-head in-system),
  depth +0.2, identity +0.0 (nothing identity-shaped changed), density +0.3 (sortable/keyboard
  held; payload size capped the gain).
- Every R6-cited fix was confirmed in deployed bytes with line numbers above — no claimed fix
  was taken on trust; the two carried minors are quoted at their live line numbers.

VERDICT: 8.9/10
