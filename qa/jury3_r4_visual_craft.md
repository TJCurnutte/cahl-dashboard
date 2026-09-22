# CAHL UI/UX JURY — R4, Juror 3/5 (visual craft lens) — v54

Method: NO browser automation (owner directive + hard constraint). Prod fetch was consent-blocked
mid-round, so deployed-bytes verification uses the deployed CSS copy saved by juror 2
(`qa/r4_juror2_style.css`) — `diff -q` against local `static/css/style.css` at git 50979f7
("R4: rink-lines hero watermark … v54"): **byte-identical**. All findings below are from that
deployed-equivalent source (1,997 lines CSS, 2,100+ lines app.js, index head). No live paint this
round; dimensions that need a browser are marked (static).

History: R1 6.5 → R2 7.8 → R3 8.1 → R4 below.

## Watermark CSS verification (the round's headline claim)

`static/css/style.css` L1586–1634 (deployed copy identical):

| Check | Result | Evidence |
|---|---|---|
| Circle centered | **PASS** | `::after` at `top:50%; left:50%` + `transform:translate(-50%,-50%)`, 180px ring, border-radius:50% (L1603–1610); shrinks to 130px <480px (L1633). |
| Lines at 25/50/75% | **PASS** | `::before` stacks five `linear-gradient(90deg, …)` hairlines: blue at `calc(25% ± 1px)`, red center at `calc(50% ± 1.5px)`, blue at `calc(75% ± 1px)`, plus 2px goal lines at each end (L1592–1600). Percentage-anchored → scales with card width. |
| Opacity ≤ 0.12 | **PASS** | Max alpha in any layer: 0.11 dark / 0.12 light (red center line); blues 0.10–0.11; crease halo inset 0.035, outer ring shadow 0.05. All whisper-level. |
| No layout shift | **PASS** | Both pseudos are `position:absolute` (`inset:0` / centered) + `pointer-events:none` + `user-select:none` — zero flow impact, zero hit-test interference. Content lifted with `.hero-card > * { position:relative; z-index:1 }` (L1617) — relative keeps flow identical. `.hero-card { position:relative; overflow:hidden }` (L1800) is the containing block and clips the 268px ring diameter that exceeds card height — intended bleed. |
| CBJ hues only | **PASS** | Dark layers use rgba(0,87,184) = --union #0057b8 and rgba(206,17,38) = Goal Red #CE1126; light variants swap to rgba(0,38,84) = Union Blue #002654 deep + same red (L1618–1631). No new hues. |
| Both themes | **PASS** | Dedicated `html[data-theme="light"]` overrides for both pseudos. |
| Reduced-motion | **PASS** | Fully static (no animation/transition) — needs no guard. |
| Geometry math | **PASS** | Label/track arithmetic re-computed: the 11-track group-B labels (L1963–67) hold constant ±20px offsets vs true track positions at 960/1200/1400px — zero drift; formula `fr=(100%−696px)/6` correct (696px = 5px tracks + 10 gaps + 16px separator... verified component-wise). |
| Cascade safety | **PASS** | Only 2 pseudo declarations exist for `.hero-card` (grep); no later block re-touches them (later hero-card rules at L1800–1806 touch position/overflow/.hero-team only). No selector collision. |

Caveat (static): rendered softness/compositing is unverified without paint; geometry is
source-proven. Print stylesheet hides `.hero-glow`/`.team-watermark` but not the hero-card
pseudos — the watermark prints (harmless at grayscale; nit).

## R3 fix-list re-verification (6 claims + carried items)

| R3 item | Verdict (v54) | Evidence |
|---|---|---|
| Saira Condensed 800 in fonts href | **FIXED** | Head link now `Saira+Condensed:wght@600;700;800`; all display weights resolve to real faces (`.brand-text` 800 at css:215, wordmark un-fauxed). |
| Mono consolidation AT ORIGINAL rules | **STILL APPEND-ONLY** | Tokens exist (L1912–14) but the original rules are untouched: `th` 10px (L479), `.sb-meta` 10px (L377), `.status-chip` 8.5px (L448), `.pal-grp` 9.5px (L766); the 5-selector overlay (L1916–20) does the binding. Cascade-order compliance, not consolidation. |
| `--mono-md` dead token | **STILL DEAD** | Defined L1914, 0 uses. |
| `.tl-game.otl` 8px | **UNFIXED** | Still `font-size: 8px` at L704 — the smallest text in the product. |
| 34 font-size values | **IMPROVED** | 30 distinct values now (16×9.5, 16×11, 15×10, 14×13 …) — drift continues but no growth. |
| Rink-lines hero watermark | **SHIPPED** | Full verification table above. |
| (sibling-ledger) verBadge deleted | **FIXED** | 0 `verBadge` hits in templates/static. |
| (sibling-ledger) em-dash empty cells + MATCH header | **FIXED** | `.t-score-empty` renders `–` with aria-label (app.js:1069) styled mono 11px faint (css:445); header spans are Time/Home/**Match**/Away/Rink (app.js:1104/1108); cols-head 11-track labels (L1963–67) kept in sync. |
| (sibling-ledger) version sync | **FIXED** | APP_VERSION=54 = JS_VERSION=54, `?v=54` everywhere — no boot reload. |
| (sibling-ledger) literal `\u2026` escape bugs | **CLEAN** | Grep for `\\u` double-backslash: 0 hits. |
| (sibling-ledger) PACEMAKERS copy | **FIXED** | Ships "LEAGUE LEADERS" (app.js:595). |
| (carried) off-token blue rgba(42,127,212) | **PARTIAL** | Down to 19 tint/border/glow instances (was 30+); core text/border colors migrated to var(--union). Tint-layer only, so perceptually near-identical — craft debt, not a hue violation. |

## Dimension scores

| Dimension | Evidence (source-level) | Score |
|---|---|---|
| 1. Visual identity (12%) | The broadcast asset finally exists: rink-lines watermark geometry-verified (center circle + crease halo, quarter-ice blue lines, red center line, goal lines) in strict CBJ hues at whisper opacity, clipped, static; Saira 800 wordmark is a real face now. Custom skate-blade mark + provenance footer. Only paint-level softness unverified. | 8.9 |
| 2. Typographic system (12%) | 3-stack intact, 800 real (kills faux-bold smear), tabular-nums table-wide, em-dash empty cells give the display face honest work. Blemishes carried: mono scale still an overlay (originals hardcoded), 30 font-size values, dead --mono-md, .tl-game.otl 8px. | 8.3 |
| 3. Color system (10%) | Accent discipline holds (Goal Red = live/cut only); watermark introduces zero new hues both themes; faint AA still passing (4.59/4.55 worst-case, R3-verified values unchanged). Residual: 19 rgba(42,127,212) tints off the --union token, elim-row 0.72 opacity compromise. | 8.4 |
| 4. Layout & hierarchy (12%) | Watermark sits behind hero content (z-lift correct, no overlap risk); 11-track cols-head label math re-derived and width-stable; marquee/long-tail separation unchanged-good. | 8.5 |
| 5. Density & data presentation (12%) | Zebra + solid hover, sticky th, min-width guards, self-hiding swipe fade, tabular everywhere — unchanged from R3 8.6 minus the 8px OTL chip. | 8.7 |
| 6. Interaction & micro-feedback (10%) | Source-only: pointer affordances, 14 focus-visible rules, palette pop, press states. Watermark's pointer-events:none verified — cannot steal clicks. <100ms feel unverifiable without a browser. (static) | 8.0 |
| 7. Motion design (8%) | Watermark deliberately static — correct restraint; motion inventory unchanged (LIVE pulse, score flash, entrances) with 3 reduced-motion blocks; hero-glow-breathe remains the sole ambient piece. | 8.3 |
| 8. Depth & material (8%) | Luminance stack + hairlines unchanged; watermark's inset-30px halo + 44px outer ring is layered depth done in two box-shadows — restrained. | 8.6 |
| 9. Consistency & component quality (8%) | Version stamp synced, verBadge dead refs gone, escape-bug class eliminated, one scorecell anatomy. Mono overlay + dead token remain the consistency drag. | 8.5 |
| 10. Mobile ergonomics (8%) | Watermark scales down (130px circle <479px) and clips inside overflow:hidden; 44px targets, card stack, safe areas — carried from R2/R3 passes. No new mobile risk from v54 assets. (static) | 8.3 |

**WEIGHTED TOTAL: 8.464 → 8.5/10**

Above my R3 stated ceiling (~8.4): the shipped bundle covered my three fixes *plus* six
sibling-ledger items (em-dash/MATCH, version sync, verBadge, escape, copy) — the identity
jump carries the total. Remaining gap to 9.7 lives in unverifiable interaction feel and the
carried mono/font-size craft debt, not in tokens or identity.

## Three cheapest fixes with the highest lift

1. **Actually consolidate the mono scale at the original rules** — swap the hardcoded px in
   `th`/`.sb-meta`/`.status-chip`/`.pal-grp` (and `.tl-game.otl` 8px → 9.5px) to the tokens,
   delete the L1916–20 overlay and the dead `--mono-md`. Δ ≈ +0.06 (consistency +0.4, type +0.3).
2. **Migrate the last 19 rgba(42,127,212,*) tints to --union-derived rgba(0,87,184,*)** —
   mechanical replace, one hue family retired. Δ ≈ +0.05 (color +0.5).
3. **Type-scale floor + consolidation** — replace the 7.5/8/8.5/9px stragglers with --mono-xs
   (9.5px floor) and collapse the 30 distinct font-size values toward a 6-step scale.
   Δ ≈ +0.04 (type +0.3, consistency +0.2).

VERDICT: 8.5/10
