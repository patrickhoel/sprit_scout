import streamlit as st
import pandas as pd
import sqlite3
from PIL import Image

icon = Image.open("logo.png")

st.set_page_config(
    page_title="Sprit Scout", 
    page_icon=icon, # Hier nutzen wir jetzt dein Bild statt dem Emoji
    layout="centered"
)

# 1. Seiten-Konfiguration (Optimiert für Mobile)
st.title("⛽ Sprit Scout")

def lade_daten():
    conn = sqlite3.connect('spritpreise.db')
    df = pd.read_sql_query("SELECT * FROM preise ORDER BY zeitstempel ASC", conn)
    conn.close()
    
    # Zeitstempel von UTC in lokale Zeit (Wuppertal/Berlin) umwandeln
    df['zeitstempel'] = pd.to_datetime(df['zeitstempel']).dt.tz_localize('UTC').dt.tz_convert('Europe/Berlin')
    return df

df = lade_daten()

if not df.empty:
    # --- BEREICH 1: QUICK-CHECK (Die 3 günstigsten) ---
    st.subheader("🚀 Günstigste Preise aktuell")
    
    # Wir filtern die aktuellsten Preise pro Tankstelle heraus
    aktuell = df.sort_values('zeitstempel', ascending=False).drop_duplicates('tankstelle')
    
    # Drei Spalten für die großen Zahlen (Metrics)
    m1, m2, m3 = st.columns(3)
    
    with m1:
        min_e5 = aktuell.loc[aktuell['e5'].idxmin()]
        st.metric("E5", f"{min_e5['e5']:.2f}€", min_e5['tankstelle'])
        
    with m2:
        min_e10 = aktuell.loc[aktuell['e10'].idxmin()]
        st.metric("E10", f"{min_e10['e10']:.2f}€", min_e10['tankstelle'])
        
    with m3:
        min_diesel = aktuell.loc[aktuell['diesel'].idxmin()]
        st.metric("Diesel", f"{min_diesel['diesel']:.2f}€", min_diesel['tankstelle'])

    st.divider()

    # --- BEREICH 2: TABS (Für die platzsparende Analyse) ---
    tab_chart, tab_list, tab_info = st.tabs(["📈 Verlauf", "📋 Liste", "📍 Info"])

    with tab_chart:
        sorte = st.selectbox("Sprit wählen:", ["e5", "e10", "diesel"], key="mobile_select")
        # Pivot-Tabelle für das Diagramm
        chart_data = df.pivot_table(index='zeitstempel', columns='tankstelle', values=sorte, aggfunc='mean')
        st.line_chart(chart_data)

    with tab_list:
        # Nur die wichtigsten Spalten anzeigen und Zeit schön formatieren
        display_df = df.copy()
        display_df['zeitstempel'] = display_df['zeitstempel'].dt.strftime('%H:%M')
        # Wir zeigen die neuesten Einträge oben an
        st.dataframe(display_df.iloc[::-1][["zeitstempel", "tankstelle", "e5", "e10", "diesel"]], width='stretch')

    with tab_info:
        st.write("**Über Sprit Scout:**")
        st.info("Daten werden alle 30 Minuten automatisch abgefragt. Dein System ist bereit für den 12:00 Uhr Preissprung!")

else:
    st.info("Warte auf Daten vom Scheduler...")
