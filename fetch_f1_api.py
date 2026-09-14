import json
from datetime import datetime
import requests

# API gratuita per i dati della F1 (senza API key)
F1_API_URL = "https://api.jolpi.ca/ergast/f1/current.json"


def fetch_f1_calendar():
    try:
        response = requests.get(F1_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        races = (
            data.get("MRData", {})
            .get("RaceTable", {})
            .get("Races", [])
        )
        f1_events = []

        for race in races:
            # Recupera la data e l'ora UTC della gara domenicale
            date_str = race.get("date")  # YYYY-MM-DD
            time_str = race.get("time", "14:00:00Z").replace(
                "Z", ""
            )  # HH:MM:SS
            time_short = ":".join(time_str.split(":")[:2])  # HH:MM

            f1_events.append(
                {
                    "tipo": "f1",
                    "partita": f"GP {race.get('raceName')}",
                    "competizione": "Formula 1",
                    "servizio": "NOW / Sky",
                    "data": date_str,
                    "ora": time_short,  # Orario in UTC
                    "url_default": "https://dlhd.pk/watch.php?id=555",  # Canale F1 di default
                }
            )

        return f1_events

    except Exception as e:
        print(f"Errore durante il recupero del calendario F1: {e}")
        return []


if __name__ == "__main__":
    f1_data = fetch_f1_calendar()
    with open("f1_calendar.json", "w", encoding="utf-8") as f:
        json.dump(f1_data, f, ensure_ascii=False, indent=2)
    print(f"Salvato calendario F1 con {len(f1_data)} eventi.")
