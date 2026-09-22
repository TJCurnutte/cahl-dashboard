import os
import json
import socket
import time
import concurrent.futures
from flask import Flask, jsonify, render_template, request

import scraper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static",
)


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _jsonify(data, err):
    if err:
        return jsonify({"error": err}), 502
    return jsonify(data)


@app.after_request
def no_cache_html(resp):
    # Always serve the shell fresh; static assets are versioned with ?v=N.
    if resp.content_type and resp.content_type.startswith("text/html"):
        resp.headers["Cache-Control"] = "no-store"
    # Live scores must not sit behind a CDN/browser cache.
    path = request.path or ""
    if path.startswith("/api/today"):
        resp.headers["Cache-Control"] = "no-store"
        resp.headers["Pragma"] = "no-cache"
    return resp


@app.route("/")
def index():
    """Landing page. Server-renders the live ticker, scoreboard card and stat
    band from caches/snapshots (never blocks on the network: falls back to
    static copy when caches are cold)."""
    ticker_items = ""
    ticker_label = "TONIGHT IN THE CAHL"
    hero_scorecard = ""
    stat_players = stat_teams = stat_leagues = ""
    games = []
    players = []
    try:
        # Games: prefer the warm scores memo, else parse the homepage once.
        if _SCORES_FLIGHT.get("result") and time.time() - _SCORES_FLIGHT.get("ts", 0) < 300:
            home = _SCORES_FLIGHT["result"]
        else:
            home, err = scraper.parse_homepage()
        games = (home or {}).get("today") or []

        # Indexes: snapshots first (7d), then in-memory caches.
        players = (_snapshot_load(_PLAYERS_SNAPSHOT, max_age_s=7 * 86400) or {}).get("players") \
            or _PLAYERS_CACHE.get("data") or []
        teams = _snapshot_load(_TEAMS_SNAPSHOT, max_age_s=7 * 86400) \
            or _TEAMS_CACHE.get("data") or []
        leagues = (home or {}).get("leagues") or []

        # Ticker: game scores/times, then league names.
        bits = []
        for g in games[:8]:
            hs, as_ = g.get("home_score"), g.get("away_score")
            score = f"{hs}\u2013{as_} " if hs is not None else ""
            bits.append(f"{score}{g.get('home', '')} vs {g.get('away', '')} · {g.get('time', '')}")
        for lg in leagues[:6]:
            bits.append(lg.get("name", ""))
        if bits:
            ticker_items = " &nbsp;●&nbsp; ".join(bits)
        ticker_track = (ticker_items + " &nbsp;●&nbsp; ") * 4 if ticker_items else ""

        # Scoreboard card: tonight's rows + league leader teaser.
        if games:
            rows = []
            for g in games[:3]:
                played = g.get("home_score") is not None
                score = (f'<span class="lp-hc-score">{g["home_score"]}\u2013{g["away_score"]}</span>'
                         if played else '<span class="lp-hc-time">' + (g.get("time") or "") + '</span>')
                rows.append(
                    f'<div class="lp-hc-row"><span class="lp-hc-teams">{g.get("home", "")} '
                    f'<span class="lp-hc-vs">vs</span> {g.get("away", "")}</span>{score}</div>')
            if players:
                top = max(players, key=lambda p: (p.get("pts") or 0))
                if top.get("pts"):
                    rows.append('<div class="lp-hc-row lp-hc-leader"><span class="lp-hc-teams">'
                                + 'LEAGUE LEADER: ' + (top.get("name") or "") + '</span>'
                                + '<span class="lp-hc-score">' + str(top.get("pts")) + ' PTS</span></div>')
            hero_scorecard = '<div class="lp-hc-rows">' + "".join(rows) + '</div>'
            if any(g.get("home_score") is not None for g in games):
                ticker_label = "LIVE SCORES"
        else:
            hero_scorecard = ('<div class="lp-hc-rows"><div class="lp-hc-empty">'
                              'Tonight\u2019s games are in the books. '
                              'The next slate posts here in the morning.</div></div>')
            ticker_label = "SEE YOU AT THE RINK"

        # Stat band.
        if players:
            stat_players = f"{len(players):,}"
        if teams:
            stat_teams = str(len(teams))
        if leagues:
            stat_leagues = str(len(leagues))
    except Exception:
        pass
    return render_template("index.html", ticker_items=ticker_track,
                           hero_scorecard=hero_scorecard, ticker_label=ticker_label,
                           stat_players=stat_players or "5,900",
                           stat_teams=stat_teams or "250",
                           stat_leagues=stat_leagues or "27")


@app.route("/api/today")
def today():
    # Fast path: homepage only. Scores come from /api/today/scores so the page
    # paints immediately instead of waiting on 30 dashboard fetches.
    data, err = scraper.parse_homepage()
    if err:
        return jsonify({"error": err}), 502
    return jsonify(data)


_SCORES_COND = __import__("threading").Condition()
_SCORES_FLIGHT = {"result": None, "ts": 0.0, "inflight": False, "gen": 0}
_SCORES_MEMO_S = 20  # serve cached result to pollers within this window


_LAST_GOOD_PATH = "/tmp/cahl-last-good.json"

def _save_last_good(payload):
    try:
        with open(_LAST_GOOD_PATH, "w") as f:
            json.dump({"ts": time.time(), "payload": payload}, f)
    except Exception:
        pass

def _load_last_good():
    try:
        with open(_LAST_GOOD_PATH) as f:
            blob = json.load(f)
        return blob
    except Exception:
        return None

def _today_scores_compute():
    """Shared body: parse homepage + enrich with live scores. Raises on hard error."""
    data, err = scraper.parse_homepage()
    if err:
        # Last-known-data fallback: when the source site blocks/slow-fails, serve the
        # most recent good snapshot instead of a hard error. The UI shows an "as of"
        # note so nobody mistakes stale data for live data.
        last = _load_last_good()
        if last and time.time() - last.get("ts", 0) < 26 * 3600:
            payload = dict(last.get("payload") or {})
            payload["_stale"] = True
            payload["_staleAsOf"] = time.strftime("%b %d, %I:%M %p ET", time.gmtime(last.get("ts", 0) - 4 * 3600))
            payload["_notice"] = str(err)
            return payload  # NOT raising — the site degrades gracefully
        raise RuntimeError(err)
    try:
        league_ids = None
        if _TEAMS_CACHE["data"]:
            by_id = {t["id"]: t["league_id"] for t in _TEAMS_CACHE["data"]}
            league_ids = set()
            for g in data.get("today", []):
                for tid in (g.get("home_id"), g.get("away_id")):
                    if tid in by_id:
                        league_ids.add(by_id[tid])
            if not league_ids:
                league_ids = None
        scraper.enrich_today_scores(data, league_ids=league_ids, timeout=45, fresh=True)
    except Exception as e:
        print(f"[today_scores] enrich failed: {e}")  # never swallow silently
    return {"games": data.get("today", [])}


@app.route("/api/today/scores")
def today_scores():
    """Live/final scores for today's games (separate slower path).
    Single-flight: the first requester computes; concurrent pollers wait for
    that result (or reuse a fresh one) instead of stampeding the source site —
    the stampede is what made live scores stick for everyone at once."""
    now = time.time()
    my_gen = None
    with _SCORES_COND:
        if (_SCORES_FLIGHT["result"] is not None
                and now - _SCORES_FLIGHT["ts"] < _SCORES_MEMO_S):
            return jsonify(_SCORES_FLIGHT["result"])
        if _SCORES_FLIGHT["inflight"]:
            my_gen = _SCORES_FLIGHT["gen"]
            # Wait up to ~55s for the in-flight computation to land.
            _SCORES_COND.wait(timeout=55)
            f = _SCORES_FLIGHT
            if (f["result"] is not None and f["gen"] != my_gen
                    and time.time() - f["ts"] < 90):
                return jsonify(f["result"])
            # Timed out or stale — fall through and compute our own.
            if _SCORES_FLIGHT["inflight"]:
                my_gen = None  # we'll compute; first-completed wins the memo
        if my_gen is None:
            _SCORES_FLIGHT["inflight"] = True
            _SCORES_FLIGHT["gen"] += 1
    try:
        payload = _today_scores_compute()
    except RuntimeError as e:
        with _SCORES_COND:
            if _SCORES_FLIGHT["inflight"]:
                _SCORES_FLIGHT["inflight"] = False
                _SCORES_COND.notify_all()
        return jsonify({"error": str(e)}), 502
    with _SCORES_COND:
        _SCORES_FLIGHT["result"] = payload
        _SCORES_FLIGHT["ts"] = time.time()
        _SCORES_FLIGHT["inflight"] = False
    _save_last_good(payload)
    with _SCORES_COND:
        _SCORES_FLIGHT["gen"] += 1
        _SCORES_COND.notify_all()
    return jsonify(payload)


@app.route("/api/leaders")
def leaders():
    data, err = scraper.parse_all_leaders()
    return _jsonify(data, err)


@app.route("/api/league/<league_id>")
def league(league_id):
    data, err = scraper.parse_dashboard(league_id)
    return _jsonify(data, err)


@app.route("/api/team/<team_id>")
def team(team_id):
    # Fetch team sub-pages in parallel to keep the dashboard snappy.
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        f_over = ex.submit(scraper.parse_team_overview, team_id)
        f_sched = ex.submit(scraper.parse_team_schedule, team_id)
        f_stats = ex.submit(scraper.parse_team_stats, team_id)
        f_stand = ex.submit(scraper.parse_team_standings, team_id)
        f_sessions = ex.submit(_sessions_for_team, team_id)

        over, e1 = f_over.result()
        sched, e2 = f_sched.result()
        stats, e3 = f_stats.result()
        stand, e4 = f_stand.result()
        sessions_data, e5 = f_sessions.result()

    err = e1 or e2 or e3 or e4
    if err:
        return jsonify({"error": err}), 502

    team_row = next((s for s in (stand or []) if s.get("team_id") == team_id), None)

    race = {}
    team_race = None
    playoffs = []
    championship = None
    season = (over or {}).get("season") or ""
    league_name = ""
    if not e5 and sessions_data:
        cutoff = sessions_data.get("playoff_cutoff")
        race = scraper.compute_playoff_race(stand or [], len(sched or []), cutoff)
        team_race = race.get(team_id)
        playoffs = sessions_data.get("playoffs", [])
        championship = sessions_data.get("championship")
        season = sessions_data.get("season") or season
        league_name = sessions_data.get("league_name") or ""

    form = scraper.compute_team_form(sched or [], team_id, team_row)
    team_name = (over or {}).get("team_name") or ""
    awards = scraper.awards_for_team(team_id, team_name, championship, stats)
    previous_sessions = []  # ChillerStats does not publish prior session W-L on team pages

    current_session = None
    if season or (form and form.get("played")):
        current_session = {
            "label": season or "Current session",
            "record": form.get("record") if form else None,
            "w": form.get("wins") if form else None,
            "l": form.get("losses") if form else None,
            "otl": form.get("otl") if form else None,
            "ties": form.get("ties") if form else None,
            "points": form.get("points") if form else None,
        }

    return jsonify({
        "overview": over,
        "schedule": sched,
        "roster": stats,
        "standings": stand,
        "form": form,
        "race": team_race,
        "playoffs": playoffs,
        "season": season,
        "league_name": league_name,
        "championship": championship,
        "awards": awards,
        "current_session": current_session,
        "previous_sessions": previous_sessions,
    })


_HISTORY_CACHE = {}
_HISTORY_TTL = 21600  # 6 hours; past sessions rarely change


@app.route("/api/team/<team_id>/history")
def team_history(team_id):
    """Previous-session W-L-OTL and championship/1st-place awards.

    Separate from /api/team so the main team page is never blocked on
    roster fan-out. Cached aggressively; partial results are not stored.
    """
    import time
    now = time.time()
    cached = _HISTORY_CACHE.get(team_id)
    if cached and now - cached["ts"] < _HISTORY_TTL:
        return jsonify(cached["data"])
    data, err = scraper.parse_team_history(team_id, timeout=20)
    if err:
        return jsonify({"error": err, "previous": [], "awards": [], "sessions": []}), 502
    payload = data or {"previous": [], "awards": [], "sessions": []}
    if data and not data.get("partial"):
        _HISTORY_CACHE[team_id] = {"data": payload, "ts": now}
    return jsonify(payload)


def _all_teams_cached(timeout=None):
    """The /api/teams aggregate, using its 5-minute cache (disk-hydrated on cold)."""
    import time
    now = time.time()
    if _TEAMS_CACHE["data"] is not None and now - _TEAMS_CACHE["ts"] < _TEAMS_TTL:
        return _TEAMS_CACHE["data"], None
    # Cold instance: hydrate from Supabase first, then the on-disk crawl
    # snapshot (<=7 days). Players-index seeding depends on this team list.
    if _TEAMS_CACHE["data"] is None:
        sb, ok = _sb_read("teams_index")
        if ok and isinstance(sb, list) and sb:
            _TEAMS_CACHE["data"] = sb
            _TEAMS_CACHE["ts"] = now
            return sb, None
        snap = _snapshot_load(_TEAMS_SNAPSHOT, max_age_s=7 * 86400)
        if isinstance(snap, list) and snap:
            _TEAMS_CACHE["data"] = snap
            _TEAMS_CACHE["ts"] = now
            return snap, None
    kw = {} if timeout is None else {"timeout": timeout}
    data, err = scraper.parse_all_teams(**kw)
    if err and not data:
        # Fall back to the (possibly stale) snapshot rather than failing hard —
        # a 7-day-old team list beats a 502 for every downstream endpoint.
        snap = _snapshot_load(_TEAMS_SNAPSHOT, max_age_s=30 * 86400)
        if isinstance(snap, list) and snap:
            return snap, None
        return None, err
    if data:
        _TEAMS_CACHE["data"] = data
        _TEAMS_CACHE["ts"] = now
        _snapshot_save(_TEAMS_SNAPSHOT, data)
        _sb_write("teams_index", data)
    return data, None


def _sessions_for_team(team_id):
    """Sessions for the team's league (for race calc); league found via the teams cache."""
    teams_data, err = _all_teams_cached()
    if err:
        return None, err
    match = next((t for t in teams_data if t["id"] == team_id), None)
    if not match:
        return None, "league not found for team"
    league_id = match["league_id"]
    sessions_data, e2 = scraper.parse_league_sessions(league_id)
    if e2:
        return None, e2
    dash, e3 = scraper.parse_dashboard(league_id)
    if not e3:
        sessions_data["playoffs"] = dash.get("playoffs", [])
        sessions_data["playoff_cutoff"] = dash.get("playoff_cutoff")
        sessions_data["championship"] = dash.get("championship")
        sessions_data["season"] = dash.get("season") or sessions_data.get("season")
        sessions_data["league_name"] = dash.get("league_name") or sessions_data.get("league_name")
    return sessions_data, None


_TEAMS_CACHE = {"data": None, "ts": 0}
_TEAMS_TTL = 900  # 15 minutes; aggregating 30 league pages is expensive


@app.route("/api/teams")
def teams():
    import time
    now = time.time()
    if _TEAMS_CACHE["data"] is not None and now - _TEAMS_CACHE["ts"] < _TEAMS_TTL:
        return jsonify(_TEAMS_CACHE["data"])
    data, err = scraper.parse_all_teams()
    if err:
        return jsonify({"error": err}), 502
    if data:
        _TEAMS_CACHE["data"] = data
        _TEAMS_CACHE["ts"] = now
    return jsonify(data or [])


_PLAYERS_CACHE = {"data": None, "ts": 0, "partial": False}
_PLAYERS_TTL = 3600  # 1 hour; matches the hourly cron baseline that re-warms it.
_PLAYERS_COND = __import__("threading").Condition()
_PLAYERS_FLIGHT = {"inflight": False, "t0": 0.0, "waiters": 0}

# ---- Disk-backed index snapshot (R10: "store all the names on the site") ----
# The in-process cache dies with every cold instance; a full rebuild fans out to
# ~60 rosters and takes 20-40s. We snapshot the completed index to /tmp after
# every successful build and load it back at boot / on cold cache, so any warm
# instance answers instantly and a fresh instance starts from the last known
# complete index instead of an empty one.
_PLAYERS_SNAPSHOT = "/tmp/cahl_players_index.json"
_TEAMS_SNAPSHOT = "/tmp/cahl_teams_index.json"

# ---- Supabase persistent store (cross-instance, survives cold boots) ----
# PostgREST direct over HTTPS — no SDK dependency. Feature-flagged: inert
# unless SUPABASE_URL + SUPABASE_SERVICE_KEY are set in the environment.
# Table: cahl_cache(key text pk, payload jsonb, updated_at timestamptz).
import urllib.request as _ureq


def _sb_config():
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
    return (url, key) if url and key else (None, None)


def _sb_read(key, timeout=8):
    """Fetch a cached payload from Supabase. Returns (data, ok)."""
    url, key_env = _sb_config()
    if not url:
        return None, False
    try:
        req = _ureq.Request(
            f"{url}/rest/v1/cahl_cache?select=payload,updated_at&key=eq.{key}",
            headers={"apikey": key_env, "Authorization": f"Bearer {key_env}"},
        )
        with _ureq.urlopen(req, timeout=timeout) as resp:
            rows = json.loads(resp.read().decode())
        if rows and isinstance(rows[0].get("payload"), (dict, list)):
            return rows[0]["payload"], True
    except Exception:
        pass
    return None, False


def _sb_write(key, payload, timeout=15):
    """Upsert a payload into Supabase. Fire-and-forget semantics."""
    url, key_env = _sb_config()
    if not url:
        return False
    try:
        req = _ureq.Request(
            f"{url}/rest/v1/cahl_cache?on_conflict=key",
            data=json.dumps({"key": key, "payload": payload,
                             "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())}).encode(),
            headers={"apikey": key_env, "Authorization": f"Bearer {key_env}",
                     "Content-Type": "application/json",
                     "Prefer": "resolution=merge-duplicates"},
            method="POST",
        )
        with _ureq.urlopen(req, timeout=timeout) as resp:
            resp.read()
        return True
    except Exception:
        return False


def _snapshot_save(path, payload):
    """Best-effort atomic snapshot write; failures never break the request."""
    try:
        tmp = path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(payload, fh, separators=(",", ":"))
        os.replace(tmp, path)
    except Exception:
        pass


def _snapshot_load(path, max_age_s):
    """Load a snapshot if it exists and is fresh enough. Returns data or None."""
    try:
        if os.path.exists(path) and time.time() - os.path.getmtime(path) <= max_age_s:
            with open(path) as fh:
                return json.load(fh)
    except Exception:
        pass
    return None


def _players_snapshot_load():
    """Seed the in-memory players cache from the last completed build (<=7d)."""
    snap = _snapshot_load(_PLAYERS_SNAPSHOT, max_age_s=7 * 86400)
    if isinstance(snap, dict) and isinstance(snap.get("players"), list) and snap["players"]:
        _PLAYERS_CACHE["data"] = snap["players"]
        _PLAYERS_CACHE["ts"] = snap.get("ts", time.time())
        _PLAYERS_CACHE["partial"] = False
        return True
    return False


def _merge_player_index(entries):
    """Warm the players cache with whatever rosters we have so far."""
    import time
    if not entries:
        return
    existing = {f"{p['name'].lower()}|{p.get('team_id')}": p for p in (_PLAYERS_CACHE["data"] or [])}
    existing.update(entries)
    data = sorted(existing.values(), key=lambda p: p["name"].lower())
    _PLAYERS_CACHE["data"] = data
    _PLAYERS_CACHE["ts"] = time.time()
    _PLAYERS_CACHE["partial"] = True


@app.route("/api/players/lookup")
def players_lookup():
    """Name search that must return without a 50s roster fan-out."""
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify({"players": [], "partial": False})
    ql = q.lower()
    cached = _PLAYERS_CACHE.get("data")
    if cached:
        hits = [p for p in cached if ql in (p.get("name") or "").lower() or ql in (p.get("team") or "").lower()]
        if hits:
            return jsonify({"players": hits[:25], "partial": bool(_PLAYERS_CACHE.get("partial"))})
        if not _PLAYERS_CACHE.get("partial") and cached:
            return jsonify({"players": [], "partial": False})

    teams_data, err = _all_teams_cached(timeout=20)
    if err:
        return jsonify({"error": err, "players": []}), 502
    hits, partial, indexed, serr = scraper.search_players(q, teams_data, timeout=32)
    if indexed:
        _merge_player_index(indexed)
        if not partial:
            _PLAYERS_CACHE["partial"] = False
    if serr and not hits:
        return jsonify({"error": serr, "players": []}), 502
    return jsonify({
        "players": hits[:25],
        "partial": partial,
        "fetched": len(indexed),
        "total": len(teams_data or []),
    })


@app.route("/api/players")
def players():
    """Every player on every team across all leagues (for the full leaderboard)."""
    import time
    from concurrent.futures import ThreadPoolExecutor
    now = time.time()
    if (_PLAYERS_CACHE["data"] is not None
            and now - _PLAYERS_CACHE["ts"] < _PLAYERS_TTL
            and not _PLAYERS_CACHE.get("partial")):
        return jsonify({"players": _PLAYERS_CACHE["data"], "partial": False})

    # Cold instance: hydrate from Supabase (cross-instance, always fresh) or
    # the local on-disk snapshot, before fanning out to ~60 rosters. Turns most
    # cold starts from 30-60s into well under a second.
    if _PLAYERS_CACHE["data"] is None:
        sb, ok = _sb_read("players_index")
        if ok and isinstance(sb.get("players"), list) and sb["players"]:
            _PLAYERS_CACHE["data"] = sb["players"]
            _PLAYERS_CACHE["ts"] = now
            _PLAYERS_CACHE["partial"] = False
            return jsonify({"players": sb["players"], "partial": False,
                            "from_supabase": True})
        if _players_snapshot_load():
            return jsonify({"players": _PLAYERS_CACHE["data"], "partial": False,
                            "from_snapshot": True})

    # Single-flight: one rebuild at a time; concurrent requests wait for the
    # in-flight rebuild instead of each fanning out to ~60 rosters (the
    # stampede is what made the leaderboard stick for everyone at once).
    with _PLAYERS_COND:
        if _PLAYERS_FLIGHT["inflight"] and now - _PLAYERS_FLIGHT["t0"] < 115:
            _PLAYERS_FLIGHT["waiters"] += 1
            _PLAYERS_COND.wait(timeout=110)
            _PLAYERS_FLIGHT["waiters"] -= 1
            c = _PLAYERS_CACHE
            if (c["data"] is not None and time.time() - c["ts"] < _PLAYERS_TTL
                    and not c.get("partial")):
                return jsonify({"players": c["data"], "partial": False})
            # timed out without a complete cache — compute our own below
        _PLAYERS_FLIGHT["inflight"] = True
        _PLAYERS_FLIGHT["t0"] = time.time()
    try:
        return _players_rebuild(now)
    finally:
        with _PLAYERS_COND:
            _PLAYERS_FLIGHT["inflight"] = False
            _PLAYERS_COND.notify_all()


def _players_rebuild(now):
    from concurrent.futures import ThreadPoolExecutor
    teams_data, err = _all_teams_cached()
    if err:
        return jsonify({"error": err}), 502

    index = {}
    errors = []
    idx_lock = __import__("threading").Lock()

    def fetch(team):
        try:
            roster, e = scraper.parse_team_stats(team["id"])
        except Exception as ex:
            errors.append(str(ex))
            return
        if e:
            errors.append(e)
            return
        # Workers can still be running when the soft timeout fires and the
        # main thread sorts/serializes `index` — guard it like search does.
        with idx_lock:
            scraper.index_roster(team, roster, index)

    # Keep this well under the function limit so the UI can clear loading.
    # ?full=1 (cron warm) gets a much longer window to finish every roster.
    SOFT_TIMEOUT = 90 if request.args.get("full") else 18
    ex = ThreadPoolExecutor(max_workers=16)
    futures = [ex.submit(fetch, team) for team in teams_data]
    done, pending = concurrent.futures.wait(futures, timeout=SOFT_TIMEOUT)
    complete = not pending
    ex.shutdown(wait=False, cancel_futures=True)

    if not index and errors and not done:
        cached = _PLAYERS_CACHE.get("data") or []
        if cached:
            return jsonify({"players": cached, "partial": True, "error": "; ".join(errors[:3])})
        return jsonify({"error": "; ".join(errors[:3]), "players": []}), 502

    # Snapshot under the lock: stragglers from timed-out futures may still be
    # inserting while we sort — "dictionary changed size during iteration" 500.
    with idx_lock:
        snapshot = list(index.values())
    # Wire-size trim: drop zero/empty stat fields per player. Clients already
    # coerce missing to 0 (p.pts || 0 patterns everywhere); preseason rosters
    # are 94% zeros, which dominated the 5.8MB payload.
    for p in snapshot:
        for k in [k for k, v in p.items() if v in (0, None, "", "-") and k != "name"]:
            del p[k]
    data = sorted(snapshot, key=lambda p: p["name"].lower())
    # Never cache an empty result as "complete" — one bad cycle would poison
    # lookups and the leaderboard for the whole TTL.
    if data:
        _PLAYERS_CACHE["data"] = data
        _PLAYERS_CACHE["ts"] = now
        _PLAYERS_CACHE["partial"] = not complete
        # Snapshot only COMPLETE builds — a partial snapshot would advertise
        # stale completeness forever (5.8MB write is ~50ms on the warm path).
        if complete:
            _snapshot_save(_PLAYERS_SNAPSHOT, {"ts": now, "players": data})
            _sb_write("players_index", {"ts": now, "players": data})
    elif not complete:
        cached = _PLAYERS_CACHE.get("data") or []
        if cached:
            return jsonify({"players": cached, "partial": True})
    return jsonify({
        "players": data,
        "partial": not complete,
        "fetched": len(done),
        "total": len(teams_data),
    })


_SESSIONS_CACHE = {}
_SESSIONS_TTL = 300  # 5 minutes; aggregating every team's schedule is expensive


@app.route("/api/sessions/<league_id>")
def sessions(league_id):
    import time
    now = time.time()
    cached = _SESSIONS_CACHE.get(league_id)
    if cached and now - cached["ts"] < _SESSIONS_TTL:
        return jsonify(cached["data"])
    data, err = scraper.parse_league_sessions(league_id)
    if err:
        return jsonify({"error": err}), 502
    _SESSIONS_CACHE[league_id] = {"data": data, "ts": now}
    return jsonify(data)


@app.route("/api/player/<team_id>/<player_id>")
def player(team_id, player_id):
    data, err = scraper.parse_player_history(team_id, player_id)
    return _jsonify(data, err)


@app.route("/api/game-log/<team_id>")
def game_log(team_id):
    """Per-game G/A/Pts/PIM log for one player, built from score sheets."""
    from urllib.parse import unquote
    player = unquote(request.args.get("player", "")).strip()
    team_name = unquote(request.args.get("team", "")).strip()
    if not player or not team_name:
        return jsonify({"error": "player and team query params required"}), 400
    sched, err = scraper.parse_team_schedule(team_id)
    if err:
        return jsonify({"error": err}), 502
    entries, err2 = scraper.compute_player_game_log(sched or [], player, team_name)
    if err2:
        return jsonify({"error": err2}), 502
    return jsonify({"player": player, "team": team_name, "games": entries})


@app.route("/api/player-token/<token>")
def player_token(token):
    data, err = scraper.parse_player_history_by_token(token)
    return _jsonify(data, err)


@app.route("/api/version")
def version():
    """Frontend version for the self-heal freshness check (parsed from app.js)."""
    import re as _re
    try:
        src = open(os.path.join(BASE_DIR, "static", "js", "app.js")).read()
        m = _re.search(r"JS_VERSION\s*=\s*(\d+)", src)
        return jsonify({"js": int(m.group(1)) if m else 0})
    except Exception:
        return jsonify({"js": 0})


@app.route("/api/client-error", methods=["POST"])
def client_error():
    """Client-side error telemetry: the browser POSTs {message, stack, href,
    version} here when a render crash escapes (e.g. RangeError stack overflows
    that only reproduce in specific browsers). Appends one JSON line per event
    to /tmp/cahl_client_errors.log (best-effort; never blocks the client)."""
    try:
        payload = request.get_json(silent=True) or {}
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "message": str(payload.get("message", ""))[:300],
            "stack": str(payload.get("stack", ""))[:2000],
            "href": str(payload.get("href", ""))[:200],
            "version": payload.get("version", 0),
            "ua": str(request.headers.get("User-Agent", ""))[:200],
        }
        with open("/tmp/cahl_client_errors.log", "a") as fh:
            fh.write(json.dumps(entry) + "\n")
    except Exception:
        pass
    return jsonify({"ok": True})


@app.route("/api/refresh", methods=["POST"])
def refresh():
    """scope=scores (cron): light refresh of page-level caches only, leaving the big
    aggregates (players/teams indexes) intact. scope=all (manual): full force refresh."""
    scope = request.args.get("scope", "all")
    scraper.clear_cache()
    _SESSIONS_CACHE.clear()
    _HISTORY_CACHE.clear()
    if scope == "all":
        _TEAMS_CACHE["data"] = None
        _TEAMS_CACHE["ts"] = 0
        _PLAYERS_CACHE["data"] = None
        _PLAYERS_CACHE["ts"] = 0
        _PLAYERS_CACHE["partial"] = False
    return jsonify({"ok": True, "scope": scope})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 0)) or find_free_port()
    print(f"\nCAHL Dashboard running at http://127.0.0.1:{port}\n")
    app.run(host="127.0.0.1", port=port, threaded=True, debug=False)
