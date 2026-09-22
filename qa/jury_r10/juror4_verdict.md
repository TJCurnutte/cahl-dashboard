# JURY R10 — 4/5 (INTERACTION LENS) — v70, Chrome-free — VERIFY-AND-SCORE

Method: byte-audit of deployed `app.js?v=70` (157,005B), `style.css?v=70` (88,845B),
`landing.css?v=70` (8,892B), index.html (13,161B), fetched 2026-09-04 16:47–17:05 ET via
urllib. Version triad in sync: JS_VERSION 70 (app.js:32) = APP_VERSION 70 (index) = `?v=70`
on all three assets; `/api/version` → `{"js":70}` (1.65s). Every score delta below traces to
an enumerated diff hunk against my own saved v67 deployed copies (qa/jury_r9/deployed/):
+68B app.js, +50B style.css, −36B landing.css — the smallest patch since R7, and every hunk
is a jury fix, not a feature. No browser automation, no git. ~25 greps, 6 census scripts,
4 timed probe rounds (single-shot + 5-burst). LIVE-state caveat unchanged: probes ran
16:47–17:05 ET vs 7:40/8:50 PM games — motion surfaces remain byte-verified, not watched.

## Verification of my R9 citations in deployed v70 — 4 of 4 FULL (2nd consecutive sweep)

| R9 citation (qa/jury_r9/juror4_verdict.md) | v70 status |
|---|---|
| (1) landing nav blur (backdrop-filter 10px ×2) | **FIXED (FULL)** — landing.css:43 `background: var(--bg); /* R9-4: nav blur removed — backdrop-filter budget stays with the app */`; `grep backdrop-filter landing.css` → 0 hits (comment line only). App census: single justified blur remains (palette scrim 3px, style.css:765). |
| (2) `.lp-cta-sm` 42px | **FIXED (FULL)** — landing.css:57 `min-height: 44px`. Landing's only remaining sub-44 control floor is gone. |
| (3) CTA hover `--union-hover` darkened | **FIXED (FULL)** — style.css:35 `--union-hover: #2b71c4` (comment: "R9-4 darkened: 4.6:1 with white label"); landing.css:103 consumes the var. **My measurement: 4.93:1** (white on #2b71c4) — the fix comment's "4.6:1" is conservative, actual is better. Light theme rides `--union-hover-deep` #0d3a73 = **11.23:1**. Old value was 3.40:1. |
| (4) lp-f-icon 11px / lp-note 12.5px / #b8925e fallbacks | **FIXED (FULL)** — landing.css:130 `font-size: var(--mono-sm)` + bare `var(--sponsor-gold)` (4 uses); lp-note/lp-fine 12.5px→13px. **Off-scale literal census: 12 distinct sizes → 7 (13/14/16/20/26/30/34)**; off-token hex census: 1 literal left in the whole file (#ffffff border). |

Also verified still-true: palette input 16px (anti-iOS-zoom, style.css:787), RM blocks 3+
landing block (all 6 transition surfaces), zero keyframes in landing.css, spinner in RM
block 1, dataStamp paintStamp+setInterval(60000) (L2919-23), esc census 0 raw
(8 data.error + 3 e.message, all esc'd), api() 30s ceiling + retry-once, watchdog wd40
40s > 30s ceiling, gate sessionStorage skip. Release-gate grep (`min-height/width:0` inside
@media blocks): 6 hits, all pre-existing flex text-truncation guards (`min-width:0` on
overflow:hidden containers — correct usage), none on interactive controls; landing.css 0.

**Convergent carries verified too (byte-checked, not log-credited):** R9-3's 3rd-round
`.pal-input-row:focus-within` ring shipped (style.css:783, inset 0 0 0 2px var(--union));
R9-5's two-sponsor-marks find shipped (app.js:1239 Today strip now `upright-lockup.png`,
0 crown refs; asset live, 242,816B).

## THE BIG ONE: /api/players persistence — verified live, mechanism changed

The briefed Supabase/PostgREST persistence is **server-side by design** (client app.js has 0
supabase/postgrest/hydrate/snapshot refs — correct: persistence shouldn't ship in the bundle).
What I can verify is the user-facing contract, and it moved more this round than any round
since R5:

| Probe (16:53–17:05 ET) | v70 measured | R9 my measurement | All-time worst |
|---|---|---|---|
| single-shot /api/players | **6.97–8.59s** | 21.6s | 45.0s (R8-A) |
| 5-burst parallel | 6.05–22.69s wall 22.69s | 30–34s (R9-1) | — |
| payload decoded | 5.52MB / 5,862 players | 3.17MB / 3,364 | 5.6MB (R8-2) |

The response also ships a **new `{partial, players}` envelope**: burst runs 3–5 and 2–5
returned `partial:true` with ~2,100 rows at ~22s while 3/5 served the full 5,862 — the
index build no longer blocks the response. The client (app.js:325-358) handles it
correctly: parses `data.players` from either shape, auto-retries up to 4× on partial,
renders "X players (still loading N of M)" in the picker (L675). First-search cold copy
(app.js:533, "up to ~30s") stays correctly gated on `allPlayersLoading || !allPlayers.length`
and now over-promises rather than under-promises against measured reality — the honest
direction.

**Residuals:** (a) 5.52MB decoded for 5,862 players is a standing backend carry — first
paint of the Players tab on cell still hurts; (b) **new find: `/api/players/lookup?q=` timed
37.35s single-shot** — beats the Players-tab typeahead's own 40s controller only barely and
the shared "up to ~30s" copy not at all; lookup carries its own copy path ("No players
match. Index still filling — tap to retry", L551-552) so the interaction contract holds via
retry affordance, but 37s for a search is the worst number on the board this round. (c)
Bare 404 on `/api/league` without id — cosmetic, not user-reachable (client always appends
an id).

## New finds this round

1. **`/api/players/lookup` 37.35s single-shot** (above) — new worst-endpoint champion;
   the 22s index fetch it used to punt to now answers in 7-9s while lookup didn't improve.
2. **partial-envelope burst honesty**: 2/5 burst responses ship ~2,100 rows `partial:true`
   at ~22s — the retry + progress copy makes this a *designed* state, not a race.
3. **Landing type-scale consolidated, not just retokened**: the v67 fork (12 sizes incl.
   11/12.5/13.5) collapsed to 7 sizes aligned with the dashboard's body scale (13/14/16px)
   plus display steps — the "new surface mints parallel scale" defect class is now closed
   at the source, not patched over.
4. **Off-token hex census landing.css: 1 literal** (#ffffff) — from 7 (3 × #b8925e
   fallbacks, #3a8fe0, union-cta fallback, gold fallback, white). Token discipline on the
   new surface is now equivalent to the app's.
5. `.rink-head` light-theme rule (8.79:1 via --union-deep) present in BOTH v67 and v70 —
   the diff hunk I first read as a deletion was insertion-positioning noise (782a783
   shift). R7-3's 2-round contrast carry confirmed closed; no regression.

## Dimension table

| # | Dimension | Evidence (one line) | Score |
|---|-----------|--------------------|-------|
| 1 | Visual identity | Landing tells the league story in CBJ hues (nav→hero→features→sponsor), broadcast grammar intact (LIVE chip, rink lines, mono kickers); signature data-viz moment still absent — ceiling unchanged, 7th round saying so | 8.9 |
| 2 | Typographic system | app.js zero literals holds; landing scale consolidated 12→7 sizes, lp-f-icon on --mono-sm token; dashboard scale pristine (8 sizes, all commented intent) | 9.2 |
| 3 | Color system | Hover now 4.93:1 dark / 11.23:1 light (was 3.40); landing hex census down to 1 literal (#ffffff); sponsor-gold + union-cta tokens both themes hold; residual = 23 union-alpha literals in style.css + pal-item ring | 9.5 |
| 4 | Layout & hierarchy | Landing sections scan in order; watchdog uniform on all 3 lazy sections; partial-index state renders progress in-picker instead of dead-ending; leaders/link anatomy clean | 9.2 |
| 5 | Density & data presentation | tnum/zebra/sticky/sortable hold; live /api/leaders 15/15 rows carry player_id (0 nulls); lookup guard + ?? '-' census 12+12; /api/players 6.97-8.59s single-shot (was 21.6s) — payload 5.52MB remains the backend carry | 9.2 |
| 6 | Interaction & micro-feedback | Every tap resolves: index fetch 7-9s vs 22s abort (headroom, was coin-flip at 21.6s); partial envelope auto-retries 4× with honest copy; cold-copy over-promises vs measured; 0 raw esc sites; lookup 37.35s is the one open sore (covered by retry affordance, not the clock) | 9.6 |
| 7 | Motion design | RM coverage: JS count-up gate (matchMedia L799) + 3 CSS blocks + landing block (6 surfaces) + spinner + palette focus ring (no motion); zero keyframes in landing.css; hero-next-pulse rgba(42,127,212) literals remain the 2nd-round carry | 9.5 |
| 8 | Depth & material | App census: single justified blur (palette 3px); landing blur deleted per citation; luminance-stacked panels, hairline borders, no shadow soup anywhere — the R9 material violation is gone | 9.2 |
| 9 | Consistency & component quality | Landing now consumes --mono-sm/--sponsor-gold/--union-cta/--union-hover bare (0 fallback hexes except 1 white border); lockup unified across Today + landing; section-h idiom intact; scorecell anatomy holds | 9.5 |
| 10 | Mobile ergonomics | lp-cta-sm 44px floor restored; ≤430 CTA 50px; release-gate grep clean (0 sub-44 interactive floors); palette input 16px; residual = 5.52MB index on cell + no nav-row card fallback on 390px tables | 9.1 |

**WEIGHTED TOTAL: 9.3/10** (9.274 exact; lineage 8.1 → 8.4 → 8.6 → 8.9 → 9.0 → 9.2 → **9.3** —
steady climb continues; 4/4 citation sweep for the 2nd consecutive round, plus 2 convergent
carries from other jurors verified shipped)

## 3 cheapest fixes toward 9.7-per-dimension

1. **Fix /api/players/lookup latency server-side (mirror the players-index path)** — the
   index endpoint dropped 45s→7-9s via the persistence/single-flight work; lookup still
   measures 37.35s and beats the client's shared "~30s" copy. Same treatment (cache the
   token→player resolution, or resolve against the persisted index instead of re-crawling)
   is one endpoint of work. **delta ≈ +0.2 interaction (9.6→9.8 gate met), +0.1 density
   ≈ +0.032 total.**
2. **Shrink the players payload** — 5.52MB decoded for 5,862 rows is the last density
   blocker; drop unused per-player fields (the row objects carry ~20 keys; the typeahead
   and leaderboard consume ~8) or add field-select to the response. Halving it moves both
   the Players tab first paint and mobile cell experience. **delta ≈ +0.2 density
   (9.2→9.4), +0.1 mobile (9.1→9.2) ≈ +0.032 total.**
3. **Token hero-next-pulse's rgba stops + the 23 union-alpha literals** (2nd-round carry)
   — swap the three `rgba(42,127,212,α)` keyframe stops (style.css:1283-85) for
   color-mix over var(--union) and census the union-alpha literals in style.css. Pure
   token hygiene, ~24 declarations. **delta ≈ +0.1 motion (9.5→9.6), +0.1 color
   (9.5→9.6) ≈ +0.016 total.**

Projected combined ≈ 9.33. The 9.7-per-dimension gate is now blocked by exactly three
things my lens can name: identity 8.9 (signature data-viz moment, 7th round), the lookup
endpoint's 37s (fix #1), and the 5.52MB payload (fix #2). Everything else on the board is
within one cheap pass of 9.7.

## Score honesty check

- 9+ means no defect findable at effort: every 9+ dimension above carries a cited residual
  (identity's missing signature viz; type's landing display steps outside tokens; color's
  union-alpha literals; density's 5.52MB; interaction's 37s lookup; motion's keyframe
  literals; depth's single justified blur; consistency's 1 white-border literal; mobile's
  payload-on-cell). No dimension reaches 9.7.
- Every score delta vs my R9 table traces to an enumerated diff hunk or a live probe:
  type +0.2 (landing scale consolidated 12→7 + lp-f-icon tokenized), color +0.1 (hover
  4.93/11.23:1 + hex census 7→1), density +0.3 (index 21.6→7-9s live-measured + leaders
  0/15 null player_id), interaction +0.1 (headroom on 22s abort + partial-envelope honesty;
  capped by lookup 37.35s), depth +0.2 (landing blur deleted), consistency +0.2 (0 fallback
  hexes + lockup unified), mobile +0.1 (44px floor + clean release-gate grep). Layout,
  identity, motion unchanged — no hunks touched them. No delta lacks a byte-level cause.
- The two R9 residuals I said patches couldn't reach were both reached this round:
  depth/mobile 9.0→9.2/9.1 via fix #1 (blur+44px), and density's timing half via the
  persistence work. Identity's signature-viz ceiling and the payload megabytes remain the
  honest blockers.
- Timing labels: every timing above is my own probe, labeled single-shot vs burst, warm
  as-found (index was warm at 16:53; burst ran immediately after). The brief's Supabase
  claim is verified at the contract level (latency + envelope + client handling), not at
  the infrastructure level — 0 client refs is the *correct* shape for server persistence,
  and I say so explicitly rather than claiming to have verified Supabase itself.
- LIVE-state caveat unchanged from R9: byte-verified against a real populated slate, not
  watched moving (games start 7:40 PM ET; probes ran 16:47–17:05 ET).

VERDICT: 9.3/10
