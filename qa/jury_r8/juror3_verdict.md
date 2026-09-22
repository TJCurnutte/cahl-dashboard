# CAHL UI/UX JURY — R8, Juror 3/5 — VISUAL CRAFT lens (v63) — verification round

- Method: Chrome-free static audit of deployed bytes — `/static/css/style.css?v=63` (88,121 B, sha `e34cf33d`), `/static/js/app.js?v=63` (156,017 B, sha `197f8c28`), `/` index, NEW `/static/css/landing.css?v=63` (6,506 B) + `cahl-logo.svg` (2,936 B), fetched 2026-09-04; `/api/version` = `{"js":63}`; `/api/today` live (9 leagues, clean shape). CSS and JS each byte-identical across two independent live fetches. Baseline for diff: my saved `qa/jury_r7/style_v61.css` (sha `b0b04072`) → +119/−95 CSS lines, +65/−17 JS lines. Contrast math recomputed independently (WCAG relative luminance) — not trusted from comments.
- Score lineage: 7.8 (R2) → 8.1 (R3) → 8.5 (R4) → 8.7 (R5) → 8.7 (R6) → 9.1 (R7) → **9.4 (R8)** — the R7 fix batch landed in full *plus* six unrequested items; this round's gain is real bytes, not generosity.

## Fix-verification ledger (R7 citations → v63 deployed bytes)

| R7 citation | v63 byte evidence | Status |
|---|---|---|
| Type-token completion: micro sizes onto tokens, 17→16, 22→20 | literal census now **8 distinct px values: 13, 14, 16, 18, 20, 26, 30, 34** (73 decls, zero sub-13, zero 9.5/10.5/12/17/22 literals); mono tokens carry real use — xs 30×, sm 40×, md 12×; **zero font-size literals in app.js** (was the JS one-off channel) | LANDED ✓ |
| `.rink-head` #4a9ae6 (6.19:1) + light override | base rule `color: #4a9ae6 /* R7-3: 6.19:1 on dark panel */`; **my independent math: 6.19:1 on `--panel` #0e1420, 5.79:1 on panel-2, 5.29:1 on panel-3 — AA on every dark surface it sits on**; `html[data-theme="light"] .rink-head { color: var(--union-deep) }` present (×2 — duplicate rule, harmless) | LANDED ✓ |
| tbody focus parity | `tbody tr:hover, tbody tr:focus-within { background: var(--panel-2); }` — one selector list, exact parity | LANDED ✓ |
| tonight-strip 2-col at ≤430px | `@media (max-width: 430px) { .tonight-strip { grid-template-columns: repeat(2, 1fr); } }` (gap 6px at ≤599); 390px cells now ~175px, not ~86px | LANDED ✓ |
| (new) hero-glow-breathe retired | `hero-glow-breathe` occurrences: **0**; keyframe deleted (11→10 keyframes); `.hero-glow::before { animation: none !important; }` belt-and-suspenders; static radial halo remains as depth, not motion | LANDED ✓ |
| (new) `h3.section-h` replaces inline styles | rule shipped; **7 templates** use `class="section-h"` (Upcoming/Team Leaders/Standings/Schedule/Full Roster/Previous sessions/Season by Season) — **1 survivor: `<h3 style="margin-bottom:8px">Session records</h3>`** in the session-card JS path (the exact pattern section-h was made to kill) | LANDED, 1 straggler |
| (new) sb-card[data-scrim] muted | `[data-scrim="1"]` emitted by JS; CSS mutes name+num to `var(--muted)` + italic, `cursor: default` — scrimmage cards no longer wear LIVE-card glamour | LANDED ✓ |
| (new) landing gate + CAHL logo | server-rendered `<div id="landingGate" role="dialog" aria-modal="true">` with `gate-logo` (real CAHL mark), `gate-cta` 52px target, sessionStorage `cahl-entered` (removed pre-paint on return); landing.css: 42 rules, 5 sizes, 3 hexes, **0 keyframes**, reduced-motion block kills its transitions | LANDED ✓ |
| (new) Upright sponsor strip | gate card `.gate-sponsor` + Today-tab `.sponsor-strip` (JS-rendered), both `rel="noopener"` + aria-labels; kicker/text anatomy reuses the house idiom | LANDED ✓ |
| (bonus, carried) watchdog honesty | wd8 "Still loading…" nudge → wd40 40s hard-error with debounced retry (`data-retrying`); cold-index truth-telling: "Index cold — first search takes 10–25s, then it's instant" | LANDED ✓ |

Also verified intact: 20 tabular-nums, 1 backdrop-filter, 3 sticky theads, 6 zebra rules, 6 min-height-44px + 7 height-44px floors, 14 focus-visible rules, 6 hover:none/pointer:coarse blocks, 4 reduced-motion blocks, print block (11pt) quarantined. **New finding: the wd40 comment claims "25s must exceed api()'s 30s ceiling" — the code's real value is 40s (correct); the comment is rot. Comment passed my behavior grep; only reading it caught it.**

## Dimension scores (fresh, v63)

| # | Dimension | Evidence (v63 bytes) | Score |
|---|---|---|---|
| 1 | Visual identity | Landing gate opens the product with the real CAHL mark + condensed-wordmark CTA; Upright strip reads as a league sponsorship asset, not ad-sludge; rink-lines watermark, broadcast bug, tonight-KPI band all intact. Effort: parsed every new block + all of landing.css. Remaining: gate-card composition is a competent centered card, not a signature rink-motif moment. | 9.3 |
| 2 | Typographic system | Census is now exactly the claimed 8-step scale (13/14/16/18/20/26/30/34), 73 on-scale decls, mono xs/sm/md = 82 real uses, zero JS type literals, zero sub-13px. Remaining: 13px is a full citizen (19 uses) with **no token** — body sizes are bare literals; landing.css adds off-scale 15/19/25px. | 9.4 |
| 3 | Color system | `.rink-head` #4a9ae6 verified 6.19:1 by my own math (was 4.46, 2 rounds); light theme rides `--union-deep`; Goal-Red discipline intact; otl/hover/muted all tokenized both themes; raw-hex census 70 but top values are token definitions, print block, #fff-on-fill. Remaining: sponsor bronze #b8925e is a second accent family (defensible as sponsor brand, but it's outside CBJ hues). | 9.5 |
| 4 | Layout & hierarchy | Marquee ladder coherent (34→30→26→20→16→14→13); tonight-strip 2-col at ≤430 completes the KPI band's mobile story; section-h gives one heading rhythm; scored-strip `auto-fill minmax(170px)` sane. Remaining: duplicate `.rink-head` light override (dead weight); 390px truth unverified visually. | 9.4 |
| 5 | Density & data presentation | Sticky theads, zebra, 20 tabular-nums, ellipsis discipline, scored-chip two-line anatomy, tonight-num 22→20 compaction — with 2-col cells the compacted type finally breathes. No jiggle risk in any grid track spec I parsed. | 9.3 |
| 6 | Interaction & micro-feedback | focus-within parity landed; watchdog ladder (8s nudge → 40s hard error, debounced retry) + cold-index honesty answer every wait state; palette input 16px. Remaining: stale 25s-vs-30s comment documents the wrong arithmetic; palette input's focus ring is suppressed with no `:focus-within` compensation on the row. | 9.4 |
| 7 | Motion design | Breathe pulse retired the clean way (keyframe deleted, `animation: none !important` backstop); 10 keyframes all purposeful; landing.css adds zero animation and RM-blocks its own transitions; count-up RM gate intact. The sheet's best craft. Not 9.7: pulse/flash timing feel is viewport truth I cannot audit Chrome-free. | 9.5 |
| 8 | Depth & material | Luminance stack bg→raise→panel→panel-2→panel-3 strictly ordered; 1 backdrop-filter total; gate shadow tokenized per theme; static hero halo is depth, not motion. No blur soup, no fake shadows. | 9.4 |
| 9 | Consistency & component quality | section-h adopted in 7 templates; scrim cards muted *into* the system instead of glamoured; sponsor strip reuses the kicker/text idiom; chips/pills one anatomy. Remaining: 1 inline-styled h3 + an inline-styled span in JS templates; landing.css sizes off-scale; duplicate override rule. | 9.3 |
| 10 | Mobile ergonomics | tonight-strip 2-col at 390px (the 2-round carry, fixed); 13× 44px floors; gate CTA 52px; 16px palette input (no iOS zoom); 6 coarse-pointer blocks. Remaining: 390px rendering itself is vision-analyze territory, not byte territory. | 9.5 |

**WEIGHTED TOTAL: 9.4/10** (identity 1.116 + type 1.128 + color 0.950 + layout 1.128 + density 1.116 + interaction 0.940 + motion 0.760 + depth 0.752 + consistency 0.744 + mobile 0.760 = **9.394**)

Gate status: ≥9.7 per-dimension still met by **zero** dimensions — four sit at 9.5, and the two point-masses left are the untokenized body sizes (13/14/16 literals) and the last inline-style stragglers. R7's predicted ceiling (~9.25) was beaten because the shipped batch was twice what I asked for.

## The 3 cheapest fixes toward 9.7-per-dimension

1. **Tokenize the body-size trio + landing.css strays** (~1h): declare `--fs-body: 13px / --fs-strong: 14px / --fs-nudge: 16px` (or fold 13→14 where line-height allows) and map the 49 literal decls (19×13 + 10×14 + 20×16) onto them; quantize landing.css 19→20, 25→26, 15→14/16 onto the existing steps. Type 9.4→~9.7, consistency 9.3→~9.5. **Delta: ~+0.05.**
2. **Kill the last inline styles + the dead duplicate** (~15min): `session-card`'s `<h3 style="margin-bottom:8px">` → `class="section-h"`, the inline `style="color:var(--muted)"` span → a tokenized class, delete the duplicate `html[data-theme="light"] .rink-head` rule. Consistency 9.3→~9.6, color 9.5→~9.6. **Delta: ~+0.03.**
3. **Comment rot + palette focus cue** (~15min): correct the wd40 comment to state the real contract (40s > 30s ceiling + one retry, not "25s > 30s") — comments are part of the product's maintainability craft; add `.pal-input-row:focus-within { border-bottom-color: var(--union) }` so the de-styled input still answers focus. Interaction 9.4→~9.6, motion/identity +0.01 each. **Delta: ~+0.03.**

Combined realistic ceiling for R9 if all three land: **~9.5/10 weighted, four dimensions at 9.6–9.7**. The remaining gap to a 9.7 median is unchanged from R7 and is honest: hover/press feel, animation timing, and true 390px rendering need vision_analyze on owner-captured screenshots — my Chrome-free audit certifies bytes, not photons.

VERDICT: 9.4/10
