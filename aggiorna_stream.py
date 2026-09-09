import json
from datetime import datetime
import requests

# 1. DOMINI BASE DA TESTARE (In ordine di preferenza)
DOMINI_STREAM = [
    "https://dlhd.pk",
    "https://dlhd.st",
    "https://dstreams.st"
]

# 2. MAPPA CANALI / PARAMETRI PER SERVIZIO
# Associa ciascun servizio al percorso/ID del relativo player
CANALI_SERVIZI = {
    "DAZN": "/watch.php?id=877",
    "Prime Video": "/watch.php?id=461",
    "Mediaset": "/watch.php?id=893", #----- DA RISOLVERERE------
    "Sky / NOW": "/watch.php?id=461"
}

# 3. VERIFICA IL DOMINIO BASE FUNZIONANTE
def trova_dominio_base_attivo():
    """Testa i domini base e restituisce il primo raggiungibile."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for dominio in DOMINI_STREAM:
        try:
            # Controllo veloce sul dominio base con timeout di 3 secondi
            response = requests.head(dominio, timeout=3, allow_redirects=True, headers=headers)
            if response.status_code < 400:
                print(f"[OK] Dominio attivo trovato: {dominio}")
                return dominio
        except requests.RequestException:
            print(f"[FAIL] Dominio non raggiungibile: {dominio}")
            continue

    # Fallback al primo se nessuno risponde
    return DOMINI_STREAM[0]

# 4. LOGICA PRINCIPALE
def main():
    oggi = datetime.now().strftime("%Y-%m-%d")
    
    # Carica il calendario
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

    # Se c'è una partita oggi
    if partita_di_oggi:
        servizio = partita_di_oggi.get("servizio")
        
        # 1. Recupera il percorso del canale (es. /watch.php?id=891)
        percorso_canale = CANALI_SERVIZI.get(servizio, "")
        
        # 2. Trova il primo dominio base funzionante
        dominio_base = trova_dominio_base_attivo()
        
        # 3. Componi l'URL completo finale
        url_finale = f"{dominio_base}{percorso_canale}" if percorso_canale else ""

        stream_data = {
            "attivo": True,
            "data": oggi,
            "partita": partita_di_oggi.get("partita"),
            "competizione": partita_di_oggi.get("competizione"),
            "servizio": servizio,
            "url": url_finale
        }
    else:
        # Nessuna partita oggi
        stream_data = {
            "attivo": False,
            "data": oggi,
            "partita": None,
            "competizione": None,
            "servizio": None,
            "url": ""
        }

    # Salva il risultato in stream.json
    with open("stream.json", "w", encoding="utf-8") as f:
        json.dump(stream_data, f, indent=2, ensure_ascii=False)
    
    print("stream.json aggiornato con successo.")

if __name__ == "__main__":
    main()
