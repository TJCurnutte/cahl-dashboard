# CAHL UI/UX JURY — R3, Juror 3/5 (visual craft lens) — v52

Method: NO browser automation (per constraint). Scored from live-source audit of
/static/css/style.css?v=52 (1950 lines), /static/js/app.js?v=52 (2943 lines), / head,
plus WCAG 2.1 contrast math computed in Python over every token×surface pair.
History: R1 6.5 → R2 7.8 → R3 below.

## R3 fix-claim verification (the six visual claims)

| Claim | Verdict | Evidence |
|---|---|---|
| Mono scale consolidated AT ORIGINAL RULES | **PARTIAL FAIL** | Tokens exist (--mono-xs/sm/md = 9.5/10.5/11.5px, css:1865–67) but are an APPEND-ONLY overlay (css:1869–73) binding only 5 selectors (.eyebrow/th/.status-chip/.sb-meta/.pal-grp). The original rules still carry hardcoded px — th 10px, .sb-meta 10px, .status-chip 8.5px, .pal-grp 9.5px, .eyebrow 9.5px — and the mono-family scatter is otherwise untouched: 34 distinct font-size values stylesheet-wide; mono rules still run 8→12px (`.tl-game` 8px, `.stat-box .label`/`.cut-label` 9px, `.t-score.live-badge` 9.5px, `.pacemaker .pace-stat small` 10px, `.t-time` 11px, `.heat-val` 12px). `--mono-md` has **0 uses** — a dead token. Cascade order makes it *render* consistent today; it is not consolidated. |
| --faint ≥ 4.5:1 both themes | **PASS** | Effective values are the late R1-E patch (css:1740–47): dark #7a8ca5, light #5b6c85. Computed worst-cases: dark 4.59:1 (on panel-3 #1a2334), light 4.55:1 (on panel-3 #e8edf5); all other surfaces 4.76–5.74. Muted also AA (dark 5.10 min, light 4.91 min). Caveat: `tr.elim td { opacity: .72 }` (css:1749) drags dimmed-row text to 3.0–3.7:1 — a conscious legibility/semantics tradeoff, still sub-AA. |
| Dead .switch / #autoToggle CSS deleted | **FAIL** | `.switch { gap:4px; font-size:11px; height:24px }` still present at css:1826 inside `@media (max-width:430px)`. No element carries class="switch" anywhere in HTML/JS templates, so visual impact is zero — but the claim said "fully deleted" and grep finds it. #autoToggle itself correctly has no CSS (it's the sr-only input inside .live-pill). |
| Saira Condensed 800 in fonts href | **FAIL** | Sole fonts link (index head) still ships `Saira+Condensed:wght@600;700`. Meanwhile CSS requests 800 on three display rules: `.brand-text` (css weight 800, the wordmark), `.team-watermark` (800), `.lead-pts` (800). Those render with synthesized/faux-bold 700 — smeared counters on a condensed face, on the most-repeated element in the chrome. Inter 800 rules are fine (400–800 loaded). |
| Single accent discipline | **PASS** | Full hex census (css+js) classifies to: slate/gray-blue neutrals, CBJ blues, Goal-Red family, status green/red, and one semantic orange pair (--otl/--warning #f0a24b, #b26a00). Zero purple/violet or stray-amber accents. JS chart hexes (#002654, #070d1a) are theme-derived. |
| Rink-lines hero watermark | **DEFERRED → ABSENT** | No rink-lines CSS exists (grep: 0 hits). Only `.team-watermark` (team page) + `.hero-glow` (soft radial). Identity scored honestly with this absence. |

## Dimension scores

| Dimension | Evidence (source-level) | Score |
|---|---|---|
| 1. Visual identity (12%) | Genuine rink-night bones: 3D Chiller logo + custom skate-blade brand mark, CBJ hues, Goal-Red live language, data-provenance footer. Missing its signature: rink-lines hero watermark deferred; Saira 800 not loaded so the wordmark renders faux-bold. | 7.5 |
| 2. Typographic system (12%) | Disciplined 3-stack (Saira display ×28 uses w/ sensible weights, JetBrains Mono micro-labels, Inter UI); tabular-nums as table-wide default ("numerals NEVER jiggle"). Blemishes: 800-face missing (3 display rules), mono scale an overlay not a consolidation, dead --mono-md token, 7.5–8.5px micro text at the bottom of the scale. | 7.6 |
| 3. Color system (10%) | One accent discipline verified by literal census; faint AA passes both themes (4.59/4.55 worst-case); luminance-stacked surfaces; elim-row opacity compromise 3.0–3.7:1. | 8.3 |
| 4. Layout & hierarchy (12%) | Marquee hero vs long-tail tables clearly separated; today-cols-head 11-track math with explicit calc() lefts so labels land over both groups (css:1899–1921) is meticulous; hero-next strip, wells/cards grouping. | 8.4 |
| 5. Density & data presentation (12%) | Zebra on .board + #leagueSecStandings + roster rows (color-mix 40% w/ solid hover, css:1879–88); sticky th (top:0); min-width guards <700px; self-hiding swipe fade + affordance chip; tabular everywhere. | 8.6 |
| 6. Interaction & micro-feedback (10%) | Source-only confidence (no browser): score-flash, live pulses, 14 focus-visible rules, skip-link, Cmd+K palette w/ pop/fade, toast, pointer affordances. Cannot verify <100ms feel. | 8.0 |
| 7. Motion design (8%) | 11 keyframes, nearly all functional (skeleton shimmer, spinner, entrances, score flash, live pulse, palette); 3 reduced-motion blocks; no blur soup (one functional palette scrim blur(3px), one decorative 10px hero glow). hero-glow-breathe is the only ambient piece. | 8.2 |
| 8. Depth & material (8%) | Textbook luminance stack bg→raise→panel→panel-2→panel-3 + inset wells; hairline rgba borders; shadows minimal + 1px rings; legacy aliases kept resolving. | 8.5 |
| 9. Consistency & component quality (8%) | One scorecell anatomy, chips/pills from one system, jersey numerals unified (.jersey-num display-face 600). Dead `.switch` rule survives at css:1826 (zero visual effect, craft debt). | 8.2 |
| 10. Mobile ergonomics (8%) | 44px targets (nav min-height:44, theme/refresh min-height:44 <700px), <480px grid-template-areas card stack, safe-area insets, header wrap guards, icon-only search <600px. | 8.3 |

**WEIGHTED TOTAL: 0.900+0.912+0.830+1.008+1.032+0.800+0.656+0.680+0.656+0.664 = 8.1/10**

## Three cheapest fixes with the highest lift

1. **Add `;800` to the Saira Condensed axes in the fonts href** — one string edit, zero CSS changes.
   Restores the true 800 face on `.brand-text`, `.lead-pts`, `.team-watermark` (kills faux-bold smear).
   Δ ≈ +0.10 (type +0.6, identity +0.3 weighted).
2. **Actually consolidate the mono scale at the original rules** — swap the ~30 hardcoded mono px
   values (8/9/9.5/10/10.5/11/12px) for the three tokens, delete the appended override block
   (css:1861–73) and the dead `.switch` line (css:1826), and either use or delete `--mono-md`.
   Δ ≈ +0.07 (consistency +0.4, type +0.3 weighted).
3. **Ship the deferred rink-lines hero watermark** — pure CSS: 3 hairline arcs/lines in
   var(--border) at low opacity inside `.hero-card` (already overflow-clipped at css:1752).
   The one asset that pushes Today from "clean dashboard" to "broadcast".
   Δ ≈ +0.12 (identity +0.8, layout +0.2 weighted).

Ceiling check: with all three, ≈8.4 — still short of 9.7; that gap now lives in interaction feel
(unverifiable without a browser) and identity signature, not in tokens.

VERDICT: 8.1/10
