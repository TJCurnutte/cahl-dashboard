# CAHL UI/UX JURY — R4, Juror 2/5 — MOBILE lens — v54

Method: no browser automation (owner rule). Source-level audit of the deployed
bytes: index.html + style.css?v=54 (82KB, 1,997 lines) + app.js?v=54 fetched live
2026-09-03; WCAG contrast computed from hex; live API timing via urllib burst
(6 parallel, 10.7s wall). Paint items are marked **(static)** — no screenshot
verification was possible this round.

## Score table

| # | Dimension | Evidence (what I verified) | Score |
|---|---|---|---|
| 1 | Visual identity 12% | Rink-night canvas #070b12, Saira Condensed display + JetBrains Mono labels; **v54 rink-lines hero watermark shipped**: red center line, quarter-ice blue lines, goal lines, 180px center-circle ring with inset crease halo, both themes, static so reduced-motion needs no guard. Verified in deployed CSS L1586–1631, not in a live paint. | 9.1 |
| 2 | Typographic system 12% | Saira Condensed 600/700/**800** all in the Google Fonts href (R2/R3 faux-bold fixed); JetBrains Mono on all eyebrow/th/label roles; tabular-nums declared globally (L134) + per-table (L1646); mono scale tokenized --mono-xs/sm/md with 5 migrated selectors; .jersey-num display digits. Hardcoded font-size scatter persists elsewhere (heatmap 12/13px, heat-name 13px, gd-empty 13px, brand 17/19px, t-home 16.5/17px). | 8.2 |
| 3 | Color system 10% | CBJ Union Blue/Goal Red discipline holds: accent only on live/active/CTA (nav active inset stripe, live-row tint, h2 marker, ::selection, focus). Status hues win/loss/tie/otl differentiated. Effective tokens (L1788 override): faint 5.37 dark / 4.55–4.89 light; muted 5.97 dark / 4.69–5.77 light — all AA; accent-on-panel 4.18:1 dark (large/graphic use only). | 9.0 |
| 4 | Layout & hierarchy 12% | Marquee (hero + scoreboard cards) vs long-tail (tables) distinction intact; 599/699/768/900 rhythm; **R2 cols-head leak fixed**: header grid display:none ≤899px, 11-track abs-pos pseudo grid only ≥900px; ≤479 stack puts time+status on line 1, home/away full-width, rink inline — hierarchy correct at 390px on paper. | 8.6 |
| 5 | Density & data presentation 12% | Mobile tables: display:block + overflow-x:auto with min-width floors (44px cells, 132px first col, rank/name floors on .board), sticky header row, **sticky first column on touch devices** (L1152), self-hiding two-layer swipe fade (local/scroll attachment, L1826–1846) + "swipe ›" chip; zebra on all three table families (both themes); sortable th with hover glyphs. No jiggling numerals anywhere (tabular). | 9.2 |
| 6 | Interaction & micro-feedback 10% | pointerdown .btn-press scale(0.94) class-toggle (not just :active, works on iOS where :active is unreliable); :active transform on buttons; pull-to-refresh implemented on main (passive pointer tracking + touchend threshold); button/ghost/hover states + focus-visible ring. No -webkit-tap-highlight-color neutralized — iOS default gray flash on <a> rows (nav, today-row links). Nav links have no :active state. (static + live API: today 0.49s, leaders 0.40s, version 1.15s, teams 4.51s, players 10.66s cold — typeahead/roster UX waits are real on first run, mitigated by cron warm) | 8.0 |
| 7 | Motion design 8% | Motion inventory: LIVE pulse, score flash, entrance fade, skeletons, button press, hover transitions — all purposeful; 3 reduced-motion blocks (L1189, 1273, 1379) kill every animation incl. skeleton shimmer + score flash; static watermark needs no guard. Decorative motion: none found. (static) | 9.0 |
| 8 | Depth & material 8% | Luminance-stacked surfaces bg→bg-raise→panel→panel-2→panel-3 + inset wells; hairline borders at 8–14% alpha; shadows barely-there + 1px ring (correct call for dark); blur tokens explicitly none; no fake-glow soups. Watermark sits at whisper opacity (0.08–0.11) under content z-index guard. | 9.0 |
| 9 | Consistency & component quality 8% | One scorecell anatomy across sb-card/today-row/game-card; chips/pills/badges share mono-caps treatment; mono scale tokens; status colors from one system; R1-D analytics classes (heat/gd) all defined. Residual: hardcoded px font-sizes outside the mono-token system (see D2); version stamp fixed (APP_VERSION=54 = JS_VERSION=54 = ?v=54 everywhere). | 8.4 |
| 10 | Mobile ergonomics 8% | Viewport `width=device-width, initial-scale=1.0, viewport-fit=cover` — user-scalable removed (R3 fixed); nav min 44→48px on touch with safe-area-inset-bottom padding; main clears nav (72px + safe-area); ≤699 table treatment + ≤479 card-stack solid; **BUT the ≤430 header block (L1872–1874) again sets `min-height:0; min-width:0` on #themeToggle/#refreshBtn — the exact R2 regression — leaving computed targets ≈22×31px; #kpalBtn 26px and live-pill 26px also sub-44; no -webkit-tap-highlight-color; manifest standalone + icons present. (static) | 7.2 |

## WEIGHTED TOTAL
0.121×9.1 + 0.122×8.2 + 0.10×9.0 + 0.122×8.6 + 0.122×9.2 + 0.10×8.0 +
0.08×9.0 + 0.08×9.0 + 0.08×8.4 + 0.08×7.2 = **8.58 → 8.6/10**

## The 3 cheapest fixes that would raise the score most

1. **Restore ≥44px hit areas inside the ≤430 header compression** (+0.4 mobile →
   +0.03 total, and it is the one hard a11y failure): delete the
   `min-height:0; min-width:0` on #themeToggle/#refreshBtn (L1872), keep the
   visual squeeze via padding/font-size only, and give #kpalBtn/.live-pill
   `min-height:44px` with transparent padding (or an ::after inset hit-slop).
   One-line root cause: visual compaction was again done with box-size zeros.

2. **Add `-webkit-tap-highlight-color: transparent` + :active states for nav and
   row links** (+0.2 interaction): one base rule `a { -webkit-tap-highlight-color:
   transparent; }` plus `nav a:active, .today-row .link:active { opacity:.7; }`
   removes the iOS gray flash and gives thumb-feedback parity with buttons.

3. **Finish the type-scale migration** (+0.2 consistency): sweep the ~10
   hardcoded font-sizes outside the mono tokens (heat-val 12px, heat-name 13px,
   gd-empty 13px, brand 17/19px, t-home 16.5/17px, sb-name 20px) into
   --mono-* / display tokens so future passes can't re-scatter it.

## Honesty notes
- All scores below 9 carry named defects above; D1–D4, D7, D8 are source-verified
  only — no screenshots this round, so paint-level artifacts (watermark rendering
  under real content, sticky-first-col behavior, swipe-fade self-hiding) remain
  unverified in a live viewport.
- Live API burst (6 parallel): today 0.49s / leaders 0.40s / version 1.15s /
  teams 4.51s / players 10.66s (5.5MB) — cold players latency is real but the
  cron warm (players?full=1 + teams every baseline, verified in
  .github/scripts/refresh_cache.py L87–103) is the correct mitigation.
- R3 ledger re-verified in deployed v54 bytes: viewport user-scalable removed ✓,
  Saira 800 in href ✓, faint AA tokens ✓, bye-ingest filter ✓, stale-listbox
  clear (taClearStale L377) ✓, league first-run auto-select (app.js L1272) ✓,
  version sync ✓, cols-head ≤899 none ✓, rink watermark ✓, cron warm ✓.
- Known-open from earlier rounds, still open: hero `hero-team` guard OK but
  `.hero-card::after` 130px circle ≤479 (L1633) sits under content — fine; no new
  regressions found beyond D10 header tap targets and missing tap-highlight.

VERDICT: 8.6/10
