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

def main():
    # Fusi orari di riferimento
    fuso_roma = ZoneInfo("Europe/Rome")
    fuso_utc = ZoneInfo("UTC")
    
    # Data attuale nel fuso orario italiano
    ora_attuale_roma = datetime.now(fuso_roma)
    oggi_roma = ora_attuale_roma.strftime("%Y-%m-%d")
    
    try:
        with open("calendar.json", "r", encoding="utf-8") as f:
            calendario = json.load(f)
    except FileNotFoundError:
        print("File calendar.json non trovato.")
        return

    partite = calendario if isinstance(calendario, list) else calendario.get("partite", [])

    partita_di_oggi = None
    dt_roma_partita = None

    for evento in partite:
        data_str = evento.get("data")
        ora_str = evento.get("ora") or evento.get("orario") or "18:45"
        
        if not data_str:
            continue

        try:
            # 1. Combina data e ora UTC di calendar.json in un datetime UTC consapevole
            dt_utc = datetime.strptime(f"{data_str} {ora_str}", "%Y-%m-%d %H:%M").replace(tzinfo=fuso_utc)
            
            # 2. Converte in orario/data italiano applicando l'ora legale o solare corretta per quel giorno
            dt_roma = dt_utc.astimezone(fuso_roma)
            
            # 3. Verifica se la partita ricade nella giornata odierna italiana
            if dt_roma.strftime("%Y-%m-%d") == oggi_roma:
                partita_di_oggi = evento
                dt_roma_partita = dt_roma
                break
        except ValueError:
            # Fallback se la stringa data non è nel formato YYYY-MM-DD
            if data_str == oggi_roma:
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

        # Estrae data e ora convertite per l'Italia
        if dt_roma_partita:
            ora_italiana = dt_roma_partita.strftime("%H:%M")
            data_italiana = dt_roma_partita.strftime("%Y-%m-%d")
        else:
            ora_italiana = partita_di_oggi.get("ora", "")
            data_italiana = oggi_roma

        stream_data = {
            "attivo": True,
            "in_chiaro": in_chiaro,
            "data": data_italiana,
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
            "data": oggi_roma,
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
    main()import json
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
