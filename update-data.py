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
# ALLEEN FEYENOORD WEDSTRIJDEN
# =========================

# Feyenoord team-ID bij football-data.org
FEYENOORD_ID = 675

matches_data = get_data(
    f"{API}/teams/{FEYENOORD_ID}/matches?competitions=DED&limit=20"
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
        "status": match.get("status"),
        "competition": match.get("competition", {}).get("name")
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
# DATA.JSON
# =========================

data = {
    "matches": matches,
    "standings": standings,
    "fr12": [],
    "updated": datetime.now(timezone.utc).isoformat()
}


with open("data.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)


print("Feyenoord wedstrijden:", len(matches))
print("Eredivisie teams:", len(standings))
print("Data succesvol bijgewerkt!")
