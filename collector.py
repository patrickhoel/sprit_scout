import sqlite3
import requests
import os
from dotenv import load_dotenv

# Lädt den API-Key aus deiner .env Datei
load_dotenv()
API_KEY = os.getenv("TANKERKOENIG_API_KEY")          

# Hier deine Koordinaten und den Suchradius in Kilometern eintragen
LAT = 51.285889    # Breitengrad (Latitude) - hier Beispiel Wuppertal
LNG = 7.229750    # Längengrad (Longitude) - hier Beispiel Wuppertal
RADIUS = 10      # 10 Kilometer Umkreis

def get_api_preise():
    """Holt die echten Daten von der Tankerkönig API."""
    print("Frage Tankerkönig API ab...")
    url = f"https://creativecommons.tankerkoenig.de/json/list.php?lat={LAT}&lng={LNG}&rad={RADIUS}&sort=dist&type=all&apikey={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status() # Wirft einen Fehler, wenn die Internetverbindung fehlschlägt
        daten = response.json()
        
        if daten.get("ok"):
            tankstellen_daten = []
            for t in daten.get("stations", []):
                # Wir nehmen nur Tankstellen, die gerade offen sind
                if t.get("isOpen"):
                    # Name und Marke zusammenbauen, damit es in der Auswertung hübscher aussieht
                    marke = t.get("brand", "").strip()
                    name = t.get("name", "").strip()
                    vollständiger_name = f"{marke} ({name})" if marke else name

                    tankstellen_daten.append({
                        "name": vollständiger_name,
                        "adresse": f"{t.get('street')} {t.get('houseNumber')}",
                        "e5": t.get("e5"),
                        "e10": t.get("e10"),
                        "diesel": t.get("diesel")
                    })
            return tankstellen_daten
        else:
            print("Fehler von der API:", daten.get("message"))
            return []
            
    except Exception as e:
        print(f"Fehler beim Abrufen der API: {e}")
        return []

def speichere_in_db(daten):
    """Speichert die übergebenen Daten in unsere SQLite-Datenbank."""
    if not daten:
        print("Keine Daten zum Speichern vorhanden.")
        return

    conn = sqlite3.connect('spritpreise.db')
    cursor = conn.cursor()
    
    for eintrag in daten:
        # Das ? schützt unsere Datenbank vor fehlerhaften Eingaben
        cursor.execute('''
            INSERT INTO preise (tankstelle, adresse, e5, e10, diesel)
            VALUES (?, ?, ?, ?, ?)
        ''', (eintrag['name'], eintrag['adresse'], eintrag['e5'], eintrag['e10'], eintrag['diesel']))
    
    conn.commit()
    conn.close()
    print(f"{len(daten)} echte Preis-Einträge erfolgreich in die Datenbank geschrieben!")

if __name__ == '__main__':
    neue_daten = get_api_preise()
    speichere_in_db(neue_daten)