# CAHL UI/UX JURY — R7, Juror 3/5 — VISUAL CRAFT lens (v61) — verification round

- Method: Chrome-free static audit of deployed bytes — `/static/css/style.css?v=61` (86,371 B, sha e4a6afe0, byte-identical to a second live fetch), `/static/js/app.js?v=61` (153,328 B, sha fc8ad474), `/` index, fetched 2026-09-04; `/api/version` = `{"js":61}`; `/api/today` live (2 games, clean shape). Baseline for diff: my saved `qa/jury_r6/style_v59.css` → 59 hunks (full type-normalization pass).
- **Verification verdict: ALL R6-cited fixes landed in deployed v61 — every one byte-verified, none fabricated.** In-place edit proof: `.heat-name`/`.gd-empty` carry `/* R6 type-scale: was 13px */` comments inside the original rule bodies — the 5-round append-over-edit anti-pattern is finally dead.
- Score lineage: 7.8 (R2) → 8.1 (R3) → 8.5 (R4) → 8.7 (R5) → 8.7 (R6) → **9.1 (R7)** — first round clearing 9.0; the R6 stalled-round debt was paid in full plus interest.

## Fix-verification ledger (R6 citations → v61 deployed bytes)

| R6 citation | v61 byte evidence | Status |
|---|---|---|
| dark `--accent` #e8253c (4.47:1/4.18:1) | `--accent: #ef3d54` (single decl) = **5.13:1 bg / 4.80:1 panel** | LANDED ✓ |
| light `--faint` #8a99ad 2.90:1 | `--faint: #5d6b80` = **5.04:1** (dark → #7d92ad = **6.18:1**) | LANDED ✓ |
| tonight-label 8.5px/7.5px | both breakpoints now `var(--mono-xs)` (9.5px) | LANDED ✓ |
| heat-name/gd-empty 13px | 14px, edited in originals w/ comments | LANDED ✓ |
| tl-game.otl 8px | 9.5px `var(--mono-xs)`, 26px pill | LANDED ✓ |
| --mono-md dead | 12px canonical, **5 uses** (+xs 4, sm 3) | LANDED ✓ |
| sb-name 19/20 split | 20px base + 20px @media (agree) | LANDED ✓ |
| t-home/t-away 16.5/17 | 17px base + both media 17px (agree) | LANDED ✓ |
| button:hover #3a8fe0 raw | `var(--union-hover)` / light `--union-hover-deep` #0d3a73; 0 raw-hex hover decls | LANDED ✓ |
| type census 28→14 | literal census: **13 px values + 1 pt (print) = 14** (17 incl. 3 mono tokens); v59 was 32 decls | LANDED ✓ |
| scored-chip truncation | two-line anatomy: home line / away line, score right-aligned, `minmax(0,1fr) auto` | LANDED ✓ |
| (bonus, R6-1) cols-head labels painted twice | ::after pseudo-labels deleted, spans are the labels | LANDED ✓ |
| (bonus, R6-4) count-ups no RM gate | `matchMedia('(prefers-reduced-motion: reduce)')` gate in `animateNumbers` | LANDED ✓ |
| (bonus, R6-1) `.scrim` emitted, 0 CSS | `.t-home/.t-away .scrim` muted+italic, `:has(.scrim)` non-interactive | LANDED ✓ |

Also verified: **zero** `font-size` literals left in app.js (JS-driven type one-offs eliminated); index refs `style.css?v=61` + `app.js?v=61` in sync with `/api/version`; Google Fonts href carries Inter 400–800 / Saira Condensed 600/700/800 / JetBrains Mono — every weight CSS requests exists; watermark (6 rules), 11 keyframes (all purposeful), 4 reduced-motion blocks, 20 tabular-nums, zebra, sticky theads, 1 backdrop-filter, 9×44px floors — all intact.

## Dimension scores (fresh, v61)

| # | Dimension | Evidence (v61 bytes) | Score |
|---|---|---|---|
| 1 | Visual identity | Rink-lines watermark block intact; broadcast-bug brand stack + Saira 800 wordmark; tonight-KPI strip and scored-chips now *strengthen* the marquee identity; the sub-AA red that kept polish from showing is gone. Effort: full-sheet rule parse + cascade check on every new block. | 9.1 |
| 2 | Typographic system | The 5-round mono ledger is CLOSED: 14 literal sizes (was 28+), 3 canonical mono tokens with real uses (md 5×), sub-14px stragglers edited in place, uniform 9.5px micro-label floor (26 selectors, one value — zero 8/7.5px survivors), zero JS type literals. Remaining: 14 literals is still 11 more than the token set — 16/17px and 20/22px pairs unquantized; `.heat-val` keeps a 12px literal that the later alias rule overrides (duplicate, not conflict). | 9.0 |
| 3 | Color system | Accent discipline holds (Goal Red = live/lead/interactive only); AA now passes where it failed 4 rounds: accent 5.13/4.80, faint 6.18 dark / 5.04 light, muted 5.97 panel; hover hues tokenized both themes; raw-hex census down to 12 defensible decls (#fff on fills, print-grayscale block, #a30e1e light-theme Goal-Red shade). **Survivor: `.rink-head` dark = var(--union) #2a7fd4 = 4.46:1 on panel — sub-AA on 10.5px mono, 2nd round.** | 9.2 |
| 4 | Layout & hierarchy | Cols-head double-paint removed (spans-only labels); marquee ladder now coherent end-to-end (34 → 26 → 22 → 20 → 17 → 14 → 9.5); tonight-strip 4-col KPI band + rink-head grouping rhythm hold; scored-strip `auto-fill minmax(170px)` sane. Weak spot: tonight-strip 4-col persists to 390px (scored under mobile). | 9.1 |
| 5 | Density & data presentation | Sticky theads, zebra, 20 tabular-nums, ellipsis everywhere; scored-chip two-line restack removes the name-truncation failure mode while keeping 8px grid rhythm; tonight-num 26→22px compaction at ≤599px. No jiggle risk found in any grid track spec. | 9.0 |
| 6 | Interaction & micro-feedback | api() 30s AbortController + retry-once, autoToggle `:has(:checked)` feedback, count-up RM gate — all carried intact. **Carry: `tr.link:focus-visible` ships outline only — no background parity with `tbody tr:hover` — keyboard rows remain weak locators (2nd round).** | 9.0 |
| 7 | Motion design | 11 keyframes, all purposeful; enrichment added zero new animation; count-ups (the last ungated motion) now respect prefers-reduced-motion; 4 RM blocks kill everything else. Nothing decorative found. | 9.3 |
| 8 | Depth & material | Still the sheet's best craft: 1 backdrop-filter total, tokenized shadow families, tonight-KPI `panel-2→panel` luminance gradient, hairline borders on every new chip, no blur soup, no fake shadows. | 9.2 |
| 9 | Consistency & component quality | New components finally inherit the system instead of inventing one-offs (tonight-label/brand-sub → var(--mono-xs); hover → shared tokens; chips → one anatomy). Token uses real (md 5×). Remaining: rink-head picks union where every other mono group label uses muted — one opinionated one-off left; heat-val duplicate decl. | 9.0 |
| 10 | Mobile ergonomics | 44px floors + tap-highlight parity intact; tonight-label 7.5px→mono-xs kills the legibility failure; tonight-num/time compacted at ≤599px; palette 16px (no iOS zoom). **Carry: `.tonight-strip` stays `repeat(4,1fr)` at 390px — 4×~86px cells, no 2-col stack (2nd round).** | 9.1 |

**WEIGHTED TOTAL: 9.1/10** (identity 1.092 + type 1.080 + color 0.920 + layout 1.092 + density 1.080 + interaction 0.900 + motion 0.744 + depth 0.736 + consistency 0.720 + mobile 0.728 = **9.092**)

Gate status: ≥9.7 per-dimension not yet met by any dimension; the two point-masses left are the type-token completion (14 literals) and the last contrast/interaction carries.

## The 3 cheapest fixes toward 9.7-per-dimension

1. **Type-token completion — collapse the remaining 14 literals onto the scale** (~1h): map 9.5→xs, 10.5→sm, 12→md everywhere (delete `.heat-val`'s 12px duplicate — the alias rule already wins); quantize 16/17px → one body size token and 20/22px → one subhead token; leave the display ladder (26/30/34) as declared `--display-*` steps. Type 9.0→~9.6, consistency 9.0→~9.5. **Delta: ~+0.11.**
2. **Last contrast + keyboard carry, two rule edits** (~15min): `.rink-head` dark color → `#4a9ae6` (6.19:1 on panel, same blue family) or `var(--muted)` (5.97:1) to match every other group label; add `tbody tr:hover, tr.link:focus-visible { background: var(--panel-2) }` parity. Color 9.2→~9.6, interaction 9.0→~9.4. **Delta: ~+0.08.**
3. **Tonight-strip 2-col stack at ≤599px** (~10min): `.tonight-strip { grid-template-columns: repeat(2, 1fr) }` in the existing ≤599px pass — 4×86px cells at 390px is thumb-hostile and is the only reason the KPI band isn't clean at mobile; the 22px/mono-xs compacted type then breathes. Mobile 9.1→~9.6, layout +0.1. **Delta: ~+0.05.**

Combined realistic ceiling for R8 if all three land: **~9.25/10 weighted, top dimensions at 9.5–9.6**. The remaining 0.2 to a 9.7 median is viewport-truth my Chrome-free audit cannot grant: hover/press feel, animation timing, and 390px rendering must be confirmed visually (vision_analyze on owner-captured screenshots, per the standing no-Chrome-automation rule) before any dimension can honestly claim 9.7.

VERDICT: 9.1/10
