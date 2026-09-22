# Jury R7 — Juror 5/5 — PRODUCT CREDIBILITY lens (v61, deployed bytes)

Method (Chrome-free, standing owner rule): fetched deployed `/` shell (8,518 B), `app.js?v=61`
(153,328 B), `style.css?v=61` (86,371 B), plus live APIs: `/api/version` → `{"js":61}`
(shell links `style.css?v=61` + `app.js?v=61`, inline `APP_VERSION = 61` — deploy verified),
`/api/today` (1.6s), `/api/today/scores` (1.2s), `/api/teams` (1.8s, 85 KB), `/api/leaders`
(1.7s), `/api/players` (**12.2s, 5.6 MB** — best ever measured; was 40s/2 MB in R6).
`/api/league/<id>` and `/api/team/<id>` returned 502 with raw scraper error strings during
this round (upstream chillerstats.com 403/short-page) — itself a live test of the app's
error path; findings noted under dimension 9. WCAG contrast recomputed on v61 tokens.
No browser automation; every claim byte- or payload-verified against prod.

## v61 gate verification (all 8 task-mandated claims)

| Claim | Status | Evidence (deployed bytes) |
|---|---|---|
| `/api/version` = `{"js":61}` | ✅ PASS | `{"js":61}`; shell `?v=61` on both assets; `APP_VERSION = 61` — no boot reload loop |
| By-Rink mixed-slate finals recovery | ✅ SHIPPED | `app.js:1188` `upcoming.concat(finals)` (self-cancelling ternary deleted); comment at L1182-1186 cites "jury R6-1/R6-2 convergent find"; mixed statuses render inside one rink group since each row carries its own chip |
| Scored-chip two-line anatomy | ✅ SHIPPED | CSS:1679-1699 `.scored-chip` grid `minmax(0,1fr) auto` — home line / away line stacked, score right-aligned (`scored-nums` 20px/16px), comment credits R6-2; no truncation possible |
| Team-tab crash fix (direct binding) | ✅ SHIPPED | `app.js:2500` `window.loadTeamContent = loadTeamContent` with a comment that names the forbidden arrow-shadow form verbatim (L2496-2499) |
| `api()` 30s ceiling + retry-once | ✅ SHIPPED | `app.js:858-885` AbortController + 30s kill + one silent retry on network/5xx + cache key; finally clears the timer |
| Client error telemetry | ✅ SHIPPED | `app.js:67-84` `/api/client-error` sendBeacon→fetch keepalive fallback, version-stamped, debounced; wired to recursion-class errors at L86-88 and L1024 |
| Night KPI strip + scoreboard strip + By-Rink on Today | ✅ SHIPPED | `app.js:1153-1158` (Games/Rinks/Live/First-puck), L1176-1179 scored strip, L1188-1209 by-rink; ≤599px squeeze at CSS:1707-1714 |
| Scrim rows muted/italic | ✅ SHIPPED | CSS:436-438 `.today-row .t-home.scrim/.t-away.scrim` muted + italic + `:has(.scrim){cursor:default}` — the R6 "class with zero CSS" hole is closed |
| Coarse-pointer 44px floors | ✅ SHIPPED | CSS:2087-2092 `@media (hover:none),(pointer:coarse){ .pill 44 · .pal-item pad 14 · #kpalBtn 44 }` — J2-R6's exact three selectors |

Ledger regression re-checks: 0 `#3a8fe0` as a literal hover (now a documented token at
CSS:35/516), 0 cols-head `::after` label dupes (CSS:2044-2049 explicitly deletes them),
0 `min-height:0|min-width:0` on controls inside max-width media blocks (L1103 is the
min-width:900px **desktop** nav compaction — pointer devices, not a regression of the R2/R4
class), 0 `PACEMAKERS`/`vs @`/`verBadge`/double-escaped `\u2026`. Type census: **28 → 13
distinct font-sizes** (9.5–34px); mono tokens wired including the ≤599px `.tonight-label`.

**New defect found this round — Defect R7-A:** the team-tab `recent_result` card
(`app.js:2057-2060`) still lacks the `hasOpp` guard the hero has (L1334-1335). Same blank
`0-0`-card risk the R6 report flagged; the guard was copied to the *next_game* site but not
this one. Dormant today (thin slate), fires the first time a scraped result lacks an
opponent name. Also: the generic error renderers interpolate raw upstream text —
`app.js:1268` and `app.js:1426` paint `${data.error}` un-escaped, so this round's live 502
bodies ("Suspiciously short page (0 bytes): /team/?TeamID=…", "403 … chillerstats.com")
would paint scraper internals straight into the card. Honest, but a data-journalism
credibility leak; `esc()` is one call away and exists on every other path.

## The 10 dimensions

| # | Dimension | Evidence (what I saw) | Score |
|---|---|---|---|
| 1 | Visual identity (12%) | The broadcast stack is complete and coherent on both themes: rink-lines hero watermark (CSS:1589+, ≤0.11 alpha, clipped by `overflow:hidden` at L1879), broadcast-bug brand stack (wordmark + mono sub-label, L211-232), Saira Condensed display numerals, JetBrains Mono eyebrows, CBJ-only hues, night KPI band, scored-strip, by-rink h3s. Nothing reads generic-admin. Remaining: the 4.5s infinite `hero-glow-breathe` is atmosphere, and the desktop brand still has no marquee-scale signature moment (watermark is whisper-level). | 9.4 |
| 2 | Typographic system (12%) | The five-round mono/type ledger is finally cashed: 13 distinct font-sizes (was 28 in R5), Saira 600/700/800 all shipped, tabular-nums block (CSS:137-140) covers tables/numerals, `--mono-xs/sm/md` = 9.5/10.5/12px defined (L2003-2005) AND applied (`.eyebrow/th/.status-chip/.sb-meta/.pal-grp/.award-*/.heat-val`), mobile `.tonight-label` retokened (L1711), `--mono-md` is a live 12px canonical (5 consumers). Stragglers: 13px body scatter (22 rules, mostly muted meta text — one hair off the 14px floor) keeps this under the 9.7 gate. | 9.4 |
| 3 | Color system (10%) | Every carried contrast defect is dead: dark `--accent #ef3d54` = **4.80:1 on panel** (5.13 on bg) — AA for the 9.5px live labels it colors; light `#ce1126` = 5.63 on white; muted/faint ≥5.78 dark, ≥5.04 light (computed); the 4-round `#3a8fe0` hover is now a *documented token* (`--union-hover`, 5.43:1 on panel) with a light-theme twin. One straggle: `.pill` border-color at 4.18:1 on panel (borders exempt from AA, but it's the last sub-4.5 in my sweep). Red discipline: accent = live/interactive only; wins are green. | 9.4 |
| 4 | Layout & hierarchy (12%) | Marquee order is complete and now *correct under mixing*: night KPI strip → my-team hero/CTA → LIVE scoreboard → On The Scoreboard chips → By-Rink groups (finals no longer vanish on multi-rink nights — the R6-1 defect is dead at L1188) → single-rink Final/Upcoming fallbacks. Empty night renders strip + CTA + "No games posted yet." card. GD viz empty state ("No goal data yet — season hasn't started", L2439) remains the honesty exemplar. Deduction: Defect R7-A (unguarded second recent_result) + League "Top Scorers" has no zero-season gate — currently moot (leaders carry real 3-7 point values in the live payload) but the table renders bare rows with no framing if the season resets. | 9.5 |
| 5 | Density & data presentation (12%) | Sticky theads ×2, zebra with explicit even:hover (CSS:2027-2036), fully sortable th with keyboard focus + per-column arrows (L571-574; hover shows ↕), tnum on every numeric column, standings race badges (clinch/elim/playoff states), scrim rows muted/italic/non-interactive, roster per-GP rates, swipe-fade scroll cue. All-zero standings columns are truthful data. One credibility dent: `dataStamp` still prints page-load time as "UPDATED HH:MM" (L2856-2861) — the R5/R6 "semantic fib" carry, untouched for 3 rounds. | 9.4 |
| 6 | Interaction & micro-feedback (10%) | The R6 finding ("no busy state on refresh") is fixed: `refreshAll()` disables the button, swaps in a spinner, and a `finally` restores it even on throw (L889-906). `api()` 30s ceiling + retry-once; 8s/20s skeleton watchdogs on league/analytics sub-sections; 180ms typeahead debounce + stale-clear; toast role=status; pull-to-refresh with in-flight guard; live-poll in-flight+hidden guards. Latency reality: `/api/players` 12.2s/5.6MB this round (improved from 40s) — the 22s team-path abort handles it honestly with a Retry card, but first leaderboard paint is still seconds of skeleton. | 9.5 |
| 7 | Motion design (8%) | 11 keyframes, each traceable to exactly one purpose (live pulse/breathe, score-flash, shimmer=skeleton only, rise-in, pal-pop, hero-next-pulse, spin, fade). Count-ups now respect `prefers-reduced-motion` (L773-779: matchMedia gate paints final value — the R4/R6 carry is closed). 4 RM blocks + global `transition-duration:0.01ms` kill (L1203). Deduction: `hero-glow-breathe` (4.5s infinite alternate, L1228) remains the one decorative-leaning animation — atmosphere, not information. | 9.3 |
| 8 | Depth & material (8%) | Still the cleanest dimension: 4-stop luminance ladder (bg→inset→panel→panel-2→panel-3), 1 backdrop-filter total (palette scrim), hairline borders 8–26% alpha, inset/1px structural shadows, watermark alphas ≤0.11, `overflow:hidden` clipping, print stylesheets ×2, the two-layer `local,scroll` swipe-fade that self-hides at full scroll (L1912-1927), reduced print of hero glows (L1404). No blur soup, no fake glows on cards, nothing to fix. | 9.5 |
| 9 | Consistency & component quality (8%) | One scorecell anatomy everywhere (t-score/live-badge/em-dash empty), one chip grammar (status-chip, pos-chip, race-badge, award-badge, strk, form-chip), scored-chip rebuilt on the sb-card grid, scrim class now styled, hover tokenized, cols-head single-label. BUT the two-idiom debt is unchanged: **28 inline `onclick=`** handlers coexist with delegated `data-*` systems (8 `data-sort` sites), **45 inline `style="…"`** in JS strings (7 identical `margin-top:18px` h3s; `.section-h` was proposed in R5 and never created), and un-escaped `${data.error}` (L1268/1426) is the one place the system's own esc() discipline is skipped. | 9.4 |
| 10 | Mobile ergonomics (8%) | Coarse-pointer 44px floors shipped (`.pill/.pal-item/#kpalBtn`); 17 explicit 44px+ declarations; ≤430 header squeeze is padding/typography-only; ≤479 four-area card stack (L1970-1986) with 17px names and full-width rink; release-gate grep clean — the only `min-h/w:0` hits are text-overflow guards and the ≥900px desktop nav; 48px floors on nav links + timeline hit-extension; 16px inputs (no iOS zoom); safe-area insets; tap-highlight + :active parity; swipe › chip; focus-visible ×7. Scored-chip two-line anatomy kills the last 390px truncation. | 9.5 |

## WEIGHTED TOTAL

identity 9.4×12% + type 9.4×12% + color 9.4×10% + layout 9.5×12% + density 9.4×12% +
interaction 9.5×10% + motion 9.3×8% + depth 9.5×8% + consistency 9.4×8% + mobile 9.5×8%
= 1.128 + 1.128 + 0.94 + 1.14 + 1.128 + 0.95 + 0.744 + 0.76 + 0.752 + 0.76 = **9.4 / 10**
(unrounded 9.43)

Lineage: R3 7.3 → R4 8.4 → R5 8.4 → R6 8.8 → **R7 9.4**. First juror (including my own
card) over 9.0: the R6 convergent fixes all landed byte-verified, the standing ledgers
(mono scale, contrast, tap floors, api ceiling) are closed rather than carried, and no
new craft violation shipped with the v61 enrichment — the first round where the fix rate
beat the regression rate on my card. The all-dimensions 9.7 gate still fails.

## The 3 cheapest fixes toward 9.7-per-dimension

1. **Copy the hero's `hasOpp` guard onto the team-tab recent_result site + esc() the
   raw error interpolations.** `app.js:2057-2060` gets the same `const hasOpp = !!(isHome ?
   r.away : r.home)` ternary the hero already runs at L1334 (guard is copy-paste, ~3
   lines); `app.js:1268` and `app.js:1426` get `esc(data.error)`. Kills the last
   blank-`0-0`-card path and stops scraper internals (live-observed 502 bodies) from
   painting raw into cards. **Δ layout 9.5→9.7, consistency +0.1 (weighted +0.032).**

2. **Create `.section-h` and sweep the inline styles.** One class for the 7 identical
   `margin-top:18px` h3s, then a mechanical pass converting the remaining ~38 inline
   `style="…"` occurrences to classes — the R5 "two idioms" finding, third round carried.
   **Δ consistency 9.4→9.7 (weighted +0.024), type +0.1.**

3. **Retire `hero-glow-breathe`** (L1228-1232): delete the animation declaration or
   replace with a static gradient — the glow itself stays, the 4.5s infinite pulse goes.
   One keyframe + one declaration. The only decorative-leaning motion in the file, and the
   sole deduction keeping motion below 9.7. **Δ motion 9.3→9.7 (weighted +0.032).**

Ceiling with all three: ≈ 9.5 weighted. The residual gap to 9.7 is the interaction-idiom
unification (28 onclicks → delegated data-*), real multi-rink/live data to prove the
By-Rink recovery in the wild, and upstream `/api/team`+`/api/league` stability (this
round's 502s) — the first is one focused pass, the second is the calendar, the third is
the scraper's war with chillerstats.com.

## Residual credibility risks (static-verification limits)

- Upstream `/api/league/*` and `/api/team/*` returned 502 with raw scraper errors during
  this round — the client's timeout/retry/watchdog stack handled termination honestly, but
  the *copy* leaked scraper internals (un-escaped) and League/Team tabs were dead-ends
  while it lasted. Esc + a friendlier "upstream stats feed is unreachable" frame is a 5-line fix.
- `dataStamp` = page-load time, not data age (3-round carry; semantic fib).
- Live detection remains a time heuristic (≤100min); postponed games could show LIVE —
  unverifiable without live data.
- (static) All findings from deployed bytes + API payloads; no rendered-pixel verification
  under the no-Chrome constraint. Contrast figures are computed, not screenshot-sampled.

VERDICT: 9.4/10
