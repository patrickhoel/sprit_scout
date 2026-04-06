import sqlite3

def mega_reparatur():
    print("🚀 Starte finale Datenbank-Reinigung (Gold-Standard)...")
    conn = sqlite3.connect('spritpreise.db')
    cursor = conn.cursor()

    # Wir suchen den jeweils längsten Namen pro Standort, 
    # der Klammern enthält. Der längste ist fast immer der mit Marke + Adresse.
    cursor.execute("""
        SELECT lat, lng, tankstelle
        FROM preise
        WHERE tankstelle LIKE '%(%)%'
        GROUP BY lat, lng
        HAVING MAX(LENGTH(tankstelle))
    """)
    gold_namen = cursor.fetchall()

    total_updates = 0
    for lat, lng, bester_name in gold_namen:
        # Jetzt bügeln wir diesen perfekten Namen über ALLE Einträge an diesem Standort
        cursor.execute("""
            UPDATE preise 
            SET tankstelle = ? 
            WHERE lat = ? AND lng = ? AND tankstelle != ?
        """, (bester_name, lat, lng, bester_name))
        
        total_updates += cursor.rowcount

    conn.commit()
    conn.close()
    print(f"✨ Bäm! {total_updates} Einträge wurden auf den Gold-Standard gebracht.")
    print("Deine App sollte jetzt absolut sauber sein.")

if __name__ == "__main__":
    mega_reparatur()