import sqlite3

def repariere_historie():
    print("Starte Datenbank-Reparatur...")
    conn = sqlite3.connect('spritpreise.db')
    cursor = conn.cursor()

    # 1. Wir suchen alle "neuen" Namen (die mit einer Klammer für die Straße)
    # und merken uns deren exakte GPS-Koordinaten.
    cursor.execute("""
        SELECT tankstelle, lat, lng 
        FROM preise 
        WHERE tankstelle LIKE '%(%)%' 
        GROUP BY lat, lng
    """)
    gute_eintraege = cursor.fetchall()

    count = 0
    for neu_name, lat, lng in gute_eintraege:
        # 2. Jetzt updaten wir alle alten Einträge, die an diesen Koordinaten 
        # liegen, aber noch den alten (kurzen) Namen haben.
        cursor.execute("""
            UPDATE preise 
            SET tankstelle = ? 
            WHERE lat = ? AND lng = ? AND tankstelle != ?
        """, (neu_name, lat, lng, neu_name))
        
        count += cursor.rowcount

    conn.commit()
    conn.close()
    print(f"Fertig! Es wurden {count} alte Preis-Einträge auf die neuen Straßennamen aktualisiert.")
    print("Deine Historie ist gerettet und die App ist aufgeräumt!")

if __name__ == "__main__":
    repariere_historie()