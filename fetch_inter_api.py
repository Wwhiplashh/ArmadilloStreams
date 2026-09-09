import os
import json
import requests
from datetime import datetime

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
INTER_TEAM_ID = 108

def determina_servizio(competizione, data_dt):
    """
    Assegna automaticamente il servizio di trasmissione in base alla competizione.
    """
    if competizione == "Serie A":
        return "DAZN"
    elif competizione == "Coppa Italia":
        return "Mediaset"
    elif competizione == "UEFA Champions League":
        # Il mercoledì (weekday() == 2) la miglior partita italiana è solitamente su Prime Video
        if data_dt.weekday() == 2:
            return "Prime Video"
        return "Sky / NOW"
    elif competizione == "Supercoppa":
        return "Mediaset"
    
    return "Generico"

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
        data_dt = datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%SZ")
        data_str = data_dt.strftime("%Y-%m-%d")
        
        home_team = match["homeTeam"]["name"]
        away_team = match["awayTeam"]["name"]
        competition = match["competition"]["name"]

        # 1. Richiama la funzione per determinare il canale/servizio TV
        servizio_tv = determina_servizio(competition, data_dt)

        # 2. Aggiunge i dati completa alla lista
        partite.append({
            "data": data_str,
            "partita": f"{home_team} vs {away_team}",
            "competizione": competition,
            "servizio": servizio_tv,
            "url": ""  # Rimane vuoto o da popolare se usi sempre URL fissi
        })

    # Salva il risultato in calendario.json
    with open("calendario.json", "w", encoding="utf-8") as f:
        json.dump(partite, f, indent=2, ensure_ascii=False)

    print("Calendario generato con successo in calendario.json")

if __name__ == "__main__":
    fetch_inter_matches()
