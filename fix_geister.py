import sqlite3

def loesche_alte_geister():
    print("Starte Staubsauger für Geister-Einträge...")
    conn = sqlite3.connect('spritpreise.db')
    cursor = conn.cursor()

    # Wir löschen alle Einträge, bei denen keine Koordinaten gespeichert wurden 
    # (also NULL, leere Strings oder 0)
    cursor.execute("""
        DELETE FROM preise 
        WHERE lat IS NULL 
           OR lng IS NULL 
           OR lat = '' 
           OR lng = ''
           OR lat = 0
    """)
    
    geloescht = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"Bäm! {geloescht} alte, unzuweisbare Einträge wurden restlos gelöscht.")
    print("Deine Datenbank ist jetzt zu 100% auf dem neuen Standard!")

if __name__ == "__main__":
    loesche_alte_geister()