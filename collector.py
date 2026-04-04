import os
import requests
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# 1. Key laden
load_dotenv()
API_KEY = os.getenv("TANKERKOENIG_API_KEY")

if not API_KEY:
    print("❌ FEHLER: Kein API_KEY in der .env gefunden!")
    exit()

# --- KONFIGURATION ---
# Wuppertal Zentrum
LAT = 51.2562
LNG = 7.1508
RADIUS = 15

def daten_sammeln():
    # KORRIGIERTE URL: Die offizielle Tankerkönig-Schnittstelle
    url = f"https://creativecommons.tankerkoenig.de/json/list.php?lat={LAT}&lng={LNG}&rad={RADIUS}&type=all&apikey={API_KEY}"
    
    # CHROME DISGUISE: Wir tarnen uns als ganz normaler Windows-Browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    try:
        print(f"📡 Starte Abfrage an Tankerkönig...")
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Server-Fehler {response.status_code}: Zugriff verweigert.")
            print("Mögliche Ursachen: API-Key noch nicht aktiv (dauert bis zu 24h) oder falscher Endpoint.")
            return

        data = response.json()
        
        if data.get('ok'):
            conn = sqlite3.connect('spritpreise.db')
            cursor = conn.cursor()
            zeitstempel = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            count = 0
            for station in data.get('stations', []):
                name = station.get('name')
                e5 = station.get('e5')
                e10 = station.get('e10')
                diesel = station.get('diesel')
                lat = station.get('lat')
                lng = station.get('lng')
                
                # Wir speichern nur, wenn die API echte Preise liefert
                if all(v is not None and isinstance(v, (int, float)) and v > 0 for v in [e5, e10, diesel]):
                    cursor.execute('''
                        INSERT INTO preise (zeitstempel, tankstelle, e5, e10, diesel, lat, lng)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (zeitstempel, name, e5, e10, diesel, lat, lng))
                    count += 1
            
            conn.commit()
            print(f"✅ [{zeitstempel}] {count} Tankstellen mit Koordinaten gespeichert.")
            
            # Housekeeping: Daten älter als 30 Tage löschen
            cursor.execute("DELETE FROM preise WHERE zeitstempel < datetime('now', '-30 days')")
            conn.commit()
            conn.close()
        else:
            print(f"⚠️ API-Fehler: {data.get('message', 'Unbekannter Fehler')}")
            
    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")

if __name__ == "__main__":
    daten_sammeln()