import sqlite3

def upgrade_db():
    try:
        conn = sqlite3.connect('spritpreise.db')
        cursor = conn.cursor()
        
        # Spalten hinzufügen
        print("Bohre neue Spalten...")
        cursor.execute("ALTER TABLE preise ADD COLUMN lat REAL;")
        cursor.execute("ALTER TABLE preise ADD COLUMN lng REAL;")
        
        conn.commit()
        print("✅ Erfolg! 'lat' und 'lng' wurden hinzugefügt.")
    except sqlite3.OperationalError:
        print("ℹ️ Hinweis: Die Spalten existieren wahrscheinlich schon.")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_db()