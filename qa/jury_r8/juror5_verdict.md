# Jury R8 — Juror 5/5 — PRODUCT CREDIBILITY lens (v63, deployed bytes)

Method (Chrome-free, standing owner rule): fetched deployed `/` shell (9,964 B — now carries
the landing gate), `app.js?v=63` (156,017 B), `style.css?v=63` (88,121 B), **new**
`landing.css?v=63` (6,510 B), `cahl-logo.svg` (2,936 B), `cahl-logo-hd.png` (129 KB),
`upright-crown.png` (128 KB), `cahl-icon-512.png` (81 KB), `manifest.json`. Live APIs this
round, all 200: `/api/version` {"js":63} (+ shell `?v=63` ×3 + inline `APP_VERSION = 63` —
deploy verified), `/api/today` (1.35s, 2 real games), `/api/today/scores` (1.32s), `/api/teams`
(4.87s, 253 teams), `/api/leaders` (1.26s), `/api/league/<id>` (1.64s — **recovered from R7's
502s**), `/api/team/<id>` (3.08s), and `/api/players` — **45.03s / 3.7 MB, worst ever measured**
(R5 19.2s → R6 23.4s → R7 12.2s → R8 45.0s). WCAG recomputed on v63 tokens; PNG alpha channels
decoded byte-level (zlib unfilter); gate/crest/crown assets inspected by image analysis. No
browser automation; every claim byte-, payload-, or pixel-file-verified against prod.

## v63 gate verification — my 3 R7 cited fixes

| Fix | Status | Evidence (deployed bytes) |
|---|---|---|
| `hasOpp` guard on team-page `recent_result` | ✅ SHIPPED + **live-validated** | `app.js:2102-2105` — comment names "R7-5: same hasOpp guard as the hero"; guard is `!!((r.home_id === teamId) ? r.away : r.home)`. Not dormant: **today's live `/api/team` payload ships `home:""`, `away:""`** in `recent_result` — the guard is what keeps the blank `0-0` card off the Team tab right now. |
| `esc(data.error)` on the 4 error paint sites | ◐ PARTIAL (4 of 6) | Esc'd: L1298, L1469, L2004, L2343 (+ league-list error L1940 escapes inline). **RAW remains: L2306 + L2317** (`renderPlayers`, `setMainHtml(html + `<div class="error">${data.error}</div>`)`) **and L2446** (`loadAnalyticsContent`, `${(data||{}).error || 'No data'}`). The R7-A scraper-internals leak is closed on Today/League/Team but still open on Players + Analytics. |
| `h3.section-h` replaces the 7 inline h3s | ✅ SHIPPED | `style.css:437` `h3.section-h { margin: 18px 0 10px; }` with "one idiom" comment; 7 emitters in app.js; **0 `margin-top:18px` literals remain**. BUT two inline-styled headings still ship: L1489 (`<h3 style="margin:18px 0 10px;color:var(--text)">` + nested span style) and L277 `leaderSection` (`<h3 style="margin-top:16px">` ×4 uses). Inline `style=` census: 43 (was 45). |

Also verified from the v63 log: `hero-glow-breathe` **retired** (css:1236 "breathe pulse retired —
static glow"; zero keyframe refs — my R7 fix #3); rink-head `#4a9ae6` = **6.20:1** on dark panel
(closes the R7-3 two-round carry); `sb-card[data-scrim="1"]` muted/italic/non-interactive
(css:441-443, closes R7-1's partial); row `focus-within` hover parity (css:504); tonight-strip
2×2 at ≤430px (css:2111); 40s watchdog + debounced retry (L1437-1455, deadline now exceeds the
30s api ceiling); cold-index typeahead copy (L531).

## New since R7 — landing gate + sponsor surface (scored honestly)

- **Gate markup** (shell L48-64): `#landingGate` `role="dialog" aria-modal` with aria-label,
  HD crest, headline, single CTA, sponsor banner; session-skipped via `sessionStorage['cahl-entered']`
  (app.js:12-23) with private-mode try/catch, focus moved to `#main` on enter, 500ms fade-then-remove.
- **Gate CSS** (landing.css): on-system — `--mono-sm/xs` kickers, display face title (30px→25px at
  ≤479), rink-lines ::before echoing the hero watermark (alphas 0.05–0.10), `--panel`/`--border`
  card, RM block covers every transition (L172-174), 479px pass. CTA white-on-`#1f6cb8` = **5.39:1**
  (AA; 19px/700 is WCAG large text where 3:1 suffices — hover `#2a7fd4` 4.13:1 also ≥3:1).
- **Crest**: vision-verified as a credible league mark ("hits every convention of the genre…
  not amateur clip-art") — crisp vector edges, even star arc, no clipping/fringe; transparent
  alpha confirmed byte-level (77.7% opaque / 22.3% transparent, zero partial-alpha fringe class).
  Same mark powers header brand, favicon (SVG), apple-touch, manifest (512 maskable), OG/twitter.
- **Crown**: real mark from uprightcreativeco.com; alpha decoded — **29.8% fully transparent,
  true transparency, no white-box defect**; hover gold `#b8925e` = 6.68:1 on inset. Sponsor strip
  on Today tab (app.js:1235-1239) sits below the data, above the nav — correct marquee respect.
- Nit: OG image is 512×512 square (platforms expect ~1200×630 — will crop/letterbox); gate is an
  `aria-modal` dialog with **no Escape-to-dismiss** (mouse/CTA only). Minor.

## New defects this round

- **R8-A — `/api/players` 45.0s / 3.7 MB, worst across 4 rounds** (R5 19.2s → R6 23.4s → R7 12.2s
  → R8 45.0s). It now beats the client's own 30s ceiling + retry (guaranteed 2×45s failure path)
  and the 25s typeahead abort. First-visit Players tab = skeleton → full-page error; first search
  = "timed out". The cold-index copy (L531) only fires when the client *knows* the index is cold.
  This is server debt (gzip/paginate/warm), but it is the product's front door this round.
- **R8-B — League "Top Scorers" rows are dead links on live data**: L2509-2510 emits
  `tr.link` + `span.link` + `onclick="selectPlayer('${p.team_id}','${p.player_id}')"` while the live
  `/api/league` payload ships `player_id: null` on every row — `selectPlayer` (L2570) no-ops on
  falsy id. Link affordance, zero response: the exact inverse of "every tap answers." Same shape
  in `leaderSection` (L277). Live-confirmed, not hypothetical.
- **R8-C** — the 2 raw `${data.error}` sites above (the un-fixed half of R7-A).
- **dataStamp semantic fib, 4th round**: L2905-2906 still prints `new Date()` page-load time as
  "UPDATED HH:MM" (R5→R8 carry).
- Payload note: `/api/teams` (253 rows) still ships "Bye Week" (Thursday C North) and "Team
  Blue"/"Team Red" (Daytime League) — reachable through team-search typeahead; Today/League
  views are clean (Today payload scan: no placeholder tokens).

## The 10 dimensions

| # | Dimension | Evidence (what I saw) | Score |
|---|---|---|---|
| 1 | Visual identity (12%) | The identity story is now complete end-to-end: real league crest (vector-rebuilt, vision-verified professional) on the gate, header brand, favicon, apple-touch, manifest, OG/twitter — first-touch brand moment the R7 report said was missing. Gate echoes the rink-lines watermark; broadcast stack (Saira numerals, mono eyebrows, night KPI band, by-rink groups) intact on both themes. Residual: gate backdrop is competent-but-generic radial glows; in-app watermark still whisper-level. | 9.6 |
| 2 | Typographic system (12%) | Census 8 distinct literal sizes (13/14/16/18/20/26/30/34) vs 82 `var(--*)` uses; landing.css is fully tokenized (`--mono-sm/xs`, display face, `text-wrap:balance/pretty`); gate hierarchy logo→display title→mono kicker is on-system. Stragglers: the 13px×19 body scatter (R7 carry, mostly muted meta) and two inline-styled headings (L1489, L277) keep it under the gate. | 9.5 |
| 3 | Color system (10%) | Last standing sub-AA item closed: rink-head `#4a9ae6` 6.20:1 on panel (2-round carry dead). New surfaces computed clean: CTA 5.39:1 (large-text AA, hover 4.13:1 ≥3:1), sponsor hover 6.68:1, gate-sub 7.15:1. Accent discipline intact (red = live/interactive only; wins green; sponsor gold quarantined to hover states). | 9.6 |
| 4 | Layout & hierarchy (12%) | Gate is a clean single-column hierarchy with balanced wrapping; Today marquee order preserved with sponsor strip correctly last; hasOpp guard kills the blank-card path (live-validated against today's empty-opponent payload); R7-A defect dead. All-zero standings remain truthful; playoff cut-line self-resolves (cutoff 6 of 6 = no mid-table line). | 9.6 |
| 5 | Density & data presentation (12%) | Sticky theads, zebra+hover, sortable th with arrows, tnum numerics, race badges, scrim rows muted — all re-verified. `/api/today` payload clean (2 real games, zero placeholder tokens). Dents: dataStamp fib 4th round; players payload 3,925 rows all-zero points (truthful but flat — no zero-season framing on the leaderboard itself). | 9.4 |
| 6 | Interaction & micro-feedback (10%) | Gains: 40s watchdog + debounced retry (R7-4 race closed), cold-index honesty copy, gate CTA hover/active/focus states, focus moved post-enter. Losses this round: R8-B dead-link Top Scorers rows (affordance with no response, live-confirmed) and R8-A `/api/players` 45s beating every client ceiling — first Players visit and first search both terminate in error/timeout copy today. | 9.2 |
| 7 | Motion design (8%) | `hero-glow-breathe` retired (my R7 fix #3 — css:1236, zero refs). Remaining keyframes all purpose-traceable: live dot breathe (informational), score flash, shimmer=skeleton-only, entrance, pal-pop, spin, fade. RM coverage now extends to the gate (landing.css:172-174) on top of the 4 blocks + global kill. No decorative infinite animation remains in either stylesheet. | 9.7 |
| 8 | Depth & material (8%) | Gate-card on the ladder (`--panel`, hairline, one 24px/80px modal-elevation shadow — appropriate for a dialog, not a glow); sponsor banner inset+border-soft; crest alpha matted with no fringe (byte-verified); backdrop-filter still exactly 1 (palette scrim); print styles ×2. New surface adds material debt: none. | 9.6 |
| 9 | Consistency & component quality (8%) | Wins: `.section-h` finally exists (R5 proposal, 7 sites unified), `data-scrim` CSS hook shipped (R7-1 partial closed), focus-within parity, gate/sponsor components built entirely from tokens. Losses: esc discipline still skipped on 3 sites (R8-C), two new inline-styled headings, two-idiom debt intact (28 onclick / 43 inline style). The system's own rules are followed on new surfaces and still skipped on old ones. | 9.3 |
| 10 | Mobile ergonomics (8%) | All three R7-3 mobile carries closed: tonight-strip 2×2 (css:2111), small-button 44px floors (#themeToggle/#refreshBtn css:265), rink-head AA. Gate mobile-passes by construction: 479px pass, 52px CTA, 24px crown, overflow-y for short viewports, `viewport-fit=cover` + safe-area unchanged, 16px inputs. No new truncation surface. | 9.6 |

## WEIGHTED TOTAL

identity 9.6×12% + type 9.5×12% + color 9.6×10% + layout 9.6×12% + density 9.4×12% +
interaction 9.2×10% + motion 9.7×8% + depth 9.6×8% + consistency 9.3×8% + mobile 9.6×8%
= 1.152 + 1.140 + 0.960 + 1.152 + 1.128 + 0.920 + 0.776 + 0.768 + 0.744 + 0.768
= **9.5 / 10** (unrounded 9.51)

Lineage: R3 7.3 → R4 8.4 → R5 8.4 → R6 8.8 → R7 9.4 → **R8 9.5**. All 3 of my R7 fixes verified
in the deployed bytes (one partial), the two-round rink-head carry closed, and the gate/sponsor
surfaces shipped on-system rather than as a one-off page — that is why the round advances despite
interaction dropping 0.3 on live-confirmed defects. Per-dimension 9.7 gate: motion passes; eight
dimensions sit 9.4–9.6; interaction (9.2) is the drag.

## The 3 cheapest fixes toward 9.7-per-dimension

1. **Escape the last 3 raw error interpolations.** `app.js:2306` and `:2317`
   (`${data.error}` → `${esc(data.error)}`) and `:2446` (`${esc((data||{}).error || 'No data')}`).
   Three one-word edits; closes the R7-A class everywhere and kills the last scraper-internals
   paint path (live-observed 502 bodies in R7). **Δ consistency 9.3→9.5, credibility leak closed
   (weighted +0.016).**
2. **Stop rendering dead links.** In the League Top Scorers emitter (L2509) and `leaderSection`
   (L277): when `p.player_id` is null, drop the `tr.link`/`span.link`/onclick and render a plain
   row — or gate the table behind the GD-empty honesty pattern ("Player profiles unlock when
   stats post"). ~6 lines. **Δ interaction 9.2→9.4 (weighted +0.020).**
3. **Fix the dataStamp fib (4th round carry).** Print the payload's own fetched-at/serve time
   (one field on `/api/today`, one render line at L2905) instead of `new Date()` page-load time.
   "UPDATED" should mean data age, not session age. **Δ density 9.4→9.6 (weighted +0.024).**

Ceiling with all three: ≈ 9.57 weighted. The residual gap to 9.7-per-dimension is server-side:
`/api/players` 45s/3.7MB (gzip + paginate + guarantee the cron warm — client ceilings cannot
absorb it), the interaction-idiom unification (28 onclick / 43 inline style), and preseason
thinness (all-zero standings/points), which the design now frames honestly almost everywhere.

## Residual credibility risks (static-verification limits)

- `/api/players` latency is the product's worst user-visible fact and moves round to round
  (12.2s → 45.0s); measured once this round, not burst-tested (single-shot, 60s budget).
- Gate a11y: `aria-modal` dialog without Escape handling or focus trap — keyboard users get
  Tab-into-page-behind behavior unverified without a rendered browser (static).
- OG image 512×512 (platform-optimal is ~1200×630) — unverified how platforms crop it.
- (static) No rendered-pixel verification under the no-Chrome constraint; contrast figures are
  computed from tokens, asset quality from byte-level PNG/SVG decoding + image analysis of the
  fetched files.

VERDICT: 9.5/10
