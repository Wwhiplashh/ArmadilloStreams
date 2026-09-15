import json
from datetime import datetime, timezone

def aggiorna_f1_stream():
    ora_attuale = datetime.now(timezone.utc)
    data_oggi = ora_attuale.strftime("%Y-%m-%d")

    # URL dello streaming F1 (inserisci il tuo link predefinito se disponibile)
    STREAM_URL_F1 = "" 

    stream_data = {
        "attivo": False,
        "url": STREAM_URL_F1,
        "gran_premio": ""
    }

    try:
        with open("f1_calendar.json", "r", encoding="utf-8") as f:
            cal_data = json.load(f)
            gare = cal_data.get("gare", [])

        # Cerca se c'è una sessione in programma per la data odierna
        for gara in gare:
            if gara.get("data") == data_oggi:
                stream_data["attivo"] = True
                stream_data["gran_premio"] = gara.get("gran_premio", "Gran Premio F1")
                break

    except FileNotFoundError:
        print("⚠️ File f1_calendar.json non trovato.")
    except Exception as e:
        print(f"⚠️ Errore durante la lettura del calendario F1: {e}")

    with open("f1_stream.json", "w", encoding="utf-8") as f:
        json.dump(stream_data, f, indent=2, ensure_ascii=False)

    print(f"✅ f1_stream.json aggiornato con successo! Stato attivo: {stream_data['attivo']}")

if __name__ == "__main__":
    aggiorna_f1_stream()
