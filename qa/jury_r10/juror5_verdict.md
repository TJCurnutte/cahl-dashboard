# Jury R10 — Juror 5/5 — PRODUCT CREDIBILITY lens (v70, deployed bytes)

Method (Chrome-free, standing owner rule): fetched the deployed `/` shell first-hand
(13,161 B, sha256 `7cde145fab61…`), then the exact asset URLs the shell references —
`/static/js/app.js?v=70` (157,005 B, sha `61a31053d57e`), `/static/css/style.css?v=70`
(88,845 B, sha `67fb387cb624`), `/static/css/landing.css?v=70` (8,892 B, sha `dba0644868d3`)
— and confirmed each byte-identical to the plain-path copies. `/api/version` → `{"js":70}`;
shell carries `?v=70` on all three assets + `APP_VERSION = 70` + `JS_VERSION = 70` in app.js —
deploy verified end-to-end. (Procedural note: bare `/app.js?v=70` 404s for non-browser
agents; the `/static/…` paths are the real ones. WAF also 403s curl with the default UA.)
Live single-shot probes this round, all 200: `/api/today` 1.97s (2 real games, zero
placeholder tokens), `/api/teams` 2.57s (252 teams), `/api/leaders` 7.95s (player_id
present 15/15 rows), `/api/players` **17.84s / 5.51 MB decompressed** (R9: 35.4s/5.6MB —
first-round visit under the client's 30s ceiling at last, warm). v67→v70 diffed line-level
(7 app.js hunks, 3 style.css hunks, 18 landing.css hunks); WCAG recomputed on changed
tokens; RM coverage re-audited rule-by-rule. No browser automation; every claim byte-,
payload-, or probe-verified against prod.

## v70 gate verification — my 3 R9 cited fixes

| Fix | Status | Evidence (deployed bytes) |
|---|---|---|
| Finish R8-B on the two remaining dead-link families (Analytics L2521 + `leaderSection` L282) | ✅ **SHIPPED — the R9-A class is closed app-wide** | Census: **0 unconditional `<tr class=link onclick=selectPlayer` rows remain**. All 5 `selectPlayer` row sites are now ternary-guarded: `leaderSection` L282 (`p.player_id ?` conditional onclick, `<span class="link">` also removed from the name), League L1576/1579/1582, Analytics Top Scorers L2521 (guard added *and* pos-chip kept). The 4th leader surface (Players search L702) guards on `p.token` via `selectPlayerToken`. **4 guarded sites across 4 leader surfaces, exactly as briefed.** With `/api/leaders` now shipping real ids 15/15, every leader table renders live-or-nothing — no dead affordances. |
| Retokenize landing.css literal sizes | ✅ **SHIPPED** | v67 had 16 literal px across 12 junk sizes (11/12.5/13.5/15/17/19/26/27/32/44). v70: **15 literals, all 7 on the system scale (13/14/16/20/26/30/34), zero off-scale**, plus 6 `var()` sizes (`--mono-sm` ×4, `--mono-xs` ×2). Off-token fallbacks stripped too (`--union-cta, #1f6cb8` → `var(--union-cta)`; `--sponsor-gold`, `--union-hover` same — every token now resolves from the one `:root` in style.css, verified def-by-def). Bonus on-token fixes: hero 44→34px, CTA hover fallback gone, `lp-cta-sm` 42→**44px** (the R7 mobile floor), mobile title 27→26. |
| Blur the blur + one sponsor mark | ✅ **SHIPPED** | landing.css L43: `.lp-nav` background is now opaque `var(--bg)` with the comment *"R9-4: nav blur removed — backdrop-filter budget stays with the app"*. **backdrop-filter census: exactly 1 in the entire product** (style.css L765, palette scrim) — down from 2. Sponsor mark unified: app.js L1239 Today strip now points at `upright-lockup.png` (`upright-crown.png` has **zero** references left); landing.css L190 adds `max-width:150px; object-fit:contain` to the strip img. One brand, one mark. |

Also byte-verified this round (carries + new): dataStamp ticking intact (paintStamp +
`setInterval(paintStamp, 60000)`, L2919-2923); esc ledger still clean (0 unescaped
`data.error`/`e.message` render interpolations across 11 sites); dead-team self-heal intact
(L2003-2011, escaped player-facing copy + picker re-render); **palette input focus ring
shipped** (`.pal-input-row:focus-within { inset box-shadow: var(--union) }`, style L784) —
a keyboard-affordance fix no juror asked for; **`?? '-'` null-guards** on all numeric
roster/search cells (gp/g/a/pts/pim) so preseason empty stats render dashes, not
`undefined`; duplicate `html[data-theme="light"] .rink-head` rule deduped;
`--union-hover` darkened to `#2b71c4` (recomputed: white on it = **4.93:1**, up from 4.6:1
label contrast on `#3a8fe0`) with the CTA idle token held at 5.39:1.

## New in v70 — Supabase persistence (verified in source + behavior)

`app.py` L328-370: PostgREST-direct store (`cahl_cache(key, payload jsonb, updated_at)`),
env-gated (`SUPABASE_URL` + `SUPABASE_SERVICE_KEY`, inert without both), fire-and-forget
upsert. The payoff is visible in the probes: `/api/players` cold-start now hydrates from
Supabase (L475-482, `from_supabase: true`) or the on-disk snapshot before fanning out to
~60 rosters — measured **17.84s → under the 30s client ceiling** this round (R8: 45.0s,
R9: 35.4s). Single-flight lock (L487-490) kills the stampede. The server debt that has
been my #1 credibility citation for three rounds is now architecturally addressed, and the
client ships honest handling for the remaining partial state (`partial: true` → "Index
still filling — tap to retry" hint at L551, copy already in place).

## New defects this round

- **R10-A — the live scrape-backed tier is 502ing right now.** Probed 4× over ~10 minutes
  (16:47–16:58Z): `/api/team/E25EA9F0-…432C8` and `/api/league/Sunday%20C%20West` both
  return **502 Bad Gateway, empty body, every attempt** (R9 got clean JSON from the same
  endpoints same-day). Cache-backed endpoints (`today/teams/leaders/players`) are all 200 —
  the Supabase tier is doing its job — but every League-tab load and the dead-team repro
  currently fall through to the client's failure path. Credit where due: that path is
  graceful by design (`api()` one silent retry on 5xx → `{error:'Network error. Try
  Refresh.'}` → escaped friendly card + Retry button), so users see a managed message, not
  a crash. But "the league tab is down while the rest of the product is up" is a live
  credibility wound, and the League-tab payload could not be re-validated this round.
- **R10-B (nit) — RM coverage is class-targeted and misses two one-shot entrance
  animations + one dot.** Rule-by-rule audit of all 22 animation declarations: infinite
  loops are fully covered (live-dot-pulse ×5 selectors, live-breathe, shimmer,
  hero-next-dot/glow, spin via `.pal-ov .spinner` — and the palette's spinner is the only
  one the RM block names; the identical `.spinner` used by ptrHint/refreshBtn at app.js
  L834/918 is killed only when it lives in `.pal-ov`). Misses: **`pal-fade` (`.pal-ov.open`)
  and `pal-pop` (`.pal` panel) have no animation kill**, and the header **`live-pill-dot`
  (style L258, pulses under `body.has-live` via `live-dot-pulse` infinite) is not named**
  in the RM block (which kills `.live-dot`, a class the markup doesn't use). All three are
  sub-200ms or 6px dots — cosmetic, but the "reduced-motion safe" claim in the brief now
  has three concrete counterexamples.
- **R10-C (nit) — inline-idiom debt static.** 43 inline `style=` (unchanged), 5
  inline-styled h3s (L284/1491/1578/1581/2041, unchanged incl. the two inside the R9 fix
  hunk), 22 `onclick=` handlers (down from 28 — the leader-row conversions replaced inline
  onclick strings with ternaries). No new debt; none paid.
- Payload note (carry): `/api/teams` still ships "Bye Week"/"Team Blue"/"Team Red" via
  typeahead (252 teams). Today/leaders payloads clean.

## The 10 dimensions

| # | Dimension | Evidence (what I saw) | Score |
|---|---|---|---|
| 1 | Visual identity (12%) | Crest ×2, 34px Saira display (was 44 — now on-scale), mono kickers, rink-lines watermark, honest founder story + not-affiliated disclaimer. My R9 identity drag (two sponsor marks) is closed — crown has zero refs left, lockup everywhere. Front door + in-app both read "sports broadcast product." Effort: re-checked every brand surface in shell/app/landing bytes. | 9.7 |
| 2 | Typographic system (12%) | landing.css fully on the system scale: 0 off-sizes of 15 literals + 6 var() uses; all fallbacks stripped so tokens resolve from the single `:root`. style.css census unchanged and clean (8 sizes, all on-scale). Residual: the 5 inline-styled h3s and 43 inline styles keep one foot in the old idiom. | 9.6 |
| 3 | Color system (10%) | Recomputed on the changed tokens: CTA 5.39:1, hover 4.93:1 (improved), sponsor gold 6.38:1 dark / 5.53:1 light — all AA. Red = live/interactive only; gold quarantined to sponsor; wins green. Zero off-token hues anywhere; fallback literals removed so theming can't fork. | 9.7 |
| 4 | Layout & hierarchy (12%) | Landing order hero→features→about→sponsor→footer; in-app sponsor strip below data. Dead-team path lands on escaped copy + picker. The 502 tier currently empties League/Team, but the failure lands as a friendly card with Retry — hierarchy holds even in failure. | 9.7 |
| 5 | Density & data presentation (12%) | `/api/players` 17.84s warm (was 35.4s) — the front door now opens inside the client ceiling. `?? '-'` guards mean empty preseason cells render dashes. Sticky theads, zebra, tnum, sortable carry. Dents: dataStamp still stamps session-not-payload (6th round as a nit); League payload unverifiable while R10-A 502s; teams payload still lists Bye Week/Team Blue/Red. | 9.6 |
| 6 | Interaction & micro-feedback (10%) | R9-A dead links closed on all 4 surfaces (0 unconditional rows); palette focus ring added; `/api/players` under ceiling; players partial-state hint copy honest. Held back by R10-A: League + team loads 502 right now, so those tabs answer only after a retry cycle — the interaction story is strong in code but degraded live this round. | 9.5 |
| 7 | Motion design (8%) | 10 keyframes, all purpose-traceable, zero decorative loops. RM audit rule-by-rule: all infinite loops covered; misses are three one-shots/sub-200ms items (pal-fade, pal-pop, live-pill-dot) — cosmetic counterexamples to "reduced-motion safe," so 9.7→9.6. | 9.6 |
| 8 | Depth & material (8%) | backdrop-filter census = **1 in the whole product** (palette scrim only). The lp-nav blur — my R9 depth citation — is gone with an in-code credit. Opaque nav bar, hairlines, no fake shadows. Nothing left to deduct. | 9.7 |
| 9 | Consistency & component quality (8%) | One scorecell anatomy across all 4 leader surfaces (same ternary-guarded row idiom, guarded class AND onclick); one sponsor mark; tokens resolve from one `:root`; esc 11/11 clean. Residual: 43 inline styles / 5 inline-styled h3s — the old idiom persists in 5 spots. | 9.6 |
| 10 | Mobile ergonomics (8%) | landing.css 430px pass improved (title 26px, CTA 16px, `lp-cta-sm` min-height 44px — the touch floor now on every CTA variant); in-app ≤430 floors, viewport-fit=cover, safe-area, 16px inputs all intact; sponsor strip img capped 150px/contain. (Static — no rendered-pixel pass under the no-Chrome rule.) | 9.6 |

## WEIGHTED TOTAL

identity 9.7×12% + type 9.6×12% + color 9.7×10% + layout 9.7×12% + density 9.6×12% +
interaction 9.5×10% + motion 9.6×8% + depth 9.7×8% + consistency 9.6×8% + mobile 9.6×8%
= 1.164 + 1.152 + 0.970 + 1.164 + 1.152 + 0.950 + 0.768 + 0.776 + 0.768 + 0.768
= **9.6 / 10** (unrounded 9.632)

Lineage: R3 7.3 → R4 8.4 → R5 8.4 → R6 8.8 → R7 9.4 → R8 9.5 → R9 9.5 → **R10 9.6**. All
three of my R9 fixes verified shipped, plus two I didn't ask for (palette focus ring,
`?? '-'` cell guards) — the fixer is now fixing ahead of the jury. The three-round-long
dead-link ledger is closed with zero unconditional rows, `/api/players` opened from 45s →
17.8s across three rounds, and the blur/sponsor/type debts from R9 are all paid. What holds
this out of the 9.7 gate: the live 502 tier (R10-A), three RM misses, and the inline-idiom
residue. Per-dimension gate: 4 dimensions pass 9.7 (identity, color, layout, depth),
5 sit at 9.6 (type, density, motion, consistency, mobile), interaction at 9.5.

## The 3 cheapest fixes toward 9.7-per-dimension

1. **Heal the 502 tier (~server-side, no client bytes).** The scrape-backed endpoints
   (`/api/team/<id>`, `/api/league/<name>`) 502 4/4 probes this round while Supabase-backed
   ones are 200. Extend the same persistence pattern: persist the last-good league/team
   payloads into `cahl_cache` (they're already JSON) and serve stale-with-`partial:true` on
   upstream failure — the client already renders that state honestly ("Still gathering…").
   Also fixes my inability to re-validate the League payload. **Δ interaction 9.5→9.7,
   density 9.6→9.7, layout 9.7 stays (weighted +0.048).**
2. **Close the three RM misses (~5 lines, one file).** Add to the L1216 RM block:
   `.pal-ov.open, .pal { animation: none !important; }` and
   `body.has-live .live-pill .live-pill-dot { animation: none !important; }` (or rename the
   L258 class to `.live-dot` to join the existing kill). Three concrete counterexamples to
   the reduced-motion claim become zero. **Δ motion 9.6→9.7, consistency 9.6→9.65
   (weighted +0.012).**
3. **Pay the inline-idiom residue (~10 edits, mechanical).** Add `.section-h`/
   `.subhead` classes for the 5 inline-styled h3s (two sit inside the R9 fix hunk at
   L1578/1581 — same file, same class of debt three rounds running) and sweep the
   highest-traffic inline `style=` (43) into landing/style utilities. **Δ consistency
   9.6→9.7, type 9.6→9.65 (weighted +0.018).**

Ceiling with all three: ≈ 9.69 weighted. The residual gap is live-upstream health (the
scrape tier's availability, which no client code can mask beyond the graceful card),
the dataStamp "UPDATED" semantics (session vs payload age), and preseason payload
thinness — all now framed honestly in the UI.

## Residual credibility risks (static-verification limits)

- 502 probes were single-shot ×4 across 10 minutes on one evening; the scrape tier's
  baseline availability needs a longer window to characterize.
- League-tab and dead-team payloads could not be re-validated this round (502s); all R9
  claims about their content rest on R9 data plus unchanged code paths.
- Gate a11y: landing dialog still lacks Escape handling and a focus trap (Escape census
  covers palette + typeaheads only); Tab-into-page-behind unverified without a browser.
- OG image still 512×512 (platforms expect ~1200×630 — crops/letterboxes).
- Landing marketing claims ("updating live", "5,900+ players" — payload says 5,862 today)
  are true warm but depend on the cron warm + Supabase hydration; a cold instance without
  env keys falls back to the snapshot, which the `partial` copy covers honestly.
- (Static) No rendered-pixel verification under the no-Chrome constraint; contrast figures
  computed from tokens; asset quality from prior byte-level PNG decode (lockup unchanged).

VERDICT: 9.6/10
