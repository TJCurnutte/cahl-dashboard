# JURY R4 — 4/5 (INTERACTION LENS) — v54, Chrome-free

Method: static audit of deployed `/static/js/app.js?v=54` (145KB) + `style.css?v=54` (82KB) + index.html,
plus single-shot urllib timing + one 4-req concurrent burst. No browser automation (owner directive).

## Dimension table

| # | Dimension | Evidence (one line) | Score |
|---|-----------|--------------------|-------|
| 1 | Visual identity | Rink-lines hero watermark shipped (style.css:1586-1633, both themes, mobile-sized, static=reduced-motion safe); hockey grammar everywhere: LIVE breathe bar, score-flash, iCal/Share/race-badge | 8.5 |
| 2 | Typographic system | Saira Condensed 800 now in fonts <link> (index:28) — faux-bold fixed; JetBrains Mono labels; t-score/live-badge mono; count-ups via setMainHtml | 8.7 |
| 3 | Color system | Watermark hues exactly CBJ (rgba 206,17,38 red / 0,87,184 blue, dimmed for light theme via 0,38,84); live-pill light theme var(--loss); R3 faint-AA held | 8.6 |
| 4 | Layout & hierarchy | Render-token guard verified in deployed bytes (L951-974) — every await checked, catch guarded too; hash restore ordered pre-setTab (L2720-2722); league first-run auto-selects (L1270-1276) | 8.5 |
| 5 | Density & data presentation | tnum on board/goalies/standings/team tables (per R1-F); zebra, sticky thead, th[data-sort] + keyboard Enter/Space activation (L2424); no jiggling (mono numerals) | 8.4 |
| 6 | Interaction & micro-feedback | Debounces: team 180ms / player 220ms + stale-clear + input-match guards; toast confirm; refresh try/finally restore; watchdog 8s/20s; BUT live-pill still a functional checkbox (see defects) | 8.0 |
| 7 | Motion design | LIVE pulse/breathe/score-flash only; 3 reduced-motion blocks (1189, 1273, 1379) kill all animated layers incl. entrances; count-up rAF-based; pal-fade 120ms | 8.5 |
| 8 | Depth & material | Watermark via ::before/::after at whisper opacity (0.08-0.11) — layered luminance, not blur; flat panels, hairlines; no new fake shadows | 8.6 |
| 9 | Consistency & component quality | One scoreboard anatomy (sb-card/sb-side/sb-num); pal items grouped Pages/Teams/Players w/ aria-selected; chips from one system; scrimmage slots still muted (v45 discipline) | 8.3 |
| 10 | Mobile ergonomics | live-pill light-theme fix landed; 44px rules at 260/281; palette touch targets; scoreboard = stacked cards; BUT api() has no timeout + ≤430px header pass zeroes tap targets (see defects) | 7.8 |

**WEIGHTED TOTAL: 8.4/10**

## All 10 dimensions complete. Verified R3→R4 ledger

| Claim | Status in v54 bytes |
|---|---|
| Render-token guard | ✅ real (L951-974, after every await, catch guarded) |
| Watchdog 8s/20s + try/finally + Retry | ✅ real (L1810-1819, 2030-2037, teamErrorHtml L2040) |
| hashchange + re-entrancy guard | ✅ real (L930-935); boot hash restore ordered (L2720-2722) |
| 180ms debounce + taClearStale | ✅ real (L415, L377) |
| League first-run auto-select | ✅ real (L1272-1276) |
| Live-pill pure status | ⚠️ HALF — label logic pure, but hidden checkbox control REMAINS (index:95-98, $auto wired L2686) with zero visible response on toggle |
| Saira 800 loaded | ✅ (index:28) |
| Rink-lines watermark | ✅ real (CSS-only, both themes) |

## Defects justifying sub-9 scores (all source-verified)

1. **[interaction] Live-pill is still a control with no feedback** — index.html:95-98 ships
   `<input type="checkbox" id="autoToggle" class="sr-only">` inside the label; app.js:2686 wires change→30s
   auto-refresh; title says "click to toggle 30s auto-refresh". Zero `input:checked` CSS, no aria-checked,
   no toast/label change beyond the LIVE/NO GAMES LIVE status text (which is game-state-driven, not
   toggle-state-driven). v54's "pure status" fix only changed the label logic — the invisible control
   remains. Worst kind of interaction defect: a visible affordance that answers clicks with nothing.
   (-interaction, -consistency)
2. **[interaction] Generic `api()` has NO timeout/AbortController** (app.js:824-838) — the fetch used by
   League/Players/Analytics/Today can hang indefinitely on a stalled connection; only team-tab (25s abort)
   and palette (45s) are protected. Stuck-skeleton audit: League/Players/Analytics content areas have
   skeletonHtml → await api() with NO watchdog of their own — a hung api() leaves a skeleton past the
   team watchdog's jurisdiction. One-line AbortController+timeout fix. (-interaction, -mobile, -layout)
3. **[consistency] Stale `_renderToken` is a module global shared across ALL renders** — palette-open
   renders, hashchange, auto-refresh timer and pull-to-refresh all bump the same counter. Correct in
   practice (last-call-wins is the desired semantic), but a palette-triggered selectTeam during an
   in-flight tab render mid-animates; minor. (-consistency, minor)
4. **[motion] Count-up animations have no reduced-motion guard in JS** — CSS kills transitions/animations
   but JS rAF count-ups (setMainHtml → count-ups) still run; values settle ~600ms later for
   reduced-motion users. Minor. (-motion, minor)
5. **[mobile] Burst test: warm APIs all <1.5s** (today 493ms, teams 1457ms, players 10.3s cold-first-run),
   but api() has no retry and no timeout → mobile on flaky connections gets silent skeleton-hang instead
   of the team tab's error card. Same root cause as #2. (-mobile)
6. **[layout] League/Players/Analytics sub-skeletons sit inside a card that's already rendered** — good
   pattern (nav never dies), but sub-skeleton has no watchdog (League L1301-1305, Players L2124/2136) —
   hung league API = infinite sub-skeleton. Same fix class as #2. (-layout, minor)
7. **[mobile] ≤430px header pass zeroes the 44px tap targets (style.css:1872)** —
   `#themeToggle, #refreshBtn { min-height:0; min-width:0; padding:4px 8px }` overrides the 44px min rules
   at lines 260/281; live-pill clamps to height:26px (L1874). R2's exact bug class resurfacing in v54.
   (-mobile)

## 3 cheapest fixes, ranked by delta

1. **Add AbortController+timeout to generic api()** (~10 lines in one function) → fixes #2/#5/#6
   simultaneously; every tab gets the team-tab's error-card + watchdog behavior. **Δ ≈ +0.3** (interaction
   8.0→8.4, mobile 8.0→8.4, layout 8.5→8.7 weighted ≈ +0.11 raw; larger effective since it's a 10-line
   change closing the last systemic hang).
2. **Make the live-pill honest: either remove the checkbox or give it visible toggle state** (2-3 lines
   CSS `#livePill:has(input:checked)` + title change, or delete the input + change handler) → **Δ ≈ +0.2**
   (interaction 8.0→8.3, consistency 8.3→8.5).
3. **Guard JS count-ups behind `matchMedia('(prefers-reduced-motion: reduce)')`** (3 lines) → **Δ ≈ +0.1**
   (motion 8.5→8.7).

Runner-up: restore min-height/min-width at ≤430px instead of zeroing them (style.css:1872) — one-line
media-query fix, but interaction-lens delta small (~+0.1 mobile) since the compressed header is a
deliberate layout trade; worth bundling with fix #2.

### Score honesty check
- 9+ means no defect found at effort: I ran 15 greps + 8 full-file reads across app.js, CSS, index;
  found 2 functional defects + 2 minor — no dimension reaches 9.
- All sub-9 scores carry the concrete defect above.

VERDICT: 8.4/10
