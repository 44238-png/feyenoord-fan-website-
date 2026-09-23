import json
import os
import urllib.request
from datetime import datetime, timezone

TOKEN = os.environ["FOOTBALL_DATA_TOKEN"]
API = "https://api.football-data.org/v4"

headers = {
    "X-Auth-Token": TOKEN
}


def get_data(url):
    request = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


# =========================
# WEDSTRIJDEN
# =========================

matches_data = get_data(
    f"{API}/competitions/DED/matches"
)

matches = []

for match in matches_data.get("matches", []):
    score = match.get("score", {})
    full_time = score.get("fullTime", {})

    home_score = full_time.get("home")
    away_score = full_time.get("away")

    if home_score is not None and away_score is not None:
        result = f"{home_score} - {away_score}"
    else:
        result = None

    matches.append({
        "date": match.get("utcDate"),
        "home": match.get("homeTeam", {}).get("name"),
        "away": match.get("awayTeam", {}).get("name"),
        "score": result,
        "status": match.get("status")
    })


# =========================
# EREDIVISIE STAND
# =========================

standings_data = get_data(
    f"{API}/competitions/DED/standings"
)

standings = []

for table in standings_data.get("standings", []):
    if table.get("type") == "TOTAL":
        for team in table.get("table", []):
            standings.append({
                "position": team.get("position"),
                "team": team.get("team", {}).get("name"),
                "played": team.get("playedGames"),
                "wins": team.get("won"),
                "draws": team.get("draw"),
                "points": team.get("points")
            })
        break


# =========================
# DATA.JSON OPSLAAN
# =========================

data = {
    "matches": matches,
    "standings": standings,
    "fr12": [],
    "updated": datetime.now(timezone.utc).isoformat()
}

with open("data.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)

print("Feyenoord-data succesvol bijgewerkt!")
print("Wedstrijden:", len(matches))
print("Stand:", len(standings), "teams")
