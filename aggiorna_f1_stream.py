import json
import urllib.request

PRIMARY_API_URL = "https://api.jolpi.ca/ergast/f1/current.json"
PRIMARY_QUALY_URL = "https://api.jolpi.ca/ergast/f1/current/qualifying.json?limit=100"
FALLBACK_API_URL = "https://ergast.com/api/f1/current.json"

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
    if not time_str:
        return "15:00"
    time_str = time_str.replace("Z", "")
    parts = time_str.split(":")
    if len(parts) >= 2:
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    return time_str

def fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ArmadilloStreams/1.0 (https://github.com/Wwhiplashh/ArmadilloStreams)"
        }
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))

def fetch_ferrari_qualy_results():
    """Recupera le posizioni in qualifica dei piloti Ferrari."""
    ferrari_results = {}
    try:
        data = fetch_json(PRIMARY_QUALY_URL)
        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        for race in races:
            round_num = race.get("round")
            qualy_list = race.get("QualifyingResults", [])
            ferrari_drivers = []
            
            for res in qualy_list:
                constructor_id = res.get("Constructor", {}).get("constructorId", "").lower()
                if constructor_id == "ferrari":
                    driver_code = res.get("Driver", {}).get("code") or res.get("Driver", {}).get("familyName", "")[:3].upper()
                    pos = res.get("position")
                    ferrari_drivers.append(f"{driver_code} P{pos}")
            
            if ferrari_drivers:
                ferrari_results[round_num] = " | ".join(ferrari_drivers)
    except Exception as e:
        print(f"⚠️ Impossibile recuperare risultati qualifiche Ferrari: {e}")
    
    return ferrari_results

def fetch_f1_calendar(include_practices=False):
    print("🔍 Interrogazione API Formula 1 in corso...")
    data = None
    
    try:
        data = fetch_json(PRIMARY_API_URL)
    except Exception as e:
        print(f"⚠️ API principale fallita: {e}. Tentativo backup...")
        try:
            data = fetch_json(FALLBACK_API_URL)
        except Exception as err_fallback:
            print(f"❌ Errore irreversibile: {err_fallback}")
            return

    races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
    if not races:
        print("⚠️ Nessuna gara trovata.")
        return

    ferrari_qualy = fetch_ferrari_qualy_results()
    gare_f1 = []

    for race in races:
        raw_name = race.get("raceName", "Gran Premio")
        gp_base_name = GP_NAMES_IT.get(raw_name, raw_name.replace("Grand Prix", "GP"))
        round_num = race.get("round")

        # Qualifiche Ufficiali
        if "Qualifying" in race and "date" in race["Qualifying"]:
            qual = race["Qualifying"]
            item = {
                "data": qual["date"],
                "ora": clean_time(qual.get("time")),
                "gran_premio": f"{gp_base_name} - Qualifiche",
                "competizione": "Formula 1",
                "servizio": "Sky Sport F1 / NOW"
            }
            if round_num in ferrari_qualy:
                item["ferrari_qualy"] = ferrari_qualy[round_num]
            gare_f1.append(item)

        # Gara Domenicale
        if "date" in race:
            gare_f1.append({
                "data": race["date"],
                "ora": clean_time(race.get("time")),
                "gran_premio": f"{gp_base_name} - Gara",
                "competizione": "Formula 1",
                "servizio": "Sky Sport F1 / NOW"
            })

    gare_f1.sort(key=lambda x: f"{x['data']}T{x['ora']}")

    with open("f1_calendar.json", "w", encoding="utf-8") as f:
        json.dump({"gare": gare_f1}, f, indent=2, ensure_ascii=False)

    print("✅ Generato f1_calendar.json con successo!")

if __name__ == "__main__":
    fetch_f1_calendar()
