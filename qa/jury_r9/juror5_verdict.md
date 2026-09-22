# Jury R9 — Juror 5/5 — PRODUCT CREDIBILITY lens (v67, deployed bytes)

Method (Chrome-free, standing owner rule): fetched deployed `/` shell (13,161 B — now the full
marketing landing), `app.js?v=67` (156,937 B), `style.css?v=67` (88,795 B), `landing.css?v=67`
(8,928 B), `upright-lockup.png` (242,816 B). `/api/version` → `{"js":67}`; shell carries
`?v=67` on all three assets + inline `APP_VERSION = 67` + `JS_VERSION = 67` in app.js — deploy
verified. Live single-shot probes this round, all 200: `/api/today` 0.94s (2 real games, zero
placeholder tokens), `/api/teams` 3.62s (253 teams; still ships Bye Week + Team Blue/Red via
typeahead — unchanged carry), `/api/leaders` 0.85s (player_id PRESENT on all 5), `/api/league/<Sunday
C West>` 3.24s (all 15 leader rows ship `player_id: None`), `/api/players` **35.4s / 5.6 MB unwired,
1.55 MB gzip wire** (R8 45.0s → 35.4s, still beats the client's 30s ceiling). v63 saved bytes
diffed line-level against v67 (19 app.js hunks, 6 style.css hunks). WCAG recomputed on v67 tokens,
both themes; lockup PNG alpha decoded byte-level (zlib unfilter). No browser automation; every
claim byte-, payload-, or pixel-file-verified against prod.

## v67 gate verification — my 3 R8 cited fixes

| Fix | Status | Evidence (deployed bytes) |
|---|---|---|
| Top Scorers null-player rows un-linked (conditional onclick when `p.player_id` present) | ◐ **PARTIAL (1 of 3 renderer families)** | The conditional shipped on the **League tab** leaders — `loadLeagueContent` L1576/1579/1582, now `` `<tr ${p.player_id ? `onclick="selectPlayer('${p.team_id}','${p.player_id}')" class="link"` : ''}>…` `` — but those three sites were **not the R8-cited ones**. My R8 citation was `L2509-2510` = **Analytics "Top Scorers"**, which is v67 `loadAnalyticsContent` **L2521 and byte-UNCHANGED from v63** (diff: the only hunk in the 2440–2530 range is the L2446→2457 esc fix). Third family: Players `leaderSection` (L279-284, feeds L2318-21 `/api/league` and L2329-31 `/api/leaders`) — also **still unconditional** `tr.link onclick`. Live harm verified: `/api/league/<id>` ships `player_id: None` on **all 15 leader rows** → Analytics Top Scorers + Players per-league render 5 dead rows each right now; `window.selectPlayer` (L2581) has a `if (!teamId || !playerId) return` no-op guard, so the click affordance fires and answers nothing. Mitigation: `/api/leaders` (CAHL-wide) ships real ids, so the Players default view links correctly — the defect is 2 of 3 views. |
| Last 3 raw error sites esc()'d | ✅ SHIPPED | v63 L2306/2317 → v67 L2317/2328 `esc(data.error)`; v63 L2446 → v67 L2457 `esc((data\|\|{}).error \|\| 'No data')`. Full census: **all 8 `data.error` interpolations (L1300, 1471, 1942, 2008, 2013, 2317, 2328, 2354) + all 3 `e.message` (L1051, 1637, 1704) now escaped. Zero raw upstream-interpolation render sites remain — the R7-A class is closed app-wide.** |
| dataStamp ticks every minute (paintStamp + setInterval 60000) | ✅ SHIPPED | v67 L2915-2923: comment names the R8 carry closed; `paintStamp = () => stampEl.textContent = new Date().toLocaleTimeString(…)`; `paintStamp(); setInterval(paintStamp, 60000);` — footer stamp now stays truthful for the life of the session. (Semantics note: it stamps render-time, not payload age — "UPDATED" still means session freshness, not data age; the fib is dead but the deeper honesty item survives as a nit.) |

Also byte-verified this round: dead-team self-heal shipped and **live-validated** — scraper.py:83
returns the player-facing message and the live probe of the exact repro id
(`E25EA9F0-0F26-BD6A-F23ECD21D7F432C8`) returns `{"error":"This team's page is no longer
available on ChillerStats — pick your team again from the list."}`; client L2003-2013 tests
`/no longer available/i`, clears `state.teamId` + `localStorage['cahl-team']` (+ myTeam), paints
the empty card, re-renders the picker. No raw scraper internals can reach the Team tab.
Shared team watchdog migrated to the 40s helper (L1987-1989, deadline > api() ceiling). Cold-index
copy widened to "~30s" (L533). Scrim cards stripped of LIVE material (css 448-452). Table
scroll-context moved onto the table (css 2111-2114, the mechanism now engages).

## New since R8 — full marketing landing + Upright lockup (scored honestly)

- **Landing markup** (shell L48-118): sticky `lp-nav` (crest + About/Features/Sponsor anchors +
  `Open Dashboard` CTA), `lp-hero` (crest, 44px/800 Saira display title, sub, CTA + arrow, "Free ·
  No sign-in · Works on your phone" hint), 4-card "What you get" grid (Live Scores / Standings &
  Stats / All-Time Players 5,900+ / By Rink), About (origin story: "desktop-only site from 2009…
  players check scores on their phones in the parking lot" — a genuinely credible founder story),
  **"Not affiliated with the Chiller or the Columbus Blue Jackets. Just fans with a database."**
  disclaimer, League Sponsor section, footer with ChillerStats credit + © line. Three enter paths
  (`gateEnter`, `gateEnterCta`, `gateEnterFoot`) all wired to `gateDismiss()` (L17-27):
  sessionStorage skip, 500ms fade-then-remove, focus to `#main`.
- **Landing CSS** (landing.css, 221 lines): fully tokenized (`--mono-sm/xs`, `--display`,
  `text-wrap: balance/pretty`), rink-lines `::before` watermark carried over, light-theme gradient
  variant shipped, RM block covers every transition + the nav (L172-174 line: `transition: none`
  for gate/cta/arrow/sponsor-card/links), focus-visible triads on CTA/links/sponsor card,
  430px + 719px passes. WCAG computed on v67 tokens, **all landing pairs pass AA on both
  themes** — worst pair lp-links/lp-sub/fine muted-on-bg = 4.77:1 light; gold kicker/f-icon on
  inset 6.76:1 dark / 5.30:1 light; CTA white on `#1f6cb8` 5.39:1.
- **Upright lockup** (`upright-lockup.png`, 1192×394 RGBA): alpha decoded byte-level — **63.9%
  fully transparent, 19.0% opaque, 17.2% partial (real anti-aliased edges)**; background cleanly
  removed, no white-box defect. Serif lockup renders at 190px in the sponsor card, 170px mobile.
- Nit found: Today-tab sponsor strip (`app.js` L1238-1241) still uses `upright-crown.png` while
  the landing uses the new lockup — two different sponsor marks in one product.
- Nit: landing.css `.lp-nav` adds `backdrop-filter: blur(10px)` — the app proper has exactly 1
  (palette scrim); the landing now doubles that count (2). On-token but it is the blur-soup class
  the brief warns about, in miniature.
- Nit: `hero-next-pulse` keyframe (css L1279-1281, `.hero-next-dot` infinite pulse) is RM-covered —
  the second RM block kills `.hero-next-dot` + `.hero-glow::before` explicitly. Cover verified;
  no uncovered infinite animation found in either stylesheet.

## New defects this round

- **R9-A — R8-B fix shipped PARTIAL; the two uncited sibling families still ship dead links.**
  The conditional landed on the League tab (uncited), while the R8-cited Analytics L2521 and the
  Players `leaderSection` L282 remain unconditional. Live `/api/league` payload: `player_id: None`
  on all 15 rows → 5 dead rows on Analytics Top Scorers + 5 on Players per-league, right now.
  This is the "fix copied to the next site, not the flagged one" class inverted — the fixer
  grepped the wrong family. `selectPlayer`'s internal no-op guard means zero response on click.
- **R9-B — `/api/players` 35.4s / 5.6 MB (1.55 MB gzip wire).** Improved from R8's 45.0s but
  still beats the client's 30s ceiling + retry (guaranteed 2×35s failure path) and the ~25s
  typeahead abort. First Players visit and first search still terminate in error/timeout copy
  today. Server debt (gzip is on; paginate/warm still missing), but it is the product's front
  door for its 5,947-player index.
- **R9-C — new inline-styled h3s landed in the fix hunk itself:** the League conditional rows
  kept their sibling `<h3 style="margin-top:14px">` ×2 (L1578, L1581) — same lines the fix
  touched. Inline `style=` census steady at 43; 5 inline-styled h3s remain (L284, 1491, 1578,
  1581, 2041). The one-off type/contrast recurrence class is dormant but the inline-idiom debt
  did not shrink.
- **R9-D (nit) — two sponsor marks:** Today strip = crown PNG, landing = serif lockup. One brand
  surface, two logos.
- Payload note (carry): `/api/teams` still ships "Bye Week"/"Team Blue"/"Team Red" (typeahead
  reachable). Today/League payloads clean.

## The 10 dimensions

| # | Dimension | Evidence (what I saw) | Score |
|---|---|---|---|
| 1 | Visual identity (12%) | The landing is now a real first-touch brand moment: crest ×2 (nav + hero), 44px Saira display headline, mono kickers, rink-lines watermark, feature grid in the system's voice — it reads "sports broadcast product" before the app even opens. Origin story + not-affiliated honesty is credibility-positive. Residual: the sponsor-mark split (crown vs lockup) and a whisper-level in-app watermark keep it under the gate. | 9.6 |
| 2 | Typographic system (12%) | landing.css is fully on tokens; style.css literal census unchanged (8 distinct px: 13/14/16/18/20/26/30/34). But landing.css introduces 12 literal sizes of its own (11/12.5/13.5/14/15/16/17/19/26/27/32/44) — several sit between the mono tokens (11 < 12px mono-md, 12.5/13.5/15 unaligned) — a new file starting its own scale the moment the main one got clean. 5 inline-styled h3s remain. | 9.4 |
| 3 | Color system (10%) | All landing pairs computed AA both themes (worst 4.77:1); CTA 5.39:1; sponsor gold tokenized per-theme (`#b8925e` dark / `#7a5c2e` light, 6.76/5.30 on inset). Accent discipline intact: red = live/interactive only; gold quarantined to sponsor; wins green. Zero new off-token hues in either stylesheet. | 9.7 |
| 4 | Layout & hierarchy (12%) | Landing reads hero → features → about → sponsor → footer with a clear marquee order and a disciplined single column; in-app Today order preserved with sponsor strip below data; dead-team path now lands on a friendly empty card + picker instead of raw internals (live-validated). Playoff cut-line self-resolves (cutoff 8 > games played 0). | 9.7 |
| 5 | Density & data presentation (12%) | Sticky theads (mechanism now engages — scroll context moved onto the table), zebra+hover, sortable th, tnum, race badges re-verified. Payloads: `/api/today` 2 real games zero placeholder tokens; standings truthful all-zero with honest gd-empty/no-data framing. Dents: dataStamp ticks but still stamps session, not payload age (5th round as a nit); players payload all-zero preseason rows flat. | 9.5 |
| 6 | Interaction & micro-feedback (10%) | Gains: dead-team self-heal live-validated end-to-end, cold-index copy widened to ~30s, three enter paths + focus management on the landing. Losses: R9-A dead links live on 2 of 3 player-leader views (Analytics + Players per-league, live-confirmed null ids); `/api/players` 35.4s beats every client ceiling — first Players visit and first search still error today. | 9.3 |
| 7 | Motion design (8%) | Keyframes census: live-breathe, live-dot-pulse, score-flash, pal-fade, pal-pop, shimmer (skeleton-only), spin, fade-in, hero-next-pulse, rise-in — every one purpose-traceable, zero decorative loops. `hero-next-pulse`'s RM cover verified present (second RM block kills `.hero-next-dot` + `.hero-glow::before`). landing.css ships zero keyframes and its RM block kills every transition it defines. | 9.7 |
| 8 | Depth & material (8%) | In-app ladder clean (backdrop-filter exactly 1 = palette scrim; hairlines; no fake shadows). Debt: landing.css `.lp-nav` adds blur(10px) — the count doubles to 2, and sticky translucent nav bars are the canonical blur-soup starter; lockup alpha byte-verified clean (63.9% true transparency, anti-aliased edges, no fringe); landing card on the panel ladder with hairline borders. | 9.4 |
| 9 | Consistency & component quality (8%) | The system's rules were followed on the new surface (landing.css fully tokenized) and skipped inside the fix hunk itself (2 new inline-styled h3s at L1578/1581, 5 total; 43 inline styles; 28 onclick). esc census finally 11/11 clean — one long-standing ledger closed. R9-A means the same table-row idiom now has three different behaviors (conditional / dead / live) across tabs. | 9.3 |
| 10 | Mobile ergonomics (8%) | landing.css 430px + 719px passes verified (nav links hide, sponsor card stacks + 170px lockup, 50px CTA min-height, title 27px, RM + focus-visible preserved); in-app ≤430 floors (44px padding-only squeeze) unchanged from R7-2's verification; viewport-fit=cover + safe-area + 16px inputs intact. New surfaces add no truncation surface. (Static — no rendered-pixel pass under the no-Chrome rule.) | 9.6 |

## WEIGHTED TOTAL

identity 9.6×12% + type 9.4×12% + color 9.7×10% + layout 9.7×12% + density 9.5×12% +
interaction 9.3×10% + motion 9.7×8% + depth 9.4×8% + consistency 9.3×8% + mobile 9.6×8%
= 1.152 + 1.128 + 0.970 + 1.164 + 1.140 + 0.930 + 0.776 + 0.752 + 0.744 + 0.768
= **9.5 / 10** (unrounded 9.524)

Lineage: R3 7.3 → R4 8.4 → R5 8.4 → R6 8.8 → R7 9.4 → R8 9.5 → **R9 9.5**. Two of my three R8
fixes shipped and verified (esc ledger 11/11 — the R7-A class closed app-wide; dataStamp ticking).
The third shipped to the wrong sibling (R9-A), which is why interaction does not advance, and the
new landing buys identity/layout/color/layout while adding its own type-scale + blur debt. The
9.5 is flat-to-R8 but the underlying product is cleaner: two long-standing ledgers closed, the
dead-team crash path eliminated live, and the front door is now a real brand surface. Per-dimension
9.7 gate: color, layout, motion pass; five dimensions sit 9.3–9.6; interaction, consistency, depth,
type are the drag.

## The 3 cheapest fixes toward 9.7-per-dimension

1. **Finish R8-B on the two remaining families (~4 lines).** Analytics L2521 and `leaderSection`
   L282: wrap the same conditional already shipped at L1576 — `` `<tr ${p.player_id ? `onclick="selectPlayer('${p.team_id}','${p.player_id}')" class="link"` : ''}> `` — or gate the whole table on
   the GD-empty honesty pattern ("Player profiles unlock when stats post"). Both sites' live
   payloads are 100% null-id right now, so the defect is fully visible. **Δ interaction
   9.3→9.5, consistency 9.3→9.5 (weighted +0.044).**
2. **Retokenize landing.css literal sizes (~6 edits, one file).** Map 11→var(--mono-xs)+size or
   --mono-md 12, 12.5/13.5→12/14 on the mono scale, 15/17→16, 19→18/20, 26/27→26, 32→34, keep
   44 display. One new file inheriting the system instead of starting a second scale — and while
   in there, swap the 2 remaining inline h3s at L1578/1581 to `h3.section-h`. **Δ type 9.4→9.6,
   consistency 9.3→9.4 (weighted +0.030).**
3. **Blur the blur + one sponsor mark (~3 edits).** Replace `.lp-nav` `backdrop-filter: blur(10px)`
   with an opaque `--panel` bar (the app's other sticky surfaces are opaque; depth stays 1 blur),
   and point the Today-tab sponsor strip at `upright-lockup.png` so the crown and the lockup stop
   being two marks for one sponsor. **Δ depth 9.4→9.6 (weighted +0.016).**

Ceiling with all three: ≈ 9.58 weighted. The residual gap to 9.7-per-dimension is server-side
(`/api/players` 35.4s/5.6MB — gzip landed, paginate/warm still missing; client ceilings cannot
absorb it), the dataStamp "UPDATED" semantics (stamps session, not payload age), and preseason
thinness (all-zero standings/points), which the design now frames honestly almost everywhere.

## Residual credibility risks (static-verification limits)

- `/api/players` measured once (single-shot, 60s budget), not burst-tested; cold/warm not labeled.
- Gate a11y: `aria-modal` landing dialog without Escape handling (keydown census: Escape handled
  for palette + typeaheads only) and no focus trap — Tab-into-page-behind behavior unverified
  without a rendered browser.
- OG image still 512×512 square (platforms expect ~1200×630 — will crop/letterbox).
- The landing's marketing claims ("updating live", "5,900+ players") are true of the payload
  today but depend on the cron warm; a cold /api/players still contradicts "then it's instant".
- (static) No rendered-pixel verification under the no-Chrome constraint; contrast figures are
  computed from tokens, asset quality from byte-level PNG decoding + the fetched files.

VERDICT: 9.5/10
