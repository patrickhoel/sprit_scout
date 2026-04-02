import sqlite3

conn = sqlite3.connect('spritpreise.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM preise") # Löscht alle Zeilen in der Tabelle 'preise'
conn.commit()
conn.close()
print("Datenbank wurde geleert!")