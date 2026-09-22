# JURY R8 — 4/5 (INTERACTION LENS) — v63, Chrome-free — VERIFY-AND-SCORE

Method: byte-audit of deployed `app.js?v=63` (156,017B), `style.css?v=63` (88,121B), index.html
(9,964B) and **landing.css?v=63 (6,510B — the new v62 gate surface, audited this round)**, fetched
2026-09-04 ~15:05–15:25 ET via urllib (`/static/` paths). Version triad in sync: JS_VERSION 63
(app.js:30) = APP_VERSION 63 (index:151) = `?v=63` on all three assets; `/api/version` → `{"js":63}`.
No browser automation, no git. ~30 greps + 12 section dumps + 7 timed API single-shots + WCAG math
on 8 pairs. **The zero-data caveat is gone**: /api/today returned a real 2-game slate (Brewskies vs
Trash Pandas 7:40 PM, Whalers vs Stepbros 8:50 PM) with 0 Bye-Week/Team-Blue/Team-Red rows — payload
hygiene verified on live data (evening puck drop not yet reached at probe time, so LIVE pulse/score
flash remain byte-verified, not pixel-verified). Timings: /api/version 1.08s, /api/today 1.74s,
/api/today/scores 1.24s, /api/league/<128-char real id> 1.86s, /api/leaders 1.65s,
**/api/players 32.1s (1.55MB gzip) — trend 10.3 → 19.2 → 23.4 → 26.9 → 32.1s, now ABOVE the app's
own 30s api() ceiling and above the typeahead's promised "10–25s" band.**

## Verification of R7-cited fixes in deployed v63 bytes — 3 of 4 FULL, 1 PARTIAL

| R7 citation (my verdict, qa/jury_r7/juror4_verdict.md) | v63 status |
|---|---|
| (1) cold-index copy in renderPlayerTypeahead | **FIXED** — app.js:531 `Index cold — first search takes 10–25s, then it's instant…` (real em-dash/en-dash/ellipsis escapes, muted typeahead item, comment credits R7-4). Wired in the right branch: fires only while `allPlayersLoading \|\| !allPlayers.length` (L528) — the actual cold-index state |
| (2) armSkeletonWatchdog reconciled: wd40 40s > api 30s, data-wd-retry + data-retrying debounce + 'Retrying…' | **FIXED** — app.js:1442-1455 `wd40` at **40000ms** (> 30s ceiling, comment L1436 documents the contract); retry button `data-wd-retry` (L1444), double-tap debounce `data-retrying` (L1447-1448, 3s window L1451), `btn.disabled = true; btn.textContent = 'Retrying…'` (L1449-1450); wd40 correctly re-fires after the 8s "Still loading…" nudge (condition covers `.empty` first-child, L1443). Wired League (L1462) + Analytics (L2435), `disarm()` in finally both sites. **NIT: stale fix-comment** — L1435 says "25s" while the code correctly uses 40s |
| (3) hasOpp guard on team-page recent_result | **FIXED** — app.js:2100-2105 with the R7-5 comment; every recent_result consumer now guarded: hero L1364-1365, team L2104-2105, share-toast L2587 (`if (!r)` early-out) |
| (4) esc() on data.error in $main/$content error paints | **PARTIAL** — esc'd at L1298 ($main/today), L1469 ($content/league), L2004 (team), L2343 (player profile); **STILL RAW: L2306 + L2317 (Players-tab leader error paints — both are `$main` paints via setMainHtml), L2446 (Analytics `$main`)**, plus L1635/L1702 raw `${e.message}` into `$sec` error cards. The cited class ($main/$content) is only half-migrated — 3 of 6 $main sites remain unescaped |
| window.loadTeamContent = loadTeamContent (v59) | **HELD** — app.js:2548 direct binding + no-IIFE shadowing comment (2544) |
| api() 30s ceiling + retry-once (v58) | **HELD** — app.js:883 `setTimeout(() => ctrl.abort(), 30000)`; 2-attempt loop L892 with 700ms backoff, AbortError propagates immediately (L897), total ceiling intact |
| client-error telemetry | **HELD** — app.js:92-103: sendBeacon → `/api/client-error` with fetch-keepalive fallback, recursion-class filter + identical-error debounce (L90-91, 105-107) |

Also verified still-true from earlier rounds: hashchange listener + re-entrancy guard (app.js:998-1014),
boot-hash-read-before-setTab (2914-2916), 180ms typeahead debounce + stale clear (458-461), render-token
guard (1024-1030), autoToggle `:has` feedback (css:247-248), palette input 16px global, tab-error Retry
(L1025 region), dataStamp `new Date()` **carry persists** (app.js:2907 — page-load time still passed off
as data age).

## New finds this round

1. **Cold-copy promise is already falsifiable** — the new L531 copy promises "10–25s"; measured
   /api/players 32.1s (5th consecutive worsening round). The honest fix is server-side (1.5MB gzip
   payload, cap/paginate), but the copy band must widen to the real ceiling ("up to ~30s") or the
   product's first promised number is the first number a user can catch it breaking.
2. **My R7 cheapest-fix #3 was not shipped**: `.pal-ov.open` (pal-fade) + `.pal` (pal-pop) animations
   (css:760, 769) are still outside every RM block (verified by span-analysis of all 3
   prefers-reduced-motion blocks), and hero-next-pulse keyframes still hardcode
   `rgba(42,127,212,…)` stops (css:1273-1275, no --union-glow token). hero-next-dot IS RM-gated
   (RM block 2, L1288) — the gap is palette-only.
3. **Fix-comment drift**: wd40's comment says "25s", code says 40s. First drift between fix-annotation
   and fix-body; the R7-3 "verify the fix comments" census should include deadline numbers, not just
   `was Npx` type notes.
4. **v62 gate surface (landing.css) audited — clean**: CTA 52px min-height, AA 5.4:1 label, hover
   lift + active scale + focus-visible (3 rules), RM block for all gate transitions, zero
   backdrop-filters, zero keyframes, sessionStorage skip before first paint (no gate flash), CTA
   sets flag → hide → 500ms remove → `#main.focus()`. One product-level nit: the gate adds one
   click before any data on each session's first visit (deliberate, session-scoped — noted, not
   scored down; the CTA interaction quality is above the app average).
5. **R7-2's mobile claims landed**: tonight-strip `repeat(2,1fr)` in the ≤599 pass (css:2111),
   `button.small` 44px floor (css:2114). The ≤699 header block's `min-width:0` hits (css:1936-1943)
   sit on text containers (h1/brand-block/live-pill label), NOT controls — checked against the R2/R4
   regression class: tap floors on controls hold (1956/1961/2093/2114). Not a regression.
6. **R7-3's rink-head AA fix landed and measured**: `#4a9ae6` = 6.19:1 on panel, 6.62:1 on bg — the
   2-round sub-AA carry is closed. section-h idiom live (5 emission sites + css:437).
   hero-glow-breathe retired to static glow (css:1236) with a "needs no RM guard" comment (L1597).

## Dimension table

| # | Dimension | Evidence (one line) | Score |
|---|-----------|--------------------|-------|
| 1 | Visual identity | Watermark + LIVE grammar + hockey vocabulary intact; NEW branded front door (HD mark, sponsor strip, broadcast copy) raises the first impression; signature data-viz moment still absent — identity ceiling unchanged | 8.7 |
| 2 | Typographic system | Type census 14 → 8 literal sizes (16/13/20/14/26/30/18/34); ZERO font-size literals left in app.js; section-h unifies section heads; Saira+JetMono hrefs intact; gate display face on-system | 8.9 |
| 3 | Color system | Accent 5.13/4.80:1 dark, 5.63:1 light; rink-head 6.19:1 (2-round carry CLOSED); faint 6.18/5.13; hover tokens both themes; residual = hardcoded rgba(42,127,212) keyframe stops (1273-75) + 23 union-alpha literals | 9.2 |
| 4 | Layout & hierarchy | Watchdog contract reconciled (40s > 30s, debounced retry, wired League+Analytics); zero dead states; boot-hash order verified; real 2-game slate renders clean; residual = 32.1s players latency + gate's one extra click to data | 9.0 |
| 5 | Density & data presentation | tnum tables, zebra, sticky both axes, sortable+keyboard, scored-chip anatomy, players retry ladder ≤4; today payload hygiene verified on LIVE slate (0 bye/scrim rows); /api/players 1.5MB/32.1s remains the weak link | 8.8 |
| 6 | Interaction & micro-feedback | Every tap resolves: 30s ceiling + retry-once, watchdogs 8s ack/40s hard with disabled 'Retrying…' debounce, cold-copy expectations, retry chips, toasts, :has(:checked) pill, gate CTA full state stack; residual = 3 raw $main error paints + copy band (10–25s) already broken by 32.1s reality | 9.3 |
| 7 | Motion design | RM coverage now: JS count-up gate + 3 CSS blocks + landing.css block + breathe retired static + hero-next-dot gated; only unguarded motion = pal-fade/pal-pop (0.12–0.15s, palette) | 9.4 |
| 8 | Depth & material | Single justified backdrop-filter (palette blur 3px); luminance stack + hairlines intact; gate-card flat elevated in-system; light-theme gate shadow token-appropriate; no new blur/shadow soup from v62/v63 | 8.9 |
| 9 | Consistency & component quality | scored-chip/scrim/data-scrim/section-h/mono tokens in-system; gate components reuse token + focus-visible idioms; residual = error-paint anatomy split (6 esc'd vs 5 raw sites) + wd comment/code drift | 9.0 |
| 10 | Mobile ergonomics | Coarse 44px floors ×2 blocks + button.small 44px + tonight-strip 2×2 + ≤699 header wrap verified non-regressional; pal input 16px; gate CTA 52px; residual = 32.1s players wait on cell network (ack'd, no cancel affordance) | 9.1 |

**WEIGHTED TOTAL: 9.0/10** (9.01 exact; lineage 8.1 → 8.4 → 8.6 → 8.9 → **9.0** — first 9+ round)

## 3 cheapest fixes toward 9.7-per-dimension

1. **Escape the 5 remaining raw error paints** — `esc()` on `${data.error}` at app.js:2306, 2317,
   2446 and `${e.message}` at 1635, 1702. Six sibling sites already carry the pattern; this is the
   same one-token-per-site edit the R7-5 class requires, and it unifies the error-card anatomy.
   ~5 tokens. **delta ≈ +0.3 consistency (9.0→9.3), +0.2 interaction ≈ +0.05 total.**
2. **Make the cold-index promise unfalsifiable + close the palette RM gap** — widen app.js:531 to
   "up to ~30s" (or fix the 1.5MB payload server-side — the honest fix; cap/paginate), and add
   `.pal-ov.open, .pal` to RM blocks (2 selector lines). ~4 lines. **delta ≈ +0.2 interaction,
   +0.2 motion (9.4→9.6), +0.1 mobile ≈ +0.06 total.**
3. **Token the keyframes + fix the comment** — swap hero-next-pulse's rgba(42,127,212,…) stops
   (css:1273-75) for a `--union-glow` token, and correct the wd40 comment "25s"→"40s" (app.js:1435)
   so the fix-annotation audit trail stays truthful. ~4 lines. **delta ≈ +0.2 color (9.2→9.4),
   +0.1 consistency ≈ +0.03 total.**

Projected combined: ~9.15/10. The per-dimension 9.7 gate remains blocked by the dimensions patches
can't reach: identity 8.7 and depth 8.9 need a signature data-viz moment, density 8.8 needs the
players payload fixed server-side (32.1s is a backend number, not a UI number), type 8.9 needs the
last 8 literal sizes tokenized. Interaction (9.3) and motion (9.4) are within one cheap pass of the
gate; nothing else is.

## Score honesty check

- 9+ means no defect findable at effort: this round found 2 new systemic items (cold-copy promise
  vs 32.1s measured reality; fix-comment drift), 1 partially-shipped cited fix (esc class: 3 raw
  $main sites remain), 1 unshipped R7 fix (#3), 1 open 6-round carry (dataStamp render-time). No
  dimension reaches 9.7; five reach 9+ and each carries a cited defect. Evening games had not
  started at probe time — LIVE pulse, score flash, and By-Rink finals recovery are verified in
  bytes against a real populated slate, not watched moving.
- Score deltas vs my R7 table trace to byte changes: color +0.1 (rink-head AA closed), layout +0.1
  (watchdog contract reconciled), type +0.1 (census 14→8, section-h), interaction +0.1 (cold copy +
  retry debounce + Retrying state), motion +0.1 (breathe retired, gate RM'd), consistency +0.1
  (scrim/chip/section-h unification continues; raw-error split caps it), density +0.1 (real-slate
  hygiene verified), mobile +0.1 (small-button floor + 2×2 strip), identity +0.0, depth +0.1 (gate
  surface in-system). No delta lacks a byte-level cause; no cited fix was taken on trust.
- Every one of my R7 citations was re-checked at its live line number; the one partial (esc) is
  quoted with all 5 raw sites. Timings re-measured fresh this round, not carried.

VERDICT: 9.0/10
