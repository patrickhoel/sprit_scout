import streamlit as st
import pandas as pd
import sqlite3

# 1. Seiten-Konfiguration (Muss die allererste Streamlit-Zeile sein)
st.set_page_config(page_title="Sprit Scout Pro", page_icon="⛽", layout="wide")

st.title("⛽ Sprit Scout - Preis-Analyse")

def lade_daten():
    """Verbindet sich mit der DB und lädt die Daten."""
    conn = sqlite3.connect('spritpreise.db')
    df = pd.read_sql_query("SELECT * FROM preise ORDER BY zeitstempel ASC", conn)
    conn.close()
    # Zeitstempel laden und als UTC markieren
    df['zeitstempel'] = pd.to_datetime(df['zeitstempel']).dt.tz_localize('UTC')

    # In die lokale Zeitzone (z.B. Berlin/Wuppertal) umwandeln
    df['zeitstempel'] = df['zeitstempel'].dt.tz_convert('Europe/Berlin')
    return df

# Daten laden
df = lade_daten()

if not df.empty:
    # --- Bereich 1: Der Preisverlauf (Diagramm) ---
    st.subheader("📈 Preisverlauf über die Zeit")
    
    # WICHTIG: Nur EIN selectbox-Aufruf mit einem eindeutigen Key
    sorte = st.selectbox(
        "Kraftstoffsorte wählen:", 
        ["e5", "e10", "diesel"], 
        key="sorten_auswahl"
    )
    
    # pivot_table fängt Duplikate ab (nimmt den Durchschnitt, falls Zeiten identisch sind)
    chart_data = df.pivot_table(
        index='zeitstempel', 
        columns='tankstelle', 
        values=sorte, 
        aggfunc='mean'
    )
    
    st.line_chart(chart_data)

    st.divider()

    # --- Bereich 2: Die Tabelle ---
    st.subheader("📋 Letzte Aktualisierungen")
    
    # Kopie für die Anzeige formatieren
    display_df = df.copy()
    display_df['zeitstempel'] = display_df['zeitstempel'].dt.strftime('%d.%m. %H:%M')
    
    # Spaltennamen für den Benutzer hübsch machen
    display_df.columns = ["ID", "Zeit", "Tankstelle", "Adresse", "Benzin E5", "Benzin E10", "Diesel"]
    
    # Tabelle anzeigen (neueste Einträge oben)
    st.dataframe(display_df.iloc[::-1].drop(columns=["ID"]), width='stretch')

else:
    st.info("Noch keine Daten vorhanden. Der Scheduler wird bald die ersten Daten sammeln.")