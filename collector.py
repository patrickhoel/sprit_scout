import os
import requests
import sqlite3
import time
from datetime import datetime
from dotenv import load_dotenv

# 1. Key laden
# Key für den Zugriff auf die freie Tankerkönig-Spritpreis-API.
# Für einen eigenen Key bitte unter https://creativecommons.tankerkoenig.de registrieren.
# Der Key muss in einer .env Datei als TANKERKOENIG_API_KEY hinterlegt werden.
load_dotenv()
API_KEY = os.getenv("TANKERKOENIG_API_KEY")

if not API_KEY:
    print("❌ FEHLER: Kein API_KEY in der .env gefunden!")
    exit()

# --- KONFIGURATION ---
LAT = 51.2562
LNG = 7.1508
RADIUS = 15
INTERVALL = 300  # 300 Sekunden = 5 Minuten

def check_preis_geaendert(cursor, name, e5, e10, diesel):
    """Prüft, ob sich der Preis zur letzten Speicherung geändert hat."""
    cursor.execute('''
        SELECT e5, e10, diesel FROM preise 
        WHERE tankstelle = ? 
        ORDER BY zeitstempel DESC LIMIT 1
    ''', (name,))
    last_entry = cursor.fetchone()
    
    if last_entry is None:
        return True  # Noch kein Eintrag vorhanden, also speichern
    
    # Vergleichen: Hat sich mindestens ein Preis geändert?
    return (e5 != last_entry[0] or e10 != last_entry[1] or diesel != last_entry[2])

def daten_sammeln():
    url = f"https://creativecommons.tankerkoenig.de/json/list.php?lat={LAT}&lng={LNG}&rad={RADIUS}&type=all&apikey={API_KEY}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Server-Fehler {response.status_code}")
            return

        data = response.json()
        if data.get('ok'):
            conn = sqlite3.connect('spritpreise.db')
            cursor = conn.cursor()
            zeitstempel = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            count_saved = 0
            for station in data.get('stations', []):
                # 1. Den rohen Namen, Marke und Adresse vom Tankerkönig holen
                raw_name = station.get('name', '').strip()
                brand = station.get('brand', '').strip()
                street = station.get('street', '').strip()
                house = station.get('houseNumber', '').strip()
                
                # Wenn der Name komplett leer ist, nehmen wir stattdessen die Marke (z.B. "HEM")
                if not raw_name:
                    raw_name = brand if brand else "Unbekannte Tankstelle"
                # Falls die Marke existiert, aber gar nicht im Namen vorkommt, setzen wir sie davor
                elif brand and brand.upper() not in raw_name.upper():
                    raw_name = f"{brand} {raw_name}"
                
                # 2. Einen einzigartigen Namen inkl. Straße basteln
                if street:
                    name = f"{raw_name} ({street} {house})".strip()
                else:
                    name = raw_name

                # 3. Die restlichen Daten holen
                e5 = station.get('e5')
                e10 = station.get('e10')
                diesel = station.get('diesel')
                lat = station.get('lat')
                lng = station.get('lng')

                # Nur prüfen/speichern, wenn Preise valide sind
                if all(v is not None and isinstance(v, (int, float)) and v > 0 for v in [e5, e10, diesel]):
                    if check_preis_geaendert(cursor, name, e5, e10, diesel):
                        cursor.execute('''
                            INSERT INTO preise (zeitstempel, tankstelle, e5, e10, diesel, lat, lng)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (zeitstempel, name, e5, e10, diesel, lat, lng))
                        count_saved += 1
            
            conn.commit()
            if count_saved > 0:
                print(f"✅ [{zeitstempel}] {count_saved} Preisänderungen gespeichert.")
            else:
                print(f"😴 [{zeitstempel}] Keine Preisänderungen erkannt.")
            
            # Housekeeping
            cursor.execute("DELETE FROM preise WHERE zeitstempel < datetime('now', '-30 days')")
            conn.commit()
            conn.close()
            
    except Exception as e:
        # Den Fehlertext als String greifen und den API_KEY durch Sternchen ersetzen
        fehler_text = str(e).replace(API_KEY, "*****VERSTECKT*****")
        print(f"❌ Kritischer Fehler: {fehler_text}")

if __name__ == "__main__":
    print(f"🚀 Collector gestartet (Intervall: {INTERVALL/60} Min)")
    while True:
        daten_sammeln()
        time.sleep(INTERVALL)