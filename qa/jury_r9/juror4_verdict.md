# JURY R9 — 4/5 (INTERACTION LENS) — v67, Chrome-free — VERIFY-AND-SCORE

Method: byte-audit of deployed `app.js?v=67` (156,937B), `style.css?v=67` (88,795B),
`landing.css?v=67` (8,928B), index.html (13,161B), fetched 2026-09-04 ~15:50–16:07 ET via
urllib. Version triad in sync: JS_VERSION 67 (app.js:32) = APP_VERSION 67 (index) = `?v=67`
on all three assets; `/api/version` → `{"js":67}` (0.78s). **This round I diffed v67 against
my own saved v63 deployed copies** (qa/jury_r8/deployed/) — every score delta below traces to
an enumerated diff hunk (+44/−29 app.js, +14/−7 style.css, +153/−107 landing.css), not to fix
logs. No browser automation, no git. ~20 greps, 8 section dumps, 7 timed API probes, WCAG math
on 14 pairs. Evening puck drop not yet reached at probe time (16:07 ET; 7:40/8:50 PM games),
so LIVE pulse / score flash / countdown behavior remain byte-verified against a real populated
slate (Brewskies vs Trash Pandas 7:40 PM, Chiller Dublin), not watched moving.

## Verification of my R8 citations in deployed v67 — 5 of 5 FULL (first sweep in 9 rounds)

| R8 citation (qa/jury_r8/juror4_verdict.md) | v67 status |
|---|---|
| (1) 5 raw error sites esc()'d — 0 raw `${data.error}`/`${e.message}` remain | **FIXED (FULL)** — census: 0 raw hits, 11 esc'd paint sites (L1051, 1300, 1471, 1637, 1704, 1942, 2008, 2013, 2317, 2328, 2354). All 5 I named in R8 (Players L2306/2317→now 2317/2328, Analytics L2446→now 2457, e.message L1635/1702→now 1637/1704) escaped in-place. The 2-round error-anatomy split is CLOSED. |
| (2) palette spinner inside an RM block | **FIXED** — css L1217: `.pal-ov .spinner` appended to RM block 1's `animation: none !important` list. The last unguarded keyframe consumer is gone. |
| (3) cold-copy widened to real ceiling | **FIXED** — app.js:533 `Index cold — first search can take up to ~30s, then it's instant…` in the same correctly-gated branch (fires only while `allPlayersLoading || !allPlayers.length`, L530). My measured warm `/api/players` this round: 21.6s — inside the promise. |
| (4) Team watchdog migrated to shared helper | **FIXED (FULL)** — inline 8s/20s pair deleted (diff-confirmed), L1989 `armSkeletonWatchdog($('#teamContent'), 'your team', …)` with the R8-2 migration comment (L1987-88). Helper L1435-1459: wd8 8000ms nudge → wd40 **40000ms** > api's 30s ceiling, `data-wd-retry` + `data-retrying` 3s debounce + disabled 'Retrying…' (L1449-1453), re-fires over `.empty` nudge (L1445). All 3 lazy sections wired: League 1464, **Team 1989**, Analytics 2446; `disarm()` in finally (1469, 2223). **Bonus: my R8 comment-drift nit fixed** — L1437 now reads "(40s) must exceed api()'s 30s ceiling + retry-once". |
| (5) dataStamp ticks every minute | **FIXED** — L2919-2923: `paintStamp()` + `setInterval(paintStamp, 60000)` with the "R8: 4-round carry closed" comment. Closed after 6 rounds of carry. Residual honesty nit: it still paints *render* time, not data age — the fib is now a *ticking* fib. Noted, not scored as a regression (the carry as cited is closed). |

Also verified still-true: hashchange + re-entrancy guard, boot-hash-read-before-setTab (L2929),
180ms typeahead debounce + stale clear, api() 30s ceiling + retry-once (L885-885 region),
palette input 16px, `window.loadTeamContent` direct binding, gate sessionStorage skip (L11-16).

## New finds this round

1. **R8-A (R8-5's convergent find) shipped**: dead-team self-heal (app.js:1999-2015) — a saved
   team whose upstream page is gone matches `/no longer available/i`, clears `state.teamId` +
   localStorage, re-renders the picker with a hint. No more permanent dead-end.
2. **R8-B (R8-5's convergent find) shipped**: leaders dead links guarded — diff shows all 3
   leader tables now emit `p.player_id ? onclick="selectPlayer(…)" : ''`. Link affordance with
   zero response is dead. (Convergent fixes from other jurors now get the same byte treatment
   as my own citations — verified, not credited on log claims.)
3. **The gate grew into a full landing page** (landing.css 6,510→8,928B): sticky nav + hero +
   features grid + about + sponsor section + footer, all 3 CTAs (nav `gateEnter` L56 / hero
   `gateEnterCta` L63 / footer `gateEnterFoot` L115) wired to ONE `gateDismiss` (app.js:17-27)
   → sessionStorage `cahl-entered` → hide→500ms→remove→`#main.focus()`. Both external links
   carry `rel="noopener"` (sponsor L104, ChillerStats L116). Session-skips before first paint.
   Circuit audit: zero keyframes, transitions-only, RM block L218-220 covers all 6 transition
   surfaces; focus-visible present on nav links, CTA, sponsor card. **Costs: (a) 2
   backdrop-filters (nav blur 10px ×2 prefixes) where v63's gate had zero and my depth note
   said "no new blur"; (b) `.lp-cta-sm` min-height:42px — 2px under the 44px floor my lens
   polices; (c) CTA hover state = white on `--union-hover` #3a8fe0 = 3.40:1 (AA-large only for
   the 19px bold label; idle state is 5.39:1).**
4. **R8-1's sponsor-gold find addressed in-system**: new tokens `--union-cta: #1f6cb8` +
   `--sponsor-gold` with a light-theme override `#7a5c2e`. Measured: gold #b8925e 6.42:1 dark
   panel / 6.86:1 bg; **#7a5c2e 6.18:1 on white / 5.66:1 on panel-2** — both themes AA. The
   R8-1 carry is closed with a real token, not a hardcode. `.lp-f-icon` still carries a
   `#b8925e` fallback — harmless (token defined in both themes).
5. **R8-2's sticky-context diagnosis fixed at the mechanism**: `card:has(table)` max-height
   replaced by `.card:has(table) table { display:block; max-height:65vh; overflow-y:auto }`
   (css:2110-2115) — the scroll container is now the table itself, so sticky th can engage.
   The invisible `::after` fade was deleted with it.
6. **/api/players warm-state re-measured: 21.6s, 3.17MB decoded, 3364 players** (single-shot,
   this round). The brief's "5959 players / 11.8s warm" was NOT the state I observed — my
   number is the honest one for this round; still inside the new "~30s" copy band and under
   the 30s api() ceiling, so the interaction contract holds, but the payload is the standing
   density carry. All other endpoints fast: version 0.78s, today 1.43s, scores 1.92s, leaders
   1.40s, league 0.85s, lookup 0.80s. Payload hygiene: 0 Bye-Week/Team Blue/Team Red rows.
7. `.section-h.tight` variant added (css:441) and used by the new Session records heading —
   the section-head idiom is being extended, not bypassed.

## Dimension table

| # | Dimension | Evidence (one line) | Score |
|---|-----------|--------------------|-------|
| 1 | Visual identity | Landing page now tells the league's story end-to-end (nav→hero→features→sponsor) in CBJ hues; broadcast grammar (LIVE chip, rink lines, mono kickers) intact; signature data-viz moment still absent — ceiling unchanged | 8.9 |
| 2 | Typographic system | Zero font-size literals in app.js holds (re-census); landing copy stays on Saira/JetMono + mono tokens (lp-links/lp-h2/kicker); lp-title 44px/800 display scale is on-system; residual = lp-f-icon 11px + lp-note 12.5px literals on the new surface | 9.0 |
| 3 | Color system | Sponsor gold tokenized BOTH themes (6.42/6.18:1 — R8-1 carry closed); CTA tokenized --union-cta 5.39:1; rink-head AA holds; residual = CTA hover 3.40:1 + 23 union-alpha literals + pal-item selection ring | 9.4 |
| 4 | Layout & hierarchy | Landing sections scan in order (nav→hero→features→about→sponsor→footer); watchdog contract now uniform on all 3 lazy sections; dead-team self-heal removes the last permanent dead-end; real slate renders clean | 9.2 |
| 5 | Density & data presentation | R8-B dead links guarded in all 3 leader tables; tnum/zebra/sticky/sortable hold; leaders payload real and linked; /api/players 21.6s + 3.17MB remains the standing backend carry | 8.9 |
| 6 | Interaction & micro-feedback | Every tap resolves: 5/5 esc census clean, uniform watchdog (8s/40s/debounced retry) on League+Team+Analytics, cold-copy honest vs 21.6s measured, retry chips, toasts, gate CTAs share one tested code path, self-heal re-renders picker | 9.5 |
| 7 | Motion design | RM coverage: JS count-up gate + 3 CSS blocks + landing.css block (all 6 transition surfaces) + pal spinner; zero unguarded keyframe consumers left; landing adds zero keyframes (transitions only) | 9.5 |
| 8 | Depth & material | App census: single justified blur (palette 3px); BUT landing nav ships backdrop-filter blur(10px) ×2 — the one material rule the new surface broke; everything else luminance-stacked, hairline borders, no shadow soup | 9.0 |
| 9 | Consistency & component quality | Error-card anatomy unified (11/11 esc'd); gold/CTA pulled into tokens both themes; section-h idiom extended (.tight); landing reuses gate-cta/lp tokens instead of new vocab; residual = lp-f-icon fallback hex + keyframe rgba literals | 9.3 |
| 10 | Mobile ergonomics | ≤430 landing CTA 50px; app 44px floors hold; BUT lp-cta-sm 42px (2px under floor, nav CTA is a real control); lp-title 27px at 430px scales cleanly; sticky-nav blur is a scroll-perf tax on old phones | 9.0 |

**WEIGHTED TOTAL: 9.2/10** (9.154 exact; lineage 8.1 → 8.4 → 8.6 → 8.9 → 9.0 → **9.2** —
largest single-round jump since R4→R5, powered by the first 5/5 citation sweep)

## 3 cheapest fixes toward 9.7-per-dimension

1. **Kill the landing nav blur + fix the 42px CTA** — delete the two backdrop-filter lines
   (landing.css:44-45; `color-mix` bg at 82% already does the work — solid var(--panel-2)
   would be indistinguishable and free), and raise `.lp-cta-sm` min-height 42→44px
   (landing.css:59). 3 deleted/edited lines. **delta ≈ +0.2 depth (9.0→9.2), +0.1 mobile
   (9.0→9.1), +0.1 identity ≈ +0.045 total.**
2. **Fix the CTA hover contrast the token way** — `--union-hover` #3a8fe0 gives white-on-hover
   3.40:1; add a darker hover for filled CTAs (`--union-cta-hover: #1a5fa3` ≈ 6.0:1, one
   token + one rule landing.css:105) or swap hover to keep bg and lift border/shadow
   instead. **delta ≈ +0.2 color (9.4→9.6), +0.1 consistency ≈ +0.03 total.**
3. **Token the last literals on the new surface** — lp-f-icon 11px→var(--mono-xs), lp-note
   12.5px→var(--mono-sm), lp-f-icon fallback #b8925e→bare var(--sponsor-gold); swap
   hero-next-pulse's rgba(42,127,212) stops (css:1282-84) for the sponsor/union token
   (2nd-round carry). ~6 tokens. **delta ≈ +0.1 type (9.0→9.1), +0.1 color, +0.1
   consistency ≈ +0.03 total.**

Projected combined ≈ 9.26. The 9.7-per-dimension gate remains blocked where patches can't
reach: identity 8.9 needs the signature data-viz moment (6th round saying so), density 8.9
needs /api/players fixed server-side (3.17MB / 21.6s is a backend number), depth 9.0 and
mobile 9.0 are one cheap pass away each (fix #1), interaction 9.5 and motion 9.5 are within
one honest pixel of the gate and are the two dimensions closest to 9.7 on the board.

## Score honesty check

- 9+ means no defect findable at effort: every 9+ dimension above carries a cited residual
  (blur, 42px, 3.40:1, 21.6s payload, render-time stamp). No dimension reaches 9.7.
- Every score delta vs my R8 table traces to an enumerated diff hunk: color +0.2 (gold/CTA
  tokenized both themes, measured), interaction +0.2 (esc census closed + watchdog uniform +
  self-heal + honest copy), motion +0.1 (pal spinner RM'd, landing zero keyframes),
  consistency +0.3 (11/11 unified anatomy + token discipline on new surface), layout +0.2
  (dead-end removed + landing structure), identity +0.2 (landing tells the story), type +0.1
  (on-system landing, literals capped at 2 new), density +0.1 (dead links guarded; payload
  carry caps it), depth +0.1 (net: token/material discipline up, nav blur down), mobile +/−0.0
  (50px CTA up, 42px lp-cta-sm down — called it a wash, cited both). No delta lacks a
  byte-level cause; no fix credited on log claims.
- Timing labels: all timings this round are my own single-shot probes, labeled per-call; the
  brief's 11.8s warm number did not reproduce for me (21.6s) and I scored my own measurement.
- LIVE-state caveat unchanged from R8: byte-verified against a real populated slate, not
  watched moving (games start 7:40 PM ET; probes ran 15:50–16:07 ET).

VERDICT: 9.2/10
