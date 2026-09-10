import json
from datetime import datetime
import requests

DOMINI_STREAM = [
    "https://dlhd.pk",
    "https://dlhd.st",
    "https://dstreams.st"
]

CANALI_SERVIZI = {
    "DAZN": "/watch.php?id=877",
    "Prime Video": "/watch.php?id=461",
    "Sky / NOW": "/watch.php?id=461"
}

def trova_dominio_base_attivo():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    for dominio in DOMINI_STREAM:
        try:
            response = requests.head(dominio, timeout=3, allow_redirects=True, headers=headers)
            if response.status_code < 400:
                return dominio
        except requests.RequestException:
            continue
    return DOMINI_STREAM[0]

def main():
    oggi = datetime.now().strftime("%Y-%m-%d")
    
    try:
        with open("calendar.json", "r", encoding="utf-8") as f:
            calendario = json.load(f)
    except FileNotFoundError:
        print("File calendar.json non trovato.")
        return

    partita_di_oggi = None
    for evento in calendario:
        if evento.get("data") == oggi:
            partita_di_oggi = evento
            break

    if partita_di_oggi:
        servizio = partita_di_oggi.get("servizio", "")
        in_chiaro = "mediaset" in servizio.lower()
        
        if in_chiaro:
            url_finale = ""
        else:
            percorso_canale = CANALI_SERVIZI.get(servizio, "")
            dominio_base = trova_dominio_base_attivo()
            url_finale = f"{dominio_base}{percorso_canale}" if percorso_canale else ""

        stream_data = {
            "attivo": True,
            "in_chiaro": in_chiaro,
            "data": oggi,
            "partita": partita_di_oggi.get("partita"),
            "home_team": partita_di_oggi.get("home_team"),
            "away_team": partita_di_oggi.get("away_team"),
            "home_logo": partita_di_oggi.get("home_logo"),
            "away_logo": partita_di_oggi.get("away_logo"),
            "competizione": partita_di_oggi.get("competizione"),
            "servizio": servizio,
            "url": url_finale
        }
    else:
        stream_data = {
            "attivo": False,
            "in_chiaro": False,
            "data": oggi,
            "partita": None,
            "home_logo": None,
            "away_logo": None,
            "competizione": None,
            "servizio": None,
            "url": ""
        }

    with open("stream.json", "w", encoding="utf-8") as f:
        json.dump(stream_data, f, indent=2, ensure_ascii=False)
    
    print("stream.json aggiornato con successo.")

if __name__ == "__main__":
    main()
