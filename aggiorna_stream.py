import json
from datetime import datetime
from zoneinfo import ZoneInfo
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

def converti_ora_in_italiana(ora_str_utc):
    """
    Se calendar.json ha l'orario in formato "HH:MM" UTC (es. "18:45"),
    lo converte nell'orario italiano corrente.
    """
    if not ora_str_utc:
        return ""
    try:
        fuso_roma = ZoneInfo("Europe/Rome")
        # Crea una data/ora fittizia in UTC con l'ora ricevuta
        ora_utc = datetime.strptime(ora_str_utc, "%H:%M").replace(tzinfo=ZoneInfo("UTC"))
        # Converte nel fuso orario italiano
        ora_roma = ora_utc.astimezone(fuso_roma)
        return ora_roma.strftime("%H:%M")
    except ValueError:
        return ora_str_utc

def main():
    # Forza il fuso orario di Roma per evitare che GitHub Actions (UTC) sbagli giorno
    fuso_roma = ZoneInfo("Europe/Rome")
    oggi = datetime.now(fuso_roma).strftime("%Y-%m-%d")
    
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

        # Converte l'ora se presente in calendar.json
        ora_originale = partita_di_oggi.get("ora", "")
        ora_italiana = converti_ora_in_italiana(ora_originale)

        stream_data = {
            "attivo": True,
            "in_chiaro": in_chiaro,
            "data": oggi,
            "ora": ora_italiana,
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
            "ora": None,
            "partita": None,
            "home_team": None,
            "away_team": None,
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
