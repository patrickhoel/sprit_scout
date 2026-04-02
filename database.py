import sqlite3

def create_database():
    # Verbindet sich mit der Datenbank (erstellt die Datei 'spritpreise.db', falls sie noch nicht existiert)
    conn = sqlite3.connect('spritpreise.db')
    
    # Der Cursor führt unsere Befehle in der Datenbank aus
    cursor = conn.cursor()
    
    # Wir erstellen unsere Tabelle (falls sie noch nicht existiert)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preise (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zeitstempel DATETIME DEFAULT CURRENT_TIMESTAMP,
            tankstelle TEXT,
            adresse TEXT,
            e5 REAL,
            e10 REAL,
            diesel REAL
        )
    ''')
    
    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()
    
    print("Datenbank und Tabelle wurden erfolgreich erstellt!")

# Dieser Block sorgt dafür, dass die Funktion ausgeführt wird, wenn wir die Datei starten
if __name__ == '__main__':
    create_database()