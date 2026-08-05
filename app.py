import os
import socket
import concurrent.futures
from flask import Flask, jsonify, render_template

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
    return resp


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/today")
def today():
    data, err = scraper.parse_homepage()
    if err:
        return jsonify({"error": err}), 502
    # Fill in scores for tonight's games once they've started (uses cached schedules)
    try:
        scraper.enrich_today_scores(data)
    except Exception:
        pass  # scores are best-effort; schedule still renders
    return jsonify(data)


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
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        f_over = ex.submit(scraper.parse_team_overview, team_id)
        f_sched = ex.submit(scraper.parse_team_schedule, team_id)
        f_stats = ex.submit(scraper.parse_team_stats, team_id)
        f_stand = ex.submit(scraper.parse_team_standings, team_id)

        over, e1 = f_over.result()
        sched, e2 = f_sched.result()
        stats, e3 = f_stats.result()
        stand, e4 = f_stand.result()

    err = e1 or e2 or e3 or e4
    if err:
        return jsonify({"error": err}), 502

    team_row = next((s for s in (stand or []) if s.get("team_id") == team_id), None)
    return jsonify({
        "overview": over,
        "schedule": sched,
        "roster": stats,
        "standings": stand,
        "form": scraper.compute_team_form(sched or [], team_id, team_row),
    })


_TEAMS_CACHE = {"data": None, "ts": 0}
_TEAMS_TTL = 300  # 5 minutes; aggregating 30 league pages is expensive


@app.route("/api/teams")
def teams():
    import time
    now = time.time()
    if _TEAMS_CACHE["data"] is not None and now - _TEAMS_CACHE["ts"] < _TEAMS_TTL:
        return jsonify(_TEAMS_CACHE["data"])
    data, err = scraper.parse_all_teams()
    if err:
        return jsonify({"error": err}), 502
    _TEAMS_CACHE["data"] = data
    _TEAMS_CACHE["ts"] = now
    return jsonify(data)


_PLAYERS_CACHE = {"data": None, "ts": 0}
_PLAYERS_TTL = 900  # 15 minutes; rosters change slowly, fan-out is expensive


@app.route("/api/players")
def players():
    """Every player on every team across all leagues (for the player lookup)."""
    import time
    from concurrent.futures import ThreadPoolExecutor
    now = time.time()
    if _PLAYERS_CACHE["data"] is not None and now - _PLAYERS_CACHE["ts"] < _PLAYERS_TTL:
        return jsonify(_PLAYERS_CACHE["data"])

    teams_data, err = scraper.parse_all_teams()
    if err:
        return jsonify({"error": err}), 502

    index = {}
    errors = []

    def fetch(team):
        roster, e = scraper.parse_team_stats(team["id"])
        if e:
            errors.append(e)
            return
        if not roster:
            return
        for sec in roster.get("sections", []):
            for p in sec["players"]:
                key = f"{p['name'].lower()}|{team['id']}"
                index[key] = {
                    "name": p["name"],
                    "team": team["name"],
                    "team_id": team["id"],
                    "league_id": team["league_id"],
                    "league_name": team["league_name"],
                    "position": p.get("position") or sec["label"],
                    "jersey": p.get("jersey", "-"),
                    "token": p.get("token"),
                    "gp": p.get("gp", 0),
                    "g": p.get("g", 0),
                    "a": p.get("a", 0),
                    "pts": p.get("pts", 0),
                    "pim": p.get("pim", 0),
                }
        for g in roster.get("goalies", []):
            key = f"{g['name'].lower()}|{team['id']}"
            index[key] = {
                "name": g["name"],
                "team": team["name"],
                "team_id": team["id"],
                "league_id": team["league_id"],
                "league_name": team["league_name"],
                "position": "Goalie",
                "jersey": g.get("jersey", "-"),
                "token": g.get("token"),
                "gp": g.get("gp", 0),
                "g": 0,
                "a": 0,
                "pts": 0,
                "pim": 0,
                "w": g.get("w", 0),
                "l": g.get("l", 0),
                "otl": g.get("otl", 0),
                "ga": g.get("ga", 0),
                "gaa": g.get("gaa", 0),
            }

    with ThreadPoolExecutor(max_workers=10) as ex:
        list(ex.map(fetch, teams_data))

    if not index and errors:
        return jsonify({"error": "; ".join(errors[:3])}), 502

    data = sorted(index.values(), key=lambda p: p["name"].lower())
    _PLAYERS_CACHE["data"] = data
    _PLAYERS_CACHE["ts"] = now
    return jsonify(data)


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


@app.route("/api/player-token/<token>")
def player_token(token):
    data, err = scraper.parse_player_history_by_token(token)
    return _jsonify(data, err)


@app.route("/api/refresh", methods=["POST"])
def refresh():
    scraper.clear_cache()
    _TEAMS_CACHE["data"] = None
    _TEAMS_CACHE["ts"] = 0
    _PLAYERS_CACHE["data"] = None
    _PLAYERS_CACHE["ts"] = 0
    _SESSIONS_CACHE.clear()
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 0)) or find_free_port()
    print(f"\nCAHL Dashboard running at http://127.0.0.1:{port}\n")
    app.run(host="127.0.0.1", port=port, threaded=True, debug=False)
