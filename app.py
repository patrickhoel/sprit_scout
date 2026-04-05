import streamlit as st
import pandas as pd
import sqlite3
from PIL import Image
import rechtliches
import numpy as np

# --- CONFIG ---
HOELTER_BLAU = "#1e5aa0"
st.set_page_config(page_title="Wuppertal Tankt | Hölter Digital", page_icon=":material/directions_car:", layout="wide")

# CSS (Hölter Style)

st.markdown(f"""
        <style>
        /* 1. Die Kacheln */
        .stMetric {{
            background-color: var(--secondary-background-color);
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid {HOELTER_BLAU};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        /* 2. Dropdown-Menü & PLZ-Feld (Fokus-Rahmen) */
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="input"] > div:focus-within {{
            border-color: {HOELTER_BLAU} !important;
            box-shadow: 0 0 0 1px {HOELTER_BLAU} !important;
        }}

        /* 3. Schieberegler (Slider) */
        div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div > div:first-child {{
            background-color: {HOELTER_BLAU} !important;
        }}
        div[data-testid="stSlider"] div[role="slider"] {{
            background-color: {HOELTER_BLAU} !important;
            border-color: {HOELTER_BLAU} !important;
        }}
        div[data-testid="stSlider"] div[role="slider"] > div {{
            color: {HOELTER_BLAU} !important;
        }}

        /* 4. Die Sorte-Auswahl (Der letzte Endgegner) */
        /* Wir zielen auf alle möglichen Pill/Button/Radio Bezeichnungen von Streamlit */
        button[data-testid="stBaseButton-pillsActive"],
        button[data-testid="stBaseButton-pillsActive"]:hover,
        button[data-testid="stBaseButton-pillsActive"]:focus,
        div[data-testid="stPills"] button[aria-pressed="true"],
        label[data-baseweb="radio"] div[aria-checked="true"] {{
            border-color: {HOELTER_BLAU} !important;
            background-color: rgba(30, 90, 160, 0.1) !important;
            color: {HOELTER_BLAU} !important;
        }}
        
        /* Erzwingt die blaue Schrift auch für den Text IM Button */
        button[data-testid="stBaseButton-pillsActive"] *,
        button[data-testid="stBaseButton-pillsActive"]:hover *,
        div[data-testid="stPills"] button[aria-pressed="true"] *,
        label[data-baseweb="radio"] div[aria-checked="true"] * {{
            color: {HOELTER_BLAU} !important;
        }}
        </style>
        """, unsafe_allow_html=True)

def berechne_distanz(lat1, lon1, lat2, lon2):
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2): return 999.0
    r = 6371 
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    return 2 * r * np.arctan2(np.sqrt(a), np.sqrt(1-a))

def lade_daten():
    conn = sqlite3.connect('spritpreise.db')
    df = pd.read_sql_query("SELECT * FROM preise", conn)
    conn.close()
    if not df.empty:
        df['zeitstempel'] = pd.to_datetime(df['zeitstempel']).dt.tz_localize('UTC').dt.tz_convert('Europe/Berlin')
    return df

# --- HEADER ---
c_logo, c_title = st.columns([1, 10])
with c_logo:
    try: st.image(Image.open("logo.png"), width=70)
    except: st.write(":material/directions_car:")
with c_title: st.title("Wuppertal tankt")

menue = st.selectbox("Navigation", ["✦ Übersicht", "◎ Umkreissuche", "§ Impressum", "⛨ Datenschutz"])
st.divider()

df = lade_daten()

if not df.empty:
    aktuell = df.sort_values('zeitstempel', ascending=False).drop_duplicates('tankstelle').copy()

    if menue == "✦ Übersicht":
        st.subheader("Die absoluten Bestpreise")
        c1, c2, c3 = st.columns(3)
        for i, s in enumerate(['e5', 'e10', 'diesel']):
            m = aktuell.loc[aktuell[s].idxmin()]
            zeit_str = m['zeitstempel'].strftime('%H:%M')
            with [c1, c2, c3][i]:
                st.metric(f"Super {s.upper()}", f"{m[s]:.2f}€")
                # Hier nutzen wir das schlichte Material-Icon
                st.caption(f":material/location_on: {m['tankstelle']} \n\n:material/schedule: Stand: {zeit_str} Uhr")

    elif menue == "◎ Umkreissuche":
        st.subheader("Umkreissuche")
        
        # 1. Filtereinstellungen
        col_plz, col_rad = st.columns([2, 2])
        with col_plz:
            plz = st.text_input("Deine PLZ:", placeholder="z.B. 42281")
        with col_rad:
            radius_km = st.select_slider("Umkreis (km):", options=[2, 5, 10, 15, 30], value=10)
        
        sorte = st.pills("Sorte:", ["e5", "e10", "diesel"], default="e5")

        plz_map = {
            "42103": (51.255, 7.149), "42105": (51.264, 7.145), "42107": (51.272, 7.144),
            "42109": (51.285, 7.142), "42111": (51.298, 7.135), "42113": (51.276, 7.114),
            "42115": (51.258, 7.118), "42117": (51.245, 7.126), "42119": (51.242, 7.155),
            "42275": (51.273, 7.188), "42277": (51.286, 7.225), "42279": (51.299, 7.215),
            "42281": (51.288, 7.195), "42283": (51.271, 7.205), "42285": (51.261, 7.185),
            "42287": (51.245, 7.195), "42289": (51.238, 7.225), "42327": (51.235, 7.075),
            "42329": (51.231, 7.085), "42349": (51.205, 7.135), "42369": (51.228, 7.215),
            "42389": (51.268, 7.265), "42399": (51.215, 7.265)
        }
        
        if plz in plz_map:
            u_lat, u_lng = plz_map[plz]
            # Entfernung berechnen
            aktuell['distanz'] = aktuell.apply(lambda r: berechne_distanz(u_lat, u_lng, r['lat'], r['lng']), axis=1)
            
            # --- DER FILTER-TRICK ---
            # Nur Tankstellen im gewählten Radius behalten
            gefiltert = aktuell[aktuell['distanz'] <= radius_km].copy()
            
            # Jetzt nach PREIS sortieren (günstigste zuerst)
            gefiltert = gefiltert.sort_values(sorte)
            
            st.caption(f"✓ {len(gefiltert)} Tankstellen innerhalb von {radius_km} km gefunden. Günstigste zuerst.")
            
            for _, row in gefiltert.iterrows():
                zeit_str = row['zeitstempel'].strftime('%H:%M')
                
                with st.container():
                    c1, c2, c3 = st.columns([4, 1, 1])
                    with c1:
                        st.markdown(f"**{row['tankstelle']}**")
                        # Das Icon fügt sich nahtlos in den Text ein
                        st.caption(f"{row['distanz']:.1f} km entfernt • :material/schedule: {zeit_str} Uhr")
                    with c2:
                        st.metric("", f"{row[sorte]:.2f}€", label_visibility="collapsed")
                    with c3:
                        url = f"https://www.google.com/maps/dir/?api=1&destination={row['lat']},{row['lng']}"
                        st.link_button(":material/navigation: Route berechnen", url, use_container_width=True)
                    st.divider()
                    
        else:
            st.info("Bitte gib eine gültige Wuppertaler PLZ ein, um den Radius-Check zu nutzen.")

    elif menue == "§ Impressum": rechtliches.zeige_impressum()
    elif menue == "⛨ Datenschutz": rechtliches.zeige_datenschutz()