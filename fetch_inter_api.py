import os
import json
import requests
from datetime import datetime

# Recupera la chiave API dalle variabili d'ambiente (GitHub Secrets)
API_KEY = os.getenv("ec7605e71b194c84b5eeb499845bfc96")
INTER_TEAM_ID = 108

def fetch_inter_matches():
    url = f"https://api.football-data.org/v4/teams/{INTER_TEAM_ID}/matches"
    headers = {"X-Auth-Token": API_KEY}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Errore nella chiamata API: {response.status_code}")
        return

    data = response.json()
    partite = []

    for match in data.get("matches", []):
        utc_date = match.get("utcDate")
        data_str = datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
        
        home_team = match["homeTeam"]["name"]
        away_team = match["awayTeam"]["name"]
        competition = match["competition"]["name"]

        partite.append({
            "data": data_str,
            "partita": f"{home_team} vs {away_team}",
            "competizione": competition,
            "servizio": "DAZN" if competition == "Serie A" else "Prime Video / Sky", # Assegnazione dinamica basata sui diritti TV
            "url": ""
        })

    with open("calendario.json", "w", encoding="utf-8") as f:
        json.dump(partite, f, indent=2, ensure_ascii=False)

    print("Calendario scaricato con successo dall'API.")

if __name__ == "__main__":
    fetch_inter_matches()
