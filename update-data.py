import json
from datetime import datetime

data = {
    "matches": [],
    "standings": [],
    "fr12": []
}

with open("data.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)

print("data.json is bijgewerkt:", datetime.now())
