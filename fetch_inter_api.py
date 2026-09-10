import json
import os
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
  # 1. Verifica se la variabile d'ambiente è presente
  if not RAPIDAPI_KEY:
    print(
        "❌ Errore: la variabile RAPIDAPI_KEY non è impostata o è vuota nei"
        " Secrets!"
    )
    return

  url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
  headers = {
      "X-RapidAPI-Key": RAPIDAPI_KEY,
      "X-RapidAPI-Host": RAPIDAPI_HOST,
  }
  params = {"team": INTER_TEAM_ID, "season": CURRENT_SEASON}

  # 2. Gestione errori di rete durante la richiesta
  try:
    response = requests.get(url, headers=headers, params=params, timeout=10)
  except requests.RequestException as e:
    print(f"❌ Errore di connessione/rete durante la chiamata API: {e}")
    return

  # 3. Controllo codice di stato HTTP
  if response.status_code != 200:
    print(f"❌ Errore HTTP {response.status_code}: {response.text}")
    return

  data = response.json()

  # 4. Controllo errori/avvisi dentro il JSON di RapidAPI
  errors = data.get("errors")
  if errors:
    print(f"⚠️ Dettaglio errore/avviso dall'API: {errors}")

  results_count = data.get("results", 0)
  print(f"ℹ️ Partite trovate nell'API: {results_count}")

  partite = []
  for item in data.get("response", []):
    fix = item["fixture"]
    league = item["league"]
    home = item["teams"]["home"]
    away = item["teams"]["away"]

    utc_date_str = fix["date"]
    try:
      data_dt = datetime.fromisoformat(utc_date_str.replace("Z", "+00:00"))
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
        "url": "",
    })

  partite.sort(key=lambda x: (x["data"], x["ora"]))

  with open("calendar.json", "w", encoding="utf-8") as f:
    json.dump(partite, f, indent=2, ensure_ascii=False)

  print(
      "✅ Operazione completata! Partite salvate in calendar.json:"
      f" {len(partite)}"
  )


if __name__ == "__main__":
  fetch_inter_matches()
