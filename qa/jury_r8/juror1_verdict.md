# JURY R8 — JUROR 1/5 — v63 (Chrome-free; deployed-bytes + live-API verification round)

**Method:** Standing rule — no browser automation. Scored from the deployed bytes of `index.html`
(9,964 B), `style.css?v=63` (88,121 B), `app.js?v=63` (156,017 B), **new** `landing.css?v=63`
(6,510 B), `/api/version` (`{"js":63}` = `JS_VERSION 63` — no boot reload loop), computed WCAG
contrast math, and live JSON APIs (all HTTP 200, byte-counted before grepping — the R7 process
rule held: nothing fetched this round was a disguised 404). Rendered-pixel claims remain
**(static)**.

**Gate check — my R7 cited fixes, byte-verified in deployed v63:**

| R7 citation | v63 evidence | Status |
|---|---|---|
| Mono-token migration at ORIGINAL rule bodies (9.5→xs, 10.5→sm, 12→md) | Census: **8 px literals** (13×19, 14×10, 16×20, 18×2, 20×15, 26×3, 30×2, 34×2) + one 11pt print rule — exactly the claimed set. Zero 9.5/10.5/12px literals remain. `.tonight-label` (css:1674-1680), `.live-pill` (css:236-247), `.brand-sub` (css:221-230) base rules now read `var(--mono-xs)`; consumers 30/40/12 (xs/sm/md). `app.js` ships **zero** font-size literals. The 5-round append-only anti-pattern is dead. | ✅ FIXED |
| `.sb-card[data-scrim="1"]` muted/italic + cursor:default | `style.css:439-443` under `/* R7-1: scoreboard cards for scrimmage slots */`: `cursor: default`, `.sb-name` muted+italic, `.sb-num` muted. Emitter intact at app.js:1108. | ✅ FIXED (partial — see New Finding A) |
| (convergent carry) `rink-head` dark 4.46:1 | `css:1704-1709` now `color:#4a9ae6` — computed **6.19:1** on dark panel | ✅ FIXED |
| (convergent carry) `tonight-strip` 4-across at 390px | `css:2110-2112` inside `@media (max-width:430px)`: `repeat(2, 1fr)` | ✅ FIXED |

**Standing ledger re-checked, still holds in v63:** `concat(finals)` (app.js:1212), refresh
busy-state disable+spinner+finally, count-up `prefers-reduced-motion` gate (app.js:797),
`api()` 30s AbortController, hash routing, teams/players error paths escaped with retry
affordances, `tnum` census 20, dark accent `#ef3d54` 4.80:1 panel / 5.13:1 bg, backdrop-filter
census **1**, 4 reduced-motion blocks, mobile min-w/h:0 gate clean (all 16 hits are flex-child
overflow fixes or inside the min-900 desktop block — no control kills).

**New since R7 — verified:** landing gate page (index: `role="dialog"` + `aria-modal`,
sessionStorage-suppressed, CTA fades 0.45s then removes + focuses `#main`; landing.css has its
own RM block and 16px+ body text), CAHL brand logo in header + gate
(cahl-logo.svg 2.9KB / cahl-logo-hd.png 129KB, both HTTP 200), Upright Creative sponsor strip on
Today (app.js:1235-1240, `rel="noopener"`) and on the gate (aria-labelled link).

---

## The 10 dimensions

| # | Dimension | Evidence (what I saw) | Score |
|---|---|---|---|
| 1 | Visual identity (12%) | The v63 landing gate is the marquee-scale signature moment R7 called missing: rink-radial blue/red backdrop (on-palette rgba of --union/#ce1126), HD CAHL logo, Saira display headline, sponsor line — instantly recognizable as a sports product before the app even loads. Header CAHL crest + Today sponsor strip extend identity in-app; sb-card/scrim grammar intact. Effort: fetched + grepped every asset incl. both new CSS files; confirmed both logo files ship. (static) | 9.3 |
| 2 | Typographic system (12%) | Census 8 literals + 11pt print, exactly as claimed; zero sub-13px literals; zero JS literals; base rules tokenized at the original bodies; landing.css consumes the same mono tokens (var(--mono-xs/sm) ×3) so the new surface inherits the system rather than forking it. No visible defect findable at today's values; residual deduction is only the un-governed 14/16/20px tiers. Effort: full-file regex census of both stylesheets + JS. | 9.6 |
| 3 | Color system (10%) | Computed: every text token ≥4.77:1 on its worst surface in BOTH themes (dark text 16.86/muted 5.97/faint 5.78/accent 4.80; light text 17.31/muted 5.13/faint 5.41/accent 5.63); rink-head 6.19:1; gate CTA #1f6cb8 = 5.39:1 with white (AA, comment in source is accurate). Two blemishes: sponsor hover gold #b8925e = **2.87:1 on light panel** (sub-AA decorative hover), and it's an off-token hue with no --gold token (dark 6.42:1 is fine). | 9.4 |
| 4 | Layout & hierarchy (12%) | Night-KPI strip → hero → scoreboard → On The Scoreboard → By-Rink order intact; By-Rink still builds from `upcoming.concat(finals)`; sponsor strip anchors Today's long-tail bottom (gives thin preseason nights a designed footer instead of a shrug); gate page is a clean single-focus hierarchy. Could not pixel-verify 11-track cols-head at 960/1200/1400 without a browser. (static) | 9.2 |
| 5 | Density & data presentation (12%) | Sticky thead ×3, zebra ×6, tnum ×20, sortable/aria-sort machinery intact; live standings payload: 6 teams all-zero GP renders the designed zero-state; zero Bye Week rows in the fetched payload (ingest filters hold); R7-2's table scroll-cue + max-height context block (css:2101-2109) verified for long-table mobile. No jiggling-column patterns. (static + live payload) | 9.3 |
| 6 | Interaction & micro-feedback (10%) | Every fetch path ceiling-protected (30s api(), 22s typeahead, watchdogs); refresh busy-state holds; retry affordances on every error path; gate CTA gives immediate 0.45s fade + focus move. Remaining friction is server-side: **/api/players 13.0s single-shot (improved from 27.5s) but 13.3–37.5s under 5-parallel burst — still straddles the 22s typeahead abort and 30s api() ceiling**; measured twice this round (13.02s cold, then burst). | 9.2 |
| 7 | Motion design (8%) | Vocabulary disciplined: live-dot pulse, score flash, live-breathe glow bar, entrance ≤0.26s for UI chrome (longest timers are pulse/flash cycles, not UI motion); 4 RM blocks + landing.css RM block; gate exit 0.45s opacity fade is purposeful. One aesthetic carry: scrim cards still inherit the animated red glow bar (see Finding A) — motion applied to a non-game state. | 9.2 |
| 8 | Depth & material (8%) | 4-stop luminance ladder (#070b12/#0e1420/#131b2b), hairlines, backdrop-filter census still exactly **1** in 88KB, 1px structural shadows; gate card uses a single large soft shadow (0 24px 80px rgba(0,0,0,.35)) — appropriate for a modal, not a blur soup; radial glows clipped to the gate backdrop. Print stylesheets ×2. (static) | 9.3 |
| 9 | Consistency & component quality (8%) | One scorecell anatomy everywhere; sponsor treatment is ONE system (gate card + Today strip share kicker/name/text pattern and both consume the same landing.css rules); gate/button/chips on-token. Deductions: sb-card scrim cards keep `data-status="live"` so css:349 (red border wash), css:355 (animated 3px glow bar + box-shadow), css:402 (red text-shadow halo on numbers) still paint — my R7 fix muted the text but not the material; and the R7-5 error-escape class survives at 5 sites (app.js:1635, 1702: raw `e.message`; 2306, 2317, 2446: raw `data.error`). | 9.1 |
| 10 | Mobile ergonomics (8%) | Release-gate grep clean (min-w/h:0 regression class dead — all 16 hits triaged: flex-children or min-900 desktop block); 44/48px floors intact (pills/pal-items/kpal 44, nav-link 48 via coarse block css:1158-1167); tonight-strip 2×2 at ≤430px landed; pal-input 16px; scroll-cue + 70vh table context; safe-area insets; tap-highlight transparent. No truncation-soup patterns. (static) | 9.4 |

---

## WEIGHTED TOTAL

identity 9.3×12% + type 9.6×12% + color 9.4×10% + layout 9.2×12% + density 9.3×12% +
interaction 9.2×10% + motion 9.2×8% + depth 9.3×8% + consistency 9.1×8% + mobile 9.4×8%
= **9.3 / 10** (unrounded 9.308)

Every dimension ≥ 9.1; seven of ten ≥ 9.2. The 9.7 all-dimension gate still fails — lowest
dimension is consistency (9.1), dragged by the scrim-material gap and the surviving
error-escape sites.

---

## The 3 cheapest fixes toward 9.7-per-dimension

1. **Finish the scrim card material — ~4 lines at css:349/355/402.** The R7-1 rules muted the
   text but the card still carries `data-status="live"`, so it paints the red border wash, the
   animated 3px glow bar, and the red text-shadow halo that the design ruling reserves for real
   games. Add
   `.sb-card[data-scrim="1"] { border-color: var(--border-soft); background: var(--panel-2); animation: none; }`
   and `.sb-card[data-scrim="1"]::before { display: none; }` (plus a text-shadow: none on
   `.sb-num`). This is the 5th appearance of the "state ships without its full treatment" class.
   **Δ consistency +0.4, motion +0.2, identity +0.1.**

2. **Escape the 5 remaining raw error interpolations — 5 one-word edits.** app.js:1635 and
   1702 render raw `e.message`, 2306/2317/2446 render raw `data.error` — the exact class R7-5
   flagged (raw upstream scraper bodies paint into the DOM when chillerstats 403s). Wrap each in
   `esc(...)` like the 9 sites already fixed. **Δ consistency +0.2, interaction +0.1.**

3. **Token the sponsor gold + make it light-theme-safe — 2 lines.** `#b8925e` is an off-token
   hue and computes **2.87:1 on the light panel** (sub-AA for a text hover). Add `--gold:
   #b8925e` + `--gold-text: #7a5c2e` (computed 6.18:1 on white / 5.75:1 on light bg) and switch
   the two hover rules (landing.css:136, 161) to `var(--gold-text)`. **Δ color +0.3.**

Combined Δ ≈ +1.2 spread across consistency/color/motion → consistency and color reach 9.6-9.7,
projected total ≈ 9.5. Honest ceiling note, same as R7: the last stretch to 9.7-everywhere is
not CSS — it needs (a) the server-side `/api/players` fix (13.0s single-shot improved but the
burst still straddles the 22s/30s client ceilings; gzip IS now served when requested — 1.54MB
wire vs 5.59MB raw — so the residual is upstream build time, not transfer), and (b) a
rendered-browser verification pass to convert the (static) dimensions into pixel-verified ones.

VERDICT: 9.3/10
