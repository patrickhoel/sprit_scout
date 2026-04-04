import streamlit as st
import pandas as pd
import sqlite3
from PIL import Image

icon = Image.open("logo.png")

st.set_page_config(
    page_title="Sprit Scout", 
    page_icon=icon,
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
        st.metric("E5", f"{min_e5['e5']:.2f}€")
        st.caption(f"📍 {min_e5['tankstelle']}")
        # Google Maps Link
        url_e5 = f"https://www.google.com/maps/search/?api=1&query={min_e5['tankstelle'].replace(' ', '+')}+Wuppertal"
        st.link_button("Anfahrt", url_e5, use_container_width=True)
        
    with m2:
        min_e10 = aktuell.loc[aktuell['e10'].idxmin()]
        st.metric("E10", f"{min_e10['e10']:.2f}€")
        st.caption(f"📍 {min_e10['tankstelle']}")
        url_e10 = f"https://www.google.com/maps/search/?api=1&query={min_e10['tankstelle'].replace(' ', '+')}+Wuppertal"
        st.link_button("Anfahrt", url_e10, use_container_width=True)
        
    with m3:
        min_diesel = aktuell.loc[aktuell['diesel'].idxmin()]
        st.metric("Diesel", f"{min_diesel['diesel']:.2f}€")
        st.caption(f"📍 {min_diesel['tankstelle']}")
        url_diesel = f"https://www.google.com/maps/search/?api=1&query={min_diesel['tankstelle'].replace(' ', '+')}+Wuppertal"
        st.link_button("Anfahrt", url_diesel, use_container_width=True)

    # --- BEREICH 2: TABS (Für die platzsparende Analyse) ---
    tab_chart, tab_list, tab_info = st.tabs(["📈 Verlauf", "📋 Liste", "📍 Info"])

    with tab_chart:
        sorte = st.selectbox("Sprit wählen:", ["e5", "e10", "diesel"], key="mobile_select")
        
        # NEU: Wir berechnen den Durchschnitt und den absoluten Tiefstpreis pro Uhrzeit
        trend_df = df.groupby('zeitstempel')[sorte].agg(['min', 'mean'])
        
        # Die Spalten hübsch umbenennen für die Legende
        trend_df = trend_df.rename(columns={
            'min': 'Günstigste Tankstelle', 
            'mean': 'Stadt-Durchschnitt'
        })
        
        # Ein aufgeräumtes Diagramm zeichnen
        st.line_chart(trend_df, color=["#00ff00", "#ff0000"]) # Grün für Bestpreis, Rot für Durchschnitt

    with tab_list:
        # Nur die wichtigsten Spalten anzeigen und Zeit schön formatieren
        display_df = df.copy()
        display_df['zeitstempel'] = display_df['zeitstempel'].dt.strftime('%H:%M')
        # Wir zeigen die neuesten Einträge oben an
        st.dataframe(display_df.iloc[::-1][["zeitstempel", "tankstelle", "e5", "e10", "diesel"]], width='stretch')

    with tab_info:
        st.write("**Über Sprit Scout:**")
        
        # Den neuesten Zeitstempel aus der Datenbank holen
        letzter_abruf = df['zeitstempel'].max().strftime('%d.%m.%Y um %H:%M Uhr')
        
        st.info(f"🤖 Die Daten werden alle 30 Minuten automatisch im Hintergrund aktualisiert.")
        st.success(f"⏱️ Letztes Preis-Update: **{letzter_abruf}**")
else:
    st.info("Warte auf Daten vom Scheduler...")
