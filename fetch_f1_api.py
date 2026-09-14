import json
import urllib.request

# URL dell'API gratuita di Formula 1 (Stagione Corrente)
API_URL = "https://api.jolpica.net/ergast/f1/current.json"

# Mappatura per tradurre i nomi dei Gran Premi in italiano
GP_NAMES_IT = {
    "Australian Grand Prix": "GP d'Australia",
    "Bahrain Grand Prix": "GP del Bahrain",
    "Saudi Arabian Grand Prix": "GP dell'Arabia Saudita",
    "Japanese Grand Prix": "GP del Giappone",
    "Chinese Grand Prix": "GP della Cina",
    "Miami Grand Prix": "GP di Miami",
    "Emilia Romagna Grand Prix": "GP dell'Emilia-Romagna (Imola)",
    "Monaco Grand Prix": "GP di Monaco",
    "Canadian Grand Prix": "GP del Canada",
    "Spanish Grand Prix": "GP di Spagna",
    "Austrian Grand Prix": "GP d'Austria",
    "British Grand Prix": "GP di Gran Bretagna (Silverstone)",
    "Hungarian Grand Prix": "GP d'Ungheria",
    "Belgian Grand Prix": "GP del Belgio (Spa)",
    "Dutch Grand Prix": "GP d'Olanda (Zandvoort)",
    "Italian Grand Prix": "GP d'Italia (Monza)",
    "Azerbaijan Grand Prix": "GP dell'Azerbaigian",
    "Singapore Grand Prix": "GP di Singapore",
    "United States Grand Prix": "GP degli Stati Uniti (Austin)",
    "Mexico City Grand Prix": "GP del Messico",
    "São Paulo Grand Prix": "GP di San Paolo",
    "Las Vegas Grand Prix": "GP di Las Vegas",
    "Qatar Grand Prix": "GP del Qatar",
    "Abu Dhabi Grand Prix": "GP di Abu Dhabi",
}

def clean_time(time_str):
    """
    Rimuove i secondi e il carattere 'Z' dall'orario UTC dell'API.
    Esempio: '14:00:00Z' -> '14:00'
    """
    if not time_str:
        return "15:00"
    time_str = time_str.replace("Z", "")
    parts = time_str.split(":")
    if len(parts) >= 2:
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    return time_str

def fetch_f1_calendar(include_practices=False):
    req = urllib.request.Request(
        API_URL,
        headers={
            "User-Agent": "ArmadilloStreams/1.0 (https://github.com/Wwhiplashh/ArmadilloStreams)"
        }
    )

    try:
        print("🔍 Interrogazione API Formula 1 in corso...")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"❌ Errore durante il recupero dei dati dall'API: {e}")
        return

    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    
    if not races:
        print("⚠️ Nessuna gara trovata per la stagione corrente.")
        return

    gare_f1 = []

    for race in races:
        raw_name = race.get("raceName", "Gran Premio")
        gp_base_name = GP_NAMES_IT.get(raw_name, raw_name.replace("Grand Prix", "GP"))

        # Configurazione sessioni del weekend da includere
        sessions_map = [
            # Prove Libere (facoltative, disattivate di default)
            ("FirstPractice", "Prove Libere 1", include_practices),
            ("SecondPractice", "Prove Libere 2", include_practices),
            ("ThirdPractice", "Prove Libere 3", include_practices),
            # Qualifiche Sprint (Sprint Shootout)
            ("SprintQualifying", "Qualifiche Sprint", True),
            ("SprintShootout", "Qualifiche Sprint", True),
            # Gara Sprint
            ("Sprint", "Gara Sprint", True),
            # Qualifiche Ufficiali
            ("Qualifying", "Qualifiche", True),
        ]

        for key, label, enabled in sessions_map:
            if enabled and key in race and "date" in race[key]:
                sess = race[key]
                gare_f1.append({
                    "data": sess["date"],
                    "ora": clean_time(sess.get("time")),
                    "gran_premio": f"{gp_base_name} - {label}",
                    "competizione": "Formula 1",
                    "servizio": "Sky Sport F1 / NOW"
                })

        # Gara Domenicale / Principale
        if "date" in race:
            gare_f1.append({
                "data": race["date"],
                "ora": clean_time(race.get("time")),
                "gran_premio": f"{gp_base_name} - Gara",
                "competizione": "Formula 1",
                "servizio": "Sky Sport F1 / NOW"
            })

    # Rimozione eventuali duplicati mantenendo l'ordine
    seen = set()
    unique_gare = []
    for item in gare_f1:
        identifier = (item["data"], item["ora"], item["gran_premio"])
        if identifier not in seen:
            seen.add(identifier)
            unique_gare.append(item)

    # Ordina cronologicamente tutte le sessioni (data + ora)
    unique_gare.sort(key=lambda x: f"{x['data']}T{x['ora']}")

    output_data = {"gare": unique_gare}

    # Salva il file f1_calendar.json
    with open("f1_calendar.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Generato f1_calendar.json con successo!")
    print(f"📊 Totale sessioni registrate (Qualifiche + Gare): {len(unique_gare)}")

if __name__ == "__main__":
    # Imposta include_practices=True se desideri salvare nel JSON anche FP1, FP2, FP3
    fetch_f1_calendar(include_practices=False)
