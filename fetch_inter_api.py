from datetime import datetime
import json
import os
import requests

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "sportapi7.p.rapidapi.com"
INTER_TEAM_ID = 2697  # ID dell'Inter su SportAPI / Sofascore


def determina_servizio(competizione, data_dt):
  comp_lower = competizione.lower()
  if "serie a" in comp_lower:
    return "DAZN"
  elif "coppa italia" in comp_lower:
    return "Mediaset"
  elif "champions league" in comp_lower:
    if data_dt.weekday() == 2:  # Mercoledì
      return "Prime Video"
    return "Sky / NOW"
  elif "supercoppa" in comp_lower:
    return "Mediaset"
  return "Generico"


def fetch_inter_matches():
  if not RAPIDAPI_KEY:
    print("❌ Errore: la variabile RAPIDAPI_KEY non è impostata nei Secrets!")
    return

  # Endpoint per le prossime partite dell'Inter
  url = (
      f"https://sportapi7.p.rapidapi.com/api/v1/team/{INTER_TEAM_ID}/events/next/0"
  )
  headers = {
      "X-RapidAPI-Key": RAPIDAPI_KEY,
      "X-RapidAPI-Host": RAPIDAPI_HOST,
  }

  try:
    response = requests.get(url, headers=headers, timeout=10)
  except requests.RequestException as e:
    print(f"❌ Errore di connessione: {e}")
    return

  if response.status_code != 200:
    print(f"❌ Errore HTTP {response.status_code}: {response.text}")
    return

  data = response.json()
  events = data.get("events", [])
  print(f"ℹ️ Partite trovate: {len(events)}")

  partite = []
  for event in events:
    tournament = event.get("tournament", {})
    home = event.get("homeTeam", {})
    away = event.get("awayTeam", {})

    # Data e ora a partire dallo timestamp Unix
    timestamp = event.get("startTimestamp")
    if not timestamp:
      continue

    data_dt = datetime.fromtimestamp(timestamp)
    data_str = data_dt.strftime("%Y-%m-%d")
    ora_str = data_dt.strftime("%H:%M")

    competition = tournament.get("name", "Competizione sconosciuta")
    servizio_tv = determina_servizio(competition, data_dt)

    # Costruzione URL dei loghi squadra
    home_id = home.get("id")
    away_id = away.get("id")
    home_logo = (
        f"https://api.sofascore.app/api/v1/team/{home_id}/image"
        if home_id
        else ""
    )
    away_logo = (
        f"https://api.sofascore.app/api/v1/team/{away_id}/image"
        if away_id
        else ""
    )

    partite.append({
        "data": data_str,
        "ora": ora_str,
        "partita": f"{home.get('name', '')} vs {away.get('name', '')}",
        "home_team": home.get("name", ""),
        "away_team": away.get("name", ""),
        "home_logo": home_logo,
        "away_logo": away_logo,
        "competizione": competition,
        "servizio": servizio_tv,
        "url": "",
    })

  partite.sort(key=lambda x: (x["data"], x["ora"]))

  with open("calendar.json", "w", encoding="utf-8") as f:
    json.dump(partite, f, indent=2, ensure_ascii=False)

  print(f"✅ Completato con successo! Generate {len(partite)} partite.")


if __name__ == "__main__":
  fetch_inter_matches()
