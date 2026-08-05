import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from html import unescape

BASE_URL = "http://www.chillerstats.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

session = requests.Session()
session.headers.update(HEADERS)


class Cache:
    def __init__(self, ttl=60):
        self.ttl = ttl
        self.store = {}

    def get(self, key):
        if key in self.store:
            value, exp = self.store[key]
            if time.time() < exp:
                return value
            del self.store[key]
        return None

    def set(self, key, value):
        self.store[key] = (value, time.time() + self.ttl)

    def clear(self):
        self.store.clear()


cache = Cache(ttl=60)


def _url(path):
    if path.startswith("http"):
        return path
    return f"{BASE_URL}/{path.lstrip('/')}"


def get_soup(path):
    key = f"html:{path}"
    text = cache.get(key)
    if text is None:
        try:
            resp = session.get(_url(path), timeout=30)
            resp.raise_for_status()
            text = resp.text
            cache.set(key, text)
        except Exception as e:
            return None, str(e)
    return BeautifulSoup(text, "html.parser"), None


def clear_cache():
    cache.clear()


def _text(el):
    if not el:
        return ""
    return unescape(el.get_text(strip=True))


def _extract_id(href, field):
    if not href:
        return None
    m = re.search(rf"{field}=([^&\"]+)", href)
    return m.group(1) if m else None


def _team_id(href):
    return _extract_id(href, "TeamID")


def _player_id(href):
    return _extract_id(href, "PlayerID")


def _score_to_int(s):
    s = s.strip() if s else ""
    return int(s) if s.isdigit() else 0


def parse_homepage():
    soup, err = get_soup("/")
    if err:
        return None, err

    today = []
    leagues = []

    # Find Today's Games carousel article
    article = None
    for a in soup.find_all("article", class_="item"):
        h2 = a.find("h2")
        if h2 and "Today" in h2.get_text():
            article = a
            break

    if article:
        # Game pairs are inside .row elements directly under .carousel-caption.
        caption = article.find("div", class_="carousel-caption")
        if caption:
            rows = caption.find_all("div", class_="row", recursive=False)
            for row in rows:
                for blk in row.find_all("div", class_="col-sm-4", recursive=False):
                    info_divs = blk.find_all("div", recursive=False)
                    if len(info_divs) < 2:
                        continue
                    meta = _text(info_divs[0])
                    m = re.match(r"(\d{1,2}:\d{2}\s*(?:AM|PM))\s*-\s*(.+)", meta, re.IGNORECASE)
                    gametime = m.group(1) if m else meta
                    facility = m.group(2).strip() if m else ""

                    matchup = info_divs[1]
                    links = matchup.find_all("a", href=True)
                    if len(links) >= 2:
                        home = _text(links[0])
                        home_id = _team_id(links[0]["href"])
                        away = _text(links[1])
                        away_id = _team_id(links[1]["href"])
                    else:
                        text = _text(matchup)
                        parts = [p.strip() for p in text.split("vs.")]
                        home = parts[0] if len(parts) > 0 else ""
                        away = parts[1] if len(parts) > 1 else ""
                        home_id = away_id = None

                    # Deduplicate; the site sometimes repeats the last game row.
                    key = (gametime, facility, home, away)
                    if any((g["time"], g["facility"], g["home"], g["away"]) == key for g in today):
                        continue

                    today.append({
                        "time": gametime,
                        "facility": facility,
                        "home": home,
                        "home_id": home_id,
                        "away": away,
                        "away_id": away_id,
                    })

    # All dashboard links from the league selectors
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "dashboard.cfm?LeagueID=" in href:
            lid = _extract_id(href, "LeagueID")
            if lid and lid not in seen:
                seen.add(lid)
                txt = _text(a)
                leagues.append({
                    "id": lid,
                    "name": txt,
                })

    return {"today": today, "leagues": leagues}, None


def parse_all_leaders():
    soup, err = get_soup("/all_leaders.cfm")
    if err:
        return None, err

    result = {"points": [], "goals": [], "assists": []}
    table_map = {
        "pts": ("points", "points"),
        "goals": ("goals", "goals"),
        "asst": ("assists", "assists"),
    }

    for table_id, (key, val_key) in table_map.items():
        table = soup.find("table", {"id": table_id})
        if not table:
            continue
        rows = table.find("tbody").find_all("tr") if table.find("tbody") else []
        for i, row in enumerate(rows, 1):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            name_link = cells[0].find("a", href=True)
            team_link = cells[1].find("a", href=True)
            player_id = _player_id(name_link["href"]) if name_link else None
            team_id = _team_id(team_link["href"]) if team_link else None
            result[key].append({
                "rank": i,
                "name": _text(name_link) if name_link else _text(cells[0]),
                "team": _text(team_link) if team_link else _text(cells[1]),
                "team_id": team_id,
                "player_id": player_id,
                val_key: _score_to_int(_text(cells[2])),
            })

    return result, None


def _team_from_link(link):
    return {"name": _text(link), "id": _team_id(link.get("href", ""))} if link else {"name": "", "id": None}


def _parse_games_section(soup, section_heading):
    games = []
    # Find a section by heading text
    headings = soup.find_all(lambda t: t.name in ("h1", "h2") and section_heading in t.get_text())
    for h in headings:
        section = h.find_parent("section") or h.find_parent("div", class_="row")
        if not section:
            section = h.parent
        # Look for repeated game blocks
        for row in section.find_all("div", class_="row"):
            cells = row.find_all("div")
            if len(cells) < 2:
                continue
            # One of the divs may contain an icon and another the text
            text_div = None
            for c in cells:
                if c.find("i", class_=re.compile("fa-calendar|fa-clock")) or c.find("a"):
                    text_div = c
                    break
            if text_div is None:
                text_div = cells[-1]
            info = text_div.find_all("div", recursive=False)
            if len(info) < 2:
                continue
            meta = _text(info[0])
            m = re.match(r"(.+)\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))", meta, re.IGNORECASE)
            if m:
                date = m.group(1).strip()
                gametime = m.group(2)
            else:
                m = re.match(r"(\d{1,2}:\d{2}\s*(?:AM|PM))\s*-\s*(.+)", meta, re.IGNORECASE)
                date = None
                gametime = m.group(1) if m else ""
                # Try to find date from heading
                date = h.get_text(strip=True).replace("Upcoming Games", "").replace("Recent Results", "").strip()

            matchup = info[1]
            links = matchup.find_all("a", href=True)
            home = _team_from_link(links[0]) if len(links) > 0 else {"name": "", "id": None}
            away = _team_from_link(links[1]) if len(links) > 1 else {"name": "", "id": None}

            games.append({
                "date": date,
                "time": gametime,
                "facility": "",
                "home": home["name"],
                "home_id": home["id"],
                "away": away["name"],
                "away_id": away["id"],
            })
    return games


def parse_dashboard(league_id):
    soup, err = get_soup(f"/dashboard.cfm?LeagueID={league_id}")
    if err:
        return None, err

    title = soup.find("h1")
    league_name = _text(title) if title else ""
    season = ""
    breadcrumb = soup.find("ol", class_="breadcrumb")
    if breadcrumb:
        season = _text(breadcrumb.find("li", class_="active") or breadcrumb.find("li"))

    # Standings
    standings = []
    standings_heading = soup.find(lambda t: t.name in ("h1", "h2") and "Standings" in t.get_text())
    if standings_heading:
        table = standings_heading.find_parent("div", class_="row")
        if table:
            table = table.find("table")
    else:
        table = soup.find("table")

    if table:
        rows = table.find("tbody").find_all("tr") if table.find("tbody") else []
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 8:
                continue
            team_link = cells[0].find("a", href=True)
            standings.append({
                "team": _text(team_link) if team_link else _text(cells[0]),
                "team_id": _team_id(team_link["href"]) if team_link else None,
                "gp": _score_to_int(_text(cells[1])),
                "w": _score_to_int(_text(cells[2])),
                "l": _score_to_int(_text(cells[3])),
                "otl": _score_to_int(_text(cells[4])),
                "pts": _score_to_int(_text(cells[5])),
                "gf": _score_to_int(_text(cells[6])),
                "ga": _score_to_int(_text(cells[7])),
            })

    # League leaders (pts, goals, asst, pim)
    leaders = {"points": [], "goals": [], "assists": [], "pim": []}
    table_map = {
        "pts": "points",
        "goals": "goals",
        "asst": "assists",
        "pim": "pim",
    }
    for table_id, key in table_map.items():
        table = soup.find("table", {"id": table_id})
        if not table:
            continue
        rows = table.find("tbody").find_all("tr") if table.find("tbody") else []
        for i, row in enumerate(rows, 1):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            name_link = cells[0].find("a", href=True)
            team_link = cells[1].find("a", href=True)
            player_id = _player_id(name_link["href"]) if name_link else None
            team_id = _team_id(team_link["href"]) if team_link else None
            leaders[key].append({
                "rank": i,
                "name": _text(name_link) if name_link else _text(cells[0]),
                "team": _text(team_link) if team_link else _text(cells[1]),
                "team_id": team_id,
                "player_id": player_id,
                "value": _score_to_int(_text(cells[2])),
            })

    # Upcoming games and recent results
    upcoming = []
    recent = []

    upcoming_heading = soup.find(lambda t: t.name in ("h1", "h2") and "Upcoming Games" in t.get_text())
    if upcoming_heading:
        section = upcoming_heading.find_parent("section")
        if section:
            for row in section.find_all("div", class_="row", recursive=False):
                # Each row: icon col, text col
                text_div = row.find("div", class_=re.compile(r"col-(?:lg|md|sm|xs)-(?:9|10|12)"))
                if not text_div:
                    # Fallback: choose the div that contains the game links
                    for c in row.find_all("div", recursive=False):
                        if c.find("a", href=re.compile(r"TeamID=")):
                            text_div = c
                            break
                if not text_div:
                    continue

                # Date is a text node, time/facility and matchup are child divs
                date_match = text_div.find(string=re.compile(r"[A-Za-z]+, [A-Za-z]+ \d+"))
                date = _text(date_match) if date_match else ""

                info_divs = text_div.find_all("div", recursive=False)
                # Filter out any nested row used just for the section heading
                info_divs = [d for d in info_divs if not d.find("h2")]

                gametime = ""
                facility = ""
                matchup = None
                for d in info_divs:
                    txt = _text(d)
                    if re.search(r"vs\.", txt):
                        matchup = d
                    elif re.match(r"\d{1,2}:\d{2}\s*(?:AM|PM)", txt, re.IGNORECASE):
                        m = re.match(r"(\d{1,2}:\d{2}\s*(?:AM|PM))\s*-\s*(.+)", txt, re.IGNORECASE)
                        gametime = m.group(1) if m else txt
                        facility = m.group(2).strip() if m else ""

                if not matchup:
                    continue
                links = matchup.find_all("a", href=True)
                home = _team_from_link(links[0]) if len(links) > 0 else {"name": "", "id": None}
                away = _team_from_link(links[1]) if len(links) > 1 else {"name": "", "id": None}
                upcoming.append({
                    "date": date,
                    "time": gametime,
                    "facility": facility,
                    "home": home["name"],
                    "home_id": home["id"],
                    "away": away["name"],
                    "away_id": away["id"],
                })

    recent_heading = soup.find(lambda t: t.name in ("h1", "h2") and "Recent Results" in t.get_text())
    if recent_heading:
        section = recent_heading.find_parent("section")
        if section:
            # Each game is a table with header having date/time and body with two rows
            for table in section.find_all("table", class_="table"):
                header = table.find("thead")
                if not header:
                    continue
                header_cells = header.find_all("th", recursive=False)
                header_text = _text(header_cells[0]) if len(header_cells) > 0 else ""
                m = re.match(r"([A-Za-z]+ \d+)\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))", header_text)
                date = m.group(1) if m else ""
                gametime = m.group(2) if m else ""

                rows = table.find("tbody").find_all("tr") if table.find("tbody") else []
                if len(rows) < 2:
                    continue
                home_link = rows[0].find("a", href=True)
                away_link = rows[1].find("a", href=True)
                home_cells = rows[0].find_all("td")
                away_cells = rows[1].find_all("td")

                def get_periods(cells):
                    vals = [_score_to_int(_text(c)) for c in cells[1:]]
                    # Last two may be F and F-SO; keep if short list
                    return vals

                home_vals = get_periods(home_cells)
                away_vals = get_periods(away_cells)

                # Final score: find last numeric value that is not zero? Use last cell text.
                home_final = _score_to_int(_text(home_cells[-1])) if home_cells else 0
                away_final = _score_to_int(_text(away_cells[-1])) if away_cells else 0

                recent.append({
                    "date": date,
                    "time": gametime,
                    "home": _text(home_link) if home_link else _text(home_cells[0]),
                    "home_id": _team_id(home_link["href"]) if home_link else None,
                    "away": _text(away_link) if away_link else _text(away_cells[0]),
                    "away_id": _team_id(away_link["href"]) if away_link else None,
                    "home_periods": home_vals,
                    "away_periods": away_vals,
                    "home_final": home_final,
                    "away_final": away_final,
                })

    # Playoffs
    playoffs = []
    playoff_tables = []
    for thead in soup.find_all("thead"):
        round_th = thead.find("th", colspan=re.compile("^\d+$"))
        if round_th and round_th.get_text(strip=True) in ("ROUND 1", "ROUND 2", "CHAMPIONSHIP", "SEMI-FINAL", "FINAL"):
            playoff_tables.append(round_th.get_text(strip=True))
    # TODO: parse playoff games if needed

    return {
        "league_name": league_name,
        "season": season,
        "standings": standings,
        "leaders": leaders,
        "upcoming": upcoming,
        "recent": recent,
        "playoffs": playoffs,
    }, None


def parse_team_overview(team_id):
    soup, err = get_soup(f"/team/?TeamID={team_id}")
    if err:
        return None, err

    h1 = soup.find("h1")
    team_name = _text(h1) if h1 else ""
    team_name_core = team_name.replace(" Hockey", "").strip()

    def _team_or_self(cell, team_id):
        link = cell.find("a", href=True)
        if link:
            return _text(link), _team_id(link["href"])
        # The current team is shown in bold without a link.
        return _text(cell), team_id

    next_game = None
    next_heading = soup.find(lambda t: t.name in ("h2", "h3") and "Next Game" in t.get_text())
    if next_heading:
        container = next_heading.find_parent("div", class_="sidebar-post-item")
        if container:
            big = container.find("div", class_=re.compile(r"col-lg-10|col-md-9|col-sm-10|col-xs-12"))

            date = ""
            gametime = ""
            facility = ""
            opponent = ""
            opp_id = None

            if big:
                # Date is a text node; time/facility and matchup are child divs
                date_match = big.find(string=re.compile(r"[A-Za-z]+, [A-Za-z]+ \d+"))
                date = _text(date_match) if date_match else ""

                for d in big.find_all("div", recursive=False):
                    if d.find("h2") or d.find("h3"):
                        continue
                    txt = _text(d)
                    if re.search(r"vs\.", txt):
                        opp_link = d.find("a", href=True)
                        if opp_link:
                            opponent = _text(opp_link)
                            opp_id = _team_id(opp_link["href"])
                    else:
                        m = re.match(r"(\d{1,2}:\d{2}\s*(?:AM|PM))\s*-\s*(.+)", txt, re.IGNORECASE)
                        if m:
                            gametime = m.group(1)
                            facility = m.group(2).strip()

            home_away = "Away" if "we are away" in container.get_text(" ", strip=True).lower() else "Home"

            next_game = {
                "date": date,
                "time": gametime,
                "facility": facility,
                "opponent": opponent,
                "opponent_id": opp_id,
                "home_away": home_away,
            }

    recent = None
    recent_heading = soup.find(lambda t: t.name in ("h2", "h3") and "Recent Results" in t.get_text())
    if recent_heading:
        container = recent_heading.find_parent("div", class_="sidebar-post-item")
        if container:
            table = container.find("table")
        if table:
            rows = table.find("tbody").find_all("tr") if table.find("tbody") else []
            if len(rows) >= 2:
                hcells = rows[0].find_all("td")
                acells = rows[1].find_all("td")
                home, home_id = _team_or_self(hcells[0], team_id)
                away, away_id = _team_or_self(acells[0], team_id)
                home_vals = [_score_to_int(_text(c)) for c in hcells[1:]]
                away_vals = [_score_to_int(_text(c)) for c in acells[1:]]
                recent = {
                    "home": home,
                    "home_id": home_id,
                    "away": away,
                    "away_id": away_id,
                    "home_periods": home_vals,
                    "away_periods": away_vals,
                    "home_final": home_vals[-1] if home_vals else 0,
                    "away_final": away_vals[-1] if away_vals else 0,
                }

    # Team leaders points/goals/assists/pim
    team_leaders = {"points": [], "goals": [], "assists": [], "pim": []}
    leader_value_map = {
        "pts": ("points", "points"),
        "goals": ("goals", "goals"),
        "asst": ("assists", "assists"),
        "pim": ("pim", "pim"),
    }
    for table_id, (key, val_key) in leader_value_map.items():
        table = soup.find("table", {"id": table_id})
        if not table:
            continue
        rows = table.find("tbody").find_all("tr") if table.find("tbody") else []
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            team_leaders[key].append({
                "name": _text(cells[0]),
                val_key: _score_to_int(_text(cells[1])),
            })

    return {
        "team_name": team_name,
        "team_name_core": team_name_core,
        "next_game": next_game,
        "recent_result": recent,
        "team_leaders": team_leaders,
    }, None


def parse_team_schedule(team_id):
    soup, err = get_soup(f"/team/schedule.cfm?TeamID={team_id}")
    if err:
        return None, err

    h1 = soup.find("h1")
    team_name = _text(h1) if h1 else ""
    team_name_core = team_name.replace(" Hockey", "").strip()

    games = []
    table = soup.find("table", class_=re.compile("table"))
    if table:
        rows = table.find("tbody").find_all("tr") if table.find("tbody") else []
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 7:
                continue
            date = _text(cells[0])
            gametime = _text(cells[1])
            facility = _text(cells[2])
            rink = _text(cells[3])

            def _is_current_team(name):
                return name == team_name_core or name == team_name or team_name_core in name or name in team_name_core

            home_link = cells[4].find("a", href=True)
            away_link = cells[5].find("a", href=True)
            home = _text(home_link) if home_link else _text(cells[4])
            away = _text(away_link) if away_link else _text(cells[5])
            home_id = _team_id(home_link["href"]) if home_link else (team_id if _is_current_team(home) else None)
            away_id = _team_id(away_link["href"]) if away_link else (team_id if _is_current_team(away) else None)

            score_text = _text(cells[6])
            m = re.match(r"(\d+)\s*-\s*(\d+)", score_text)
            home_score = _score_to_int(m.group(1)) if m else 0
            away_score = _score_to_int(m.group(2)) if m else 0

            score_sheet = None
            if len(cells) > 7:
                ssa = cells[7].find("a", href=True)
                if ssa:
                    href = ssa["href"]
                    if href.startswith("../"):
                        href = href[3:]
                    if not href.startswith("http"):
                        href = BASE_URL + "/" + href.lstrip("/")
                    score_sheet = href

            games.append({
                "date": date,
                "time": gametime,
                "facility": facility,
                "rink": rink,
                "home": home,
                "home_id": home_id,
                "away": away,
                "away_id": away_id,
                "home_score": home_score,
                "away_score": away_score,
                "score_sheet": score_sheet,
                "played": bool(m),
            })

    return games, None


def parse_team_stats(team_id):
    soup, err = get_soup(f"/team/stats.cfm?TeamID={team_id}")
    if err:
        return None, err

    players = []
    table = soup.find("table", attrs={"data-provide": "datatable"})
    if not table:
        table = soup.find("table", class_=re.compile("table"))
    if not table:
        return players, None

    header = [c.get_text(strip=True).lower() for c in table.find("thead").find_all("th")] if table.find("thead") else []
    rows = table.find("tbody").find_all("tr") if table.find("tbody") else []

    stats_cols = ["jersey", "name", "position", "gp", "g", "a", "pts", "pim", "esg", "ppg", "shg", "psg", "sog"]
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 7:
            continue
        player_link = cells[1].find("a", href=True)
        token = None
        if player_link:
            href = player_link.get("href", "")
            if re.match(r"^[0-9A-Fa-f]+$", href.split("?")[-1]):
                token = href.split("?")[-1]

        player = {
            "jersey": _score_to_int(_text(cells[0])),
            "name": _text(player_link) if player_link else _text(cells[1]),
            "position": _text(cells[2]),
            "token": token,
        }
        # numeric columns after name/position
        for i, col in enumerate(stats_cols[3:], start=3):
            player[col] = _score_to_int(_text(cells[i])) if i < len(cells) else 0
        players.append(player)

    return players, None


def parse_team_standings(team_id):
    soup, err = get_soup(f"/team/standings.cfm?TeamID={team_id}")
    if err:
        return None, err

    standings = []
    table = soup.find("table", class_=re.compile("table"))
    if table:
        rows = table.find("tbody").find_all("tr") if table.find("tbody") else []
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 8:
                continue
            team_link = cells[0].find("a", href=True)
            standings.append({
                "team": _text(team_link) if team_link else _text(cells[0]),
                "team_id": _team_id(team_link["href"]) if team_link else None,
                "gp": _score_to_int(_text(cells[1])),
                "w": _score_to_int(_text(cells[2])),
                "l": _score_to_int(_text(cells[3])),
                "otl": _score_to_int(_text(cells[4])),
                "pts": _score_to_int(_text(cells[5])),
                "gf": _score_to_int(_text(cells[6])),
                "ga": _score_to_int(_text(cells[7])),
            })

    return standings, None


def _parse_player_history_soup(soup):
    h1 = soup.find("h1")
    name = _text(h1) if h1 else ""

    history = []
    table = soup.find("table", {"id": "playerTable"})
    if table:
        rows = table.find("tbody").find_all("tr") if table.find("tbody") else []
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 11:
                continue
            history.append({
                "season": _text(cells[0]),
                "league": _text(cells[1]),
                "team": _text(cells[2]),
                "gp": _score_to_int(_text(cells[3])),
                "g": _score_to_int(_text(cells[4])),
                "a": _score_to_int(_text(cells[5])),
                "pts": _score_to_int(_text(cells[6])),
                "pim": _score_to_int(_text(cells[7])),
                "esg": _score_to_int(_text(cells[8])),
                "ppg": _score_to_int(_text(cells[9])),
                "shg": _score_to_int(_text(cells[10])) if len(cells) > 10 else 0,
                "psg": _score_to_int(_text(cells[11])) if len(cells) > 11 else 0,
                "sog": _score_to_int(_text(cells[12])) if len(cells) > 12 else 0,
            })

    return {"name": name, "history": history}


def parse_player_history(team_id, player_id):
    soup, err = get_soup(f"/team/player_history.cfm?TeamID={team_id}&PlayerID={player_id}")
    if err:
        return None, err
    return _parse_player_history_soup(soup), None


def parse_player_history_by_token(token):
    soup, err = get_soup(f"/team/player_history.cfm?{token}")
    if err:
        return None, err
    return _parse_player_history_soup(soup), None
