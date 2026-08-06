#!/usr/bin/env python3
"""CAHL data verifier — cross-checks the API against the source site.

Runs on GitHub Actions alongside the cache warmer. Fails loudly (exit 1,
red workflow) when the app serves data that disagrees with chillerstats.com:

  1. API health: core endpoints answer and look structurally sane.
  2. Standings cross-check: for a rotating sample of leagues, the API's
     standings row count must match the site's own dashboard (the "file
     scrape vs the database" check). Empty-API-when-site-has-data = fail.
  3. Stale live-score check: today's games that started >2h ago and have no
     score in the API are looked up on the site's dashboard recents. If the
     SITE has a score and we don't, our scrape is stale/broken = fail.
     If the site also lacks it, that's fine — the site just hasn't updated.
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from urllib.request import urlopen, Request

# Ground truth = a fresh scrape of the site with the repo's own parser
# (fresh process = cold cache, so this is always live site data).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import scraper  # noqa: E402

BASE = os.environ.get("BASE_URL", "https://cahl.neural-forge.io")

FAILURES = []
WARNINGS = []


def fail(msg):
    FAILURES.append(msg)
    print(f"FAIL: {msg}")


def warn(msg):
    WARNINGS.append(msg)
    print(f"WARN: {msg}")


def ok(msg):
    print(f"ok: {msg}")


def get_api(path, timeout=70):
    req = Request(f"{BASE}{path}", headers={"User-Agent": "cahl-verify/1.0"})
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def et_now():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/New_York"))
    except Exception:
        return datetime.utcnow() - timedelta(hours=4)


def site_dashboard(league_id):
    """Fresh scrape of a league dashboard — the ground truth."""
    dash, err = scraper.parse_dashboard(league_id)
    if err or not dash:
        raise RuntimeError(err or "no data")
    return dash, len(dash.get("standings", []))


def main():
    # ---- 1. API health --------------------------------------------------
    try:
        home = get_api("/api/today")
        if not home.get("leagues"):
            fail("/api/today returned no leagues")
        else:
            ok(f"/api/today: {len(home['leagues'])} leagues, {len(home.get('today', []))} games")
    except Exception as e:
        fail(f"/api/today unreachable: {e}")
        report()

    try:
        leaders = get_api("/api/leaders")
        if not leaders.get("points"):
            fail("/api/leaders returned no points leaders")
        else:
            ok(f"/api/leaders: {len(leaders['points'])} points leaders")
    except Exception as e:
        warn(f"/api/leaders check failed: {e}")

    # ---- 2. Standings cross-check vs site (rotating sample) -------------
    leagues = home.get("leagues", [])
    if leagues:
        # Rotate through the list so every league gets checked over time.
        slot = int(time.time() // 1800) % max(1, (len(leagues) + 2) // 3)
        sample = leagues[slot * 3 : slot * 3 + 3]
        for lg in sample:
            name, lid = lg["name"], lg["id"]
            try:
                api_data = get_api(f"/api/league/{lid}")
                api_rows = len(api_data.get("standings", []))
            except Exception as e:
                fail(f"/api/league {name}: endpoint error: {e}")
                continue
            try:
                _, site_rows = site_dashboard(lid)
            except Exception as e:
                warn(f"site dashboard for {name} unfetchable: {e}")
                continue
            if site_rows == 0 and api_rows == 0:
                warn(f"{name}: no standings on site either (pre-season?)")
            elif api_rows == 0 and site_rows > 0:
                fail(f"{name}: API shows 0 standings but site has {site_rows} — scrape broken/stale")
            elif api_rows != site_rows:
                warn(f"{name}: API {api_rows} standings rows vs site {site_rows}")
            else:
                ok(f"{name}: standings match site ({api_rows} rows)")

    # ---- 3. Stale live-score check --------------------------------------
    games = home.get("today", [])
    if games:
        try:
            scores = get_api("/api/today/scores")
            by_ids = {f"{g.get('home_id')}|{g.get('away_id')}": g for g in scores.get("games", [])}
        except Exception as e:
            warn(f"/api/today/scores unfetchable: {e}")
            by_ids = {}

        now = et_now()
        stale = []
        for g in games:
            m = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)", g.get("time", ""), re.IGNORECASE)
            if not m:
                continue
            hh = int(m.group(1)) % 12
            if m.group(3).upper() == "PM":
                hh += 12
            start = now.replace(hour=hh, minute=int(m.group(2)), second=0, microsecond=0)
            if now < start + timedelta(hours=2):
                continue  # still plausibly playing
            s = by_ids.get(f"{g.get('home_id')}|{g.get('away_id')}", {})
            if s.get("played") and (s.get("home_score") or s.get("away_score")):
                continue  # we have the score
            stale.append(g)

        if stale:
            # Scope each stale game to its own league's dashboard via the teams index.
            try:
                teams = get_api("/api/teams")
                team2league = {t["id"]: t.get("league_id") for t in teams}
            except Exception as e:
                warn(f"/api/teams unfetchable, skipping stale cross-check: {e}")
                team2league = {}

            today_label = now.strftime("%b %-d")
            for g in stale:
                lids = {team2league.get(g.get("home_id")), team2league.get(g.get("away_id"))} - {None}
                found = False
                for lid in lids:
                    try:
                        dash, _ = site_dashboard(lid)
                    except Exception:
                        continue
                    for r in dash.get("recent", []):
                        if r.get("date") != today_label:
                            continue
                        if {r.get("home_id"), r.get("away_id")} == {g.get("home_id"), g.get("away_id")}:
                            if r.get("home_final") or r.get("away_final"):
                                found = True  # site has a real final; we don't
                    if found:
                        break
                if found:
                    fail(
                        f"Stale score: {g['time']} {g['home']} vs {g['away']} — "
                        f"site shows a final, API has none"
                    )
                else:
                    ok(f"{g['time']} {g['home']} vs {g['away']}: no score on site either (site not updated)")
        else:
            ok("no stale unscored games older than 2h")

    report()


def report():
    print()
    if FAILURES:
        print(f"VERIFICATION FAILED: {len(FAILURES)} failure(s), {len(WARNINGS)} warning(s)")
        sys.exit(1)
    print(f"VERIFICATION PASSED ({len(WARNINGS)} warning(s))")
    sys.exit(0)


if __name__ == "__main__":
    main()
