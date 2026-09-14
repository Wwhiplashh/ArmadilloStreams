from datetime import datetime
import json
import os
from zoneinfo import ZoneInfo
import requests

# Lista dei domini mirror di riferimento
DOMINI_STREAM = [
    "https://dlhd.pk",
    "https://dlhd.st",
    "https://dstreams.st",
]


def trova_dominio_base_attivo():
    """Effettua un controllo HEAD sui domini mirror e restituisce il primo raggiungibile."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    for dominio in DOMINI_STREAM:
        try:
            response = requests.head(
                dominio, timeout=3, allow_redirects=True, headers=headers
            )
            if response.status_code < 400:
                return dominio
        except requests.RequestException:
            continue
    return DOMINI_STREAM[0]


def pulisci_orario(ora_str):
    """Pulisce e standardizza la stringa orario nel formato HH:MM (es. '14:00:00Z' -> '14:00')."""
    if not ora_str:
        return "14:00"
    ora_str = str(ora_str).replace("Z", "").strip()
    parti = ora_str.split(":")
    if len(parti) >= 2:
        return f"{parti[0].zfill(2)}:{parti[1].zfill(2)}"
    return "14:00"


def ottieni_url_stream_inter(servizio, dominio_base):
    """Determina l'URL di streaming per le partite dell'Inter in base alla piattaforma."""
    servizio_lower = (servizio or "").lower()

    # Se è in chiaro (es. Mediaset), non viene fornito un link pirata
    if "mediaset" in servizio_lower:
        return "", True

    if "dazn" in servizio_lower:
        percorso = "/watch.php?id=877"
    elif "prime" in servizio_lower:
        percorso = "/watch.php?id=461"
    else:
        # Default per Sky / NOW / Altri
        percorso = "/watch.php?id=461"

    return f"{dominio_base}{percorso}", False


def elabora_evento_oggi(eventi, oggi_roma, fuso_utc, fuso_roma):
    """Filtra gli eventi cercando quello che ricade nella giornata odierna in Italia,

    convertendo data e ora da UTC al fuso orario di Roma.
    """
    if not isinstance(eventi, list):
        return None, None

    for evento in eventi:
        if not isinstance(evento, dict):
            continue

        data_str = evento.get("data")
        if not data_str:
            continue

        ora_raw = evento.get("ora") or evento.get("orario")
        ora_str = pulisci_orario(ora_raw)

        try:
            # 1. Combina data e ora UTC
            dt_utc = datetime.strptime(
                f"{data_str} {ora_str}", "%Y-%m-%d %H:%M"
            ).replace(tzinfo=fuso_utc)

            # 2. Converte nel fuso di Roma (gestisce automaticamente ora legale e solare)
            dt_roma = dt_utc.astimezone(fuso_roma)

            # 3. Verifica se l'evento appartiene alla giornata odierna italiana
            if dt_roma.strftime("%Y-%m-%d") == oggi_roma:
                return evento, dt_roma
        except ValueError:
            # Fallback se la stringa data non è standard
            if data_str == oggi_roma:
                return evento, None

    return None, None


def main():
    fuso_roma = ZoneInfo("Europe/Rome")
    fuso_utc = ZoneInfo("UTC")

    ora_attuale_roma = datetime.now(fuso_roma)
    oggi_roma = ora_attuale_roma.strftime("%Y-%m-%d")

    # Trova il dominio mirror funzionante
    dominio_base = trova_dominio_base_attivo()
    stream_output = {}

    # ==========================================
    # 1. ELABORAZIONE INTER (calendar.json)
    # ==========================================
    partite_inter = []
    if os.path.exists("calendar.json"):
        try:
            with open("calendar.json", "r", encoding="utf-8") as f:
                cal = json.load(f)
                if isinstance(cal, list):
                    partite_inter = cal
                elif isinstance(cal, dict):
                    partite_inter = cal.get("partite", [])
        except Exception as e:
            print(f"Attenzione: errore lettura calendar.json: {e}")

    partita_oggi, dt_roma_inter = elabora_evento_oggi(
        partite_inter, oggi_roma, fuso_utc, fuso_roma
    )

    if partita_oggi:
        servizio_inter = partita_oggi.get("servizio", "")
        url_finale_inter, in_chiaro = ottieni_url_stream_inter(
            servizio_inter, dominio_base
        )

        stream_output["inter"] = {
            "attivo": True,
            "in_chiaro": in_chiaro,
            "data": (
                dt_roma_inter.strftime("%Y-%m-%d")
                if dt_roma_inter
                else oggi_roma
            ),
            "ora": (
                dt_roma_inter.strftime("%H:%M")
                if dt_roma_inter
                else pulisci_orario(partita_oggi.get("ora"))
            ),
            "partita": partita_oggi.get("partita"),
            "home_team": partita_oggi.get("home_team"),
            "away_team": partita_oggi.get("away_team"),
            "home_logo": partita_oggi.get("home_logo"),
            "away_logo": partita_oggi.get("away_logo"),
            "competizione": partita_oggi.get("competizione"),
            "servizio": servizio_inter,
            "url": url_finale_inter,
        }
    else:
        stream_output["inter"] = {
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
            "url": "",
        }

    # ==========================================
    # 2. ELABORAZIONE FORMULA 1 (f1_calendar.json)
    # ==========================================
    gare_f1 = []
    if os.path.exists("f1_calendar.json"):
        try:
            with open("f1_calendar.json", "r", encoding="utf-8") as f:
                cal_f1 = json.load(f)
                if isinstance(cal_f1, list):
                    gare_f1 = cal_f1
                elif isinstance(cal_f1, dict):
                    gare_f1 = (
                        cal_f1.get("gare")
                        or cal_f1.get("races")
                        or cal_f1.get("partite", [])
                    )
        except Exception as e:
            print(f"Attenzione: errore lettura f1_calendar.json: {e}")

    gara_oggi, dt_roma_f1 = elabora_evento_oggi(
        gare_f1, oggi_roma, fuso_utc, fuso_roma
    )

    if gara_oggi:
        # Per la F1 il canale dedicato su Sky Sport F1 è id=555
        url_finale_f1 = f"{dominio_base}/watch.php?id=555"

        stream_output["f1"] = {
            "attivo": True,
            "in_chiaro": False,
            "data": (
                dt_roma_f1.strftime("%Y-%m-%d") if dt_roma_f1 else oggi_roma
            ),
            "ora": (
                dt_roma_f1.strftime("%H:%M")
                if dt_roma_f1
                else pulisci_orario(gara_oggi.get("ora"))
            ),
            "partita": gara_oggi.get("partita"),
            "competizione": "Formula 1",
            "servizio": gara_oggi.get("servizio", "NOW / Sky"),
            "url": url_finale_f1,
        }
    else:
        stream_output["f1"] = {
            "attivo": False,
            "in_chiaro": False,
            "data": oggi_roma,
            "ora": None,
            "partita": None,
            "competizione": None,
            "servizio": None,
            "url": "",
        }

    # ==========================================
    # 3. SALVATAGGIO IN STREAM.JSON
    # ==========================================
    try:
        with open("stream.json", "w", encoding="utf-8") as f:
            json.dump(stream_output, f, indent=2, ensure_ascii=False)
        print("stream.json (Inter & F1) aggiornato con successo.")
    except Exception as e:
        print(f"Errore durante la scrittura di stream.json: {e}")


if __name__ == "__main__":
    main()
