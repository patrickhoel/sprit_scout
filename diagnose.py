import sqlite3
import pandas as pd

# Verbinden mit deiner heruntergeladenen Datenbank
conn = sqlite3.connect('spritpreise.db')

print("🔍 STARTE DATENBANK-ANALYSE...\n")

# 1. Status der Aral-Tankstellen checken
print("1️⃣ STATUS DER ARAL-TANKSTELLEN:")
df_aral = pd.read_sql_query("""
    SELECT tankstelle, COUNT(*) as anzahl_updates, MAX(zeitstempel) as letztes_update 
    FROM preise 
    WHERE tankstelle LIKE '%Aral%' 
    GROUP BY tankstelle
""", conn)
print(df_aral.to_string(index=False) if not df_aral.empty else "Keine Aral gefunden!")
print("\n" + "-"*50 + "\n")

# 2. Die absoluten Sorgenkinder (Tankstellen mit den wenigsten Updates)
print("2️⃣ DIE SCHWARZEN SCHAFE (Wenigste Updates):")
df_wenig = pd.read_sql_query("""
    SELECT tankstelle, COUNT(*) as anzahl_updates, MAX(zeitstempel) as letztes_update 
    FROM preise 
    GROUP BY tankstelle 
    ORDER BY anzahl_updates ASC 
    LIMIT 10
""", conn)
print(df_wenig.to_string(index=False))

conn.close()