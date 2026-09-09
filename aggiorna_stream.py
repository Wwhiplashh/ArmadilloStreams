import json
from datetime import datetime

def genera_stream():
    # Recupera la data di oggi nel formato YYYY-MM-DD
    oggi = datetime.now().strftime("%Y-%m-%d")
    
    # Carica il calendario delle partite
    try:
        with open("calendar.json", "r", encoding="utf-8") as f:
            calendario = json.load(f)
    except FileNotFoundError:
        print("File calendar.json non trovato.")
        return

    # Cerca la partita in programma per oggi
    partita_di_oggi = None
    for evento in calendario:
        if evento.get("data") == oggi:
            partita_di_oggi = evento
            break

    # Se c'è una partita oggi, imposta i dati, altrimenti imposta uno stato di default/riposo
    if partita_di_oggi:
        stream_data = {
            "attivo": True,
            "data": oggi,
            "partita": partita_di_oggi.get("partita"),
            "servizio": partita_di_oggi.get("servizio"),
            "url": partita_di_oggi.get("url")
        }
        print(f"Trovata partita per oggi ({oggi}): {partita_di_oggi['partita']}")
    else:
        stream_data = {
            "attivo": False,
            "data": oggi,
            "partita": "Nessuna partita programmata per oggi",
            "servizio": "N/A",
            "url": ""
        }
        print(f"Nessuna partita in programma per oggi ({oggi}).")

    # Salva il risultato in stream.json
    with open("stream.json", "w", encoding="utf-8") as f:
        json.dump(stream_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    genera_stream()
