import json
import os
import urllib.request
import re
from datetime import datetime, timezone
from html.parser import HTMLParser

TOKEN = os.environ["FOOTBALL_DATA_TOKEN"]
API = "https://api.football-data.org/v4"

headers = {
    "X-Auth-Token": TOKEN,
    "User-Agent": "Mozilla/5.0"
}


def get_json(url):
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


# =========================
# FEYENOORD WEDSTRIJDEN
# =========================

FEYENOORD_ID = 675

matches_data = get_json(
    f"{API}/teams/{FEYENOORD_ID}/matches?competitions=DED&limit=20"
)

matches = []

for match in matches_data.get("matches", []):
    full_time = match.get("score", {}).get("fullTime", {})

    home_score = full_time.get("home")
    away_score = full_time.get("away")

    score = None

    if home_score is not None and away_score is not None:
        score = f"{home_score} - {away_score}"

    matches.append({
        "date": match.get("utcDate"),
        "home": match.get("homeTeam", {}).get("name"),
        "away": match.get("awayTeam", {}).get("name"),
        "score": score,
        "status": match.get("status")
    })


# =========================
# EREDIVISIE STAND
# =========================

standings_data = get_json(
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
# FR12 NIEUWS
# =========================

class FR12Parser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.articles = []
        self.current_link = None
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "a" and attrs.get("href"):
            href = attrs["href"]

            if "fr12.nl" in href and "/nieuws/" in href:
                self.current_link = href
                self.current_text = []

    def handle_data(self, data):
        if self.current_link:
            self.current_text.append(data.strip())

    def handle_endtag(self, tag):
        if tag == "a" and self.current_link:

            title = " ".join(
                x for x in self.current_text if x
            ).strip()

            if title and len(title) > 10:

                if not any(
                    article["title"] == title
                    for article in self.articles
                ):
                    self.articles.append({
                        "title": title,
                        "summary": "",
                        "date": "",
                        "url": self.current_link
                    })

            self.current_link = None
            self.current_text = []


try:

    request = urllib.request.Request(
        "https://www.fr12.nl/",
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(request) as response:
        html = response.read().decode("utf-8", errors="ignore")

    parser = FR12Parser()
    parser.feed(html)

    fr12 = parser.articles[:10]

except Exception as error:

    print("FR12 kon niet worden opgehaald:", error)
    fr12 = []


# =========================
# DATA.JSON OPSLAAN
# =========================

data = {
    "matches": matches,
    "standings": standings,
    "fr12": fr12,
    "updated": datetime.now(timezone.utc).isoformat()
}

with open("data.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)


print("Feyenoord wedstrijden:", len(matches))
print("Eredivisie teams:", len(standings))
print("FR12 artikelen:", len(fr12))
print("Data succesvol bijgewerkt!")
