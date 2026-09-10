import os
import json
from datetime import datetime
import requests

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "api-football-v1.p.rapidapi.com"
INTER_TEAM_ID = 505
CURRENT_SEASON = 2026

def determina_servizio(competizione, data_dt):
    comp_lower = competizione.lower()
    if "serie a" in comp_lower:
        return "DAZN"
    elif "coppa italia" in comp_lower:
        return "Mediaset"
    elif "champions league" in comp_lower:
        if data_dt.weekday() == 2:
            return "Prime Video"
        return "Sky / NOW"
    elif "supercoppa" in comp_lower:
        return "Mediaset"
    return "Generico"

def fetch_inter_matches():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    params = {
        "team": INTER_TEAM_ID,
        "season": CURRENT_SEASON
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Errore nella chiamata API-Football: {response.status_code} - {response.text}")
        return

    data = response.json()
    partite = []

    for item in data.get("response", []):
        fix = item["fixture"]
        league = item["league"]
        home = item["teams"]["home"]
        away = item["teams"]["away"]
        
        utc_date_str = fix["date"]
        try:
            data_dt = datetime.fromisoformat(utc_date_str.replace('Z', '+00:00'))
        except ValueError:
            data_dt = datetime.strptime(utc_date_str[:19], "%Y-%m-%dT%H:%M:%S")

        data_str = data_dt.strftime("%Y-%m-%d")
        ora_str = data_dt.strftime("%H:%M")
        
        competition = league["name"]
        servizio_tv = determina_servizio(competition, data_dt)

        partite.append({
            "data": data_str,
            "ora": ora_str,
            "partita": f"{home['name']} vs {away['name']}",
            "home_team": home["name"],
            "away_team": away["name"],
            "home_logo": home["logo"],
            "away_logo": away["logo"],
            "competizione": competition,
            "servizio": servizio_tv,
            "url": ""
        })

    partite.sort(key=lambda x: (x["data"], x["ora"]))

    with open("calendar.json", "w", encoding="utf-8") as f:
        json.dump(partite, f, indent=2, ensure_ascii=False)

    print("Calendario generato con successo con loghi inclusi.")

if __name__ == "__main__":
    fetch_inter_matches()
