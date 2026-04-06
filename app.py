import streamlit as st
import pandas as pd
import sqlite3
from PIL import Image
import rechtliches
import numpy as np
from datetime import timedelta
from tab_analyse import zeige_analyse_tab

# --- CONFIG ---
HOELTER_BLAU = "#1e5aa0"
st.set_page_config(page_title="Wuppertal Tankt | Hölter Digital", page_icon="logo.png", layout="wide")

# --- INITIALISIERUNG & POP-UP FENSTER ---
if "preis_modus" not in st.session_state:
    st.session_state.preis_modus = None  # Wir wissen noch nicht, was der User will

# --- DAS POP-UP FENSTER ---
@st.dialog("Wuppertal tankt")
def zeige_willkommens_dialog():
    # DIESE ZEILE HAT GEFEHLT: Hier werden die Spalten erschaffen!
    col_logo, col_text = st.columns([1, 4])
    
    with col_logo:
        try: 
            logo_img = Image.open("logo.png")
            st.image(logo_img, width="stretch")
        except: 
            st.write(":material/local_gas_station:")
            
    with col_text:
        # Etwas größere, fette Überschrift
        st.markdown("#### Willkommen!")
        st.write("Wie möchtest du die Spritpreise in der App angezeigt bekommen?")
    
    st.write("") # Ein bisschen Luft für die Optik
    
    # Dropdown statt Radio-Buttons
    wahl = st.selectbox(
        "Deine bevorzugte Anzeige:",
        [
            "Klassisch (3-stellig, wie an der Zapfsäule)", 
            "Übersichtlich (2-stellig, aufgerundet)"
        ],
        index=0
    )
    
    st.write("") # Ein bisschen Luft vor dem Button
    
    # Der Button wird als "Primary" markiert und über die ganze Breite gezogen
    if st.button("Speichern & Starten", type="primary", width='stretch'):
        st.session_state.preis_modus = wahl
        st.rerun()

# Trigger: Wenn noch keine Wahl getroffen wurde, Pop-up öffnen
if st.session_state.preis_modus is None:
    zeige_willkommens_dialog()

# --- CSS (Hölter Style) ---
st.markdown(f"""
        <style>
        /* 1. Die Kacheln */
        .stMetric, .pro-metric {{
            background-color: var(--secondary-background-color);
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid {HOELTER_BLAU};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        /* Sorgt dafür, dass der Markdown-Text keinen extra Abstand nach unten hat */
        .pro-metric p {{ margin-bottom: 0; line-height: 1.2; }}

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

        /* 4. Die Sorte-Auswahl */
        button[data-testid="stBaseButton-pillsActive"],
        button[data-testid="stBaseButton-pillsActive"]:hover,
        button[data-testid="stBaseButton-pillsActive"]:focus,
        div[data-testid="stPills"] button[aria-pressed="true"],
        label[data-baseweb="radio"] div[aria-checked="true"] {{
            border-color: {HOELTER_BLAU} !important;
            background-color: rgba(30, 90, 160, 0.1) !important;
            color: {HOELTER_BLAU} !important;
        }}
        
        button[data-testid="stBaseButton-pillsActive"] *,
        button[data-testid="stBaseButton-pillsActive"]:hover *,
        div[data-testid="stPills"] button[aria-pressed="true"] *,
        label[data-baseweb="radio"] div[aria-checked="true"] * {{
            color: {HOELTER_BLAU} !important;
        }}
        /* 5. Primary Button umfärben (für das Pop-up) */
        button[kind="primary"] {{
            background-color: {HOELTER_BLAU} !important;
            border-color: {HOELTER_BLAU} !important;
            color: white !important;
        }}
        
        button[kind="primary"]:hover {{
            background-color: #154073 !important; /* Ein etwas dunkleres Blau für den Hover-Effekt */
            border-color: #154073 !important;
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

@st.cache_data(ttl=300) # Behält die Daten für 300 Sekunden (5 Min) im Cache
def lade_daten():
    conn = sqlite3.connect('spritpreise.db')
    df = pd.read_sql_query("SELECT * FROM preise WHERE zeitstempel >= datetime('now', '-7 days')", conn)
    conn.close()
    if not df.empty:
        df['zeitstempel'] = pd.to_datetime(df['zeitstempel']).dt.tz_localize('UTC').dt.tz_convert('Europe/Berlin')
    return df

# --- HEADER ---
c_logo, c_title = st.columns([1, 10])
with c_logo:
    try: 
        logo_img = Image.open("logo.png")
        st.image(logo_img, width="stretch")
    except: 
        st.write(":material/directions_car:")
with c_title: 
    st.title("Wuppertal tankt")

# --- NAVIGATION ---
menue = st.selectbox("Navigation", ["✦ Übersicht", "◎ Umkreissuche", "⇄ Preis-Vergleich", "🚟 Wuppertal Tankt 2.0"])
st.divider()

df = lade_daten()

if not df.empty:
    aktuell = df.sort_values('zeitstempel', ascending=False).drop_duplicates('tankstelle').copy()

    # --- ÜBERSICHT ---
    if menue == "✦ Übersicht":
        st.subheader("Die absoluten Bestpreise")
        
        c1, c2, c3 = st.columns(3)
        for i, s in enumerate(['e5', 'e10', 'diesel']):
            m = aktuell.loc[aktuell[s].idxmin()]
            
            ts = m['zeitstempel']
            heute = pd.Timestamp.now(tz='Europe/Berlin').date()
            gestern = heute - pd.Timedelta(days=1)
            
            if ts.date() == heute:
                zeit_str = f"Heute, {ts.strftime('%H:%M')}"
            elif ts.date() == gestern:
                zeit_str = f"Gestern, {ts.strftime('%H:%M')}"
            else:
                zeit_str = f"{ts.strftime('%d.%m.')}, {ts.strftime('%H:%M')}"
                
            with [c1, c2, c3][i]:
                # Logik-Anpassung an die neuen Bezeichnungen
                if st.session_state.preis_modus == "Klassisch (3-stellig, wie an der Zapfsäule)":
                    preis_str = f"{m[s]:.3f}"
                    st.markdown(f"""
                    <div class="pro-metric">
                        <div style="font-size: 0.9rem; opacity: 0.7; margin-bottom: 4px;">Super {s.upper()}</div>
                        <div style="font-size: 1.8rem; font-weight: bold;">{preis_str[:-1]}<sup style="font-size: 0.6em;">{preis_str[-1]}</sup> €</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.metric(f"Super {s.upper()}", f"{m[s]:.2f}€")
                
                st.caption(f":material/location_on: {m['tankstelle']} \n\n:material/schedule: Stand: {zeit_str} Uhr")
                
    # --- UMKREISSUCHE ---
    elif menue == "◎ Umkreissuche":
        st.subheader("Umkreissuche & Stationen")
        
        stationen_namen = sorted(aktuell['tankstelle'].unique().tolist())
        gewaehlte_station = st.selectbox(":material/search: Tankstelle suchen", ["Alle anzeigen"] + stationen_namen)

        col_plz, col_rad = st.columns([2, 2])
        with col_plz:
            plz_input = st.text_input("Deine PLZ (für Umkreis):", placeholder="z.B. 42281")
        with col_rad:
            radius_km = st.select_slider("Umkreis (km):", options=[2, 5, 10, 15, 30], value=10)
        
        sorte = st.pills("Sorte:", ["e5", "e10", "diesel"], default="e5")

        gefiltert = aktuell.copy()

        if gewaehlte_station != "Alle anzeigen":
            gefiltert = gefiltert[gefiltert['tankstelle'] == gewaehlte_station]

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

        if plz_input in plz_map:
            u_lat, u_lng = plz_map[plz_input]
            gefiltert['distanz'] = gefiltert.apply(lambda r: berechne_distanz(u_lat, u_lng, r['lat'], r['lng']), axis=1)
            gefiltert = gefiltert[gefiltert['distanz'] <= radius_km]
        elif plz_input != "":
            st.warning("PLZ nicht im System. Zeige alle Stationen.")

        gefiltert = gefiltert.sort_values(sorte)
        
        if gewaehlte_station == "Alle anzeigen":
            st.caption(f"✓ {len(gefiltert)} Tankstellen gefunden. **(Sortiert: Günstigste zuerst)**")
        else:
            st.caption(f"✓ Ergebnisse für {gewaehlte_station}")

        for _, row in gefiltert.iterrows():
            ts = row['zeitstempel']
            heute = pd.Timestamp.now(tz='Europe/Berlin').date()
            if ts.date() == heute:
                zeit_str = f"Heute, {ts.strftime('%H:%M')}"
            else:
                zeit_str = f"{ts.strftime('%d.%m.')}, {ts.strftime('%H:%M')}"
            distanz_text = f"{row['distanz']:.1f} km entfernt • " if 'distanz' in row else ""
            
            with st.container():
                c1, c2, c3 = st.columns([4, 1, 1])
                with c1:
                    st.markdown(f"**{row['tankstelle']}**")
                    st.caption(f"{distanz_text}:material/schedule: {zeit_str} Uhr")
                with c2:
                    # Logik-Anpassung an die neuen Bezeichnungen
                    if st.session_state.preis_modus == "Klassisch (3-stellig, wie an der Zapfsäule)":
                        preis_str = f"{row[sorte]:.3f}"
                        st.markdown(f"""
                        <div class="pro-metric">
                            <div style="font-size: 1.5rem; font-weight: bold; text-align: center;">
                                {preis_str[:-1]}<sup style="font-size: 0.6em;">{preis_str[-1]}</sup> €
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.metric("Preis", f"{row[sorte]:.2f}€", label_visibility="collapsed")
                with c3:
                    url = f"https://www.google.com/maps/search/?api=1&query={row['lat']},{row['lng']}"
                    st.link_button(":material/navigation: Route", url, width="stretch")
                st.divider()

    # --- PREIS-VERGLEICH ---
    elif menue == "⇄ Preis-Vergleich":
        st.subheader("Preis-Vergleich")
        
        min_date = df['zeitstempel'].min().date()
        max_date = df['zeitstempel'].max().date()
        
        default_date = max_date - pd.Timedelta(days=14)
        if default_date < min_date:
            default_date = min_date
        
        col_date, col_time, col_sorte = st.columns(3)
        with col_date:
            ziel_datum = st.date_input("Vergleichsdatum", value=default_date, min_value=min_date, max_value=max_date)
        with col_time:
            ziel_uhrzeit = st.time_input("Uhrzeit", value=pd.Timestamp.now().replace(minute=0, second=0, microsecond=0).time(), step=timedelta(minutes=30))
        with col_sorte:
            sorte = st.selectbox("Kraftstoff", ["e5", "e10", "diesel"], index=0)
            
        stationen_namen = sorted(aktuell['tankstelle'].unique().tolist())
        such_station = st.selectbox("⌕ Bestimmte Tankstelle (optional)", ["Alle vergleichen"] + stationen_namen)
        
        st.divider()
        
        target_dt = pd.to_datetime(f"{ziel_datum} {ziel_uhrzeit}").tz_localize('Europe/Berlin')
        historie_df = df[df['zeitstempel'] <= target_dt]
        
        if historie_df.empty:
            st.warning(f"Für diesen Zeitpunkt habe ich noch keine Daten.")
        else:
            historie_aktuell = historie_df.sort_values('zeitstempel').drop_duplicates('tankstelle', keep='last')
            
            vergleichs_df = pd.merge(
                aktuell[['tankstelle', sorte, 'zeitstempel']], 
                historie_aktuell[['tankstelle', sorte, 'zeitstempel']], 
                on='tankstelle', 
                suffixes=('_jetzt', '_damals')
            )
            
            if such_station != "Alle vergleichen":
                vergleichs_df = vergleichs_df[vergleichs_df['tankstelle'] == such_station]
                
            if vergleichs_df.empty:
                st.info("Keine passenden Vergleichsdaten für diese Auswahl gefunden.")
            else:
                st.caption(f"Vergleich: HEUTE vs. {ziel_datum.strftime('%d.%m.%Y')} ({ziel_uhrzeit.strftime('%H:%M')} Uhr)")
                
                for _, row in vergleichs_df.iterrows():
                    preis_jetzt = row[f'{sorte}_jetzt']
                    preis_damals = row[f'{sorte}_damals']
                    differenz = preis_jetzt - preis_damals
                    
                    with st.container():
                        c1, c2, c3 = st.columns([3, 1, 1])
                        with c1:
                            st.markdown(f"**{row['tankstelle']}**")
                            st.caption(f"Aktueller Stand: {row['zeitstempel_jetzt'].strftime('%H:%M')} Uhr")
                        with c2:
                            if st.session_state.preis_modus == "Klassisch (3-stellig, wie an der Zapfsäule)":
                                preis_jetzt_str = f"{preis_jetzt:.3f}"
                                
                                # Unsere eigene Delta-Pfeil Logik (Teurer = Rot, Billiger = Grün)
                                if differenz > 0:
                                    d_color = "#ff2b2b" # Streamlit Rot
                                    d_text = f"▲ +{differenz:.3f} €"
                                elif differenz < 0:
                                    d_color = "#09ab3b" # Streamlit Grün
                                    d_text = f"▼ -{abs(differenz):.3f} €"
                                else:
                                    d_color = "gray"
                                    d_text = "► ±0.000 €"
                                
                                # Unser HTML für die 9 oben PLUS dem farbigen Delta-Pfeil
                                st.markdown(f"""
                                <div class="pro-metric">
                                    <div style="font-size: 0.9rem; opacity: 0.7; margin-bottom: 4px;">Aktueller Preis</div>
                                    <div style="font-size: 1.8rem; font-weight: bold; line-height: 1;">
                                        {preis_jetzt_str[:-1]}<sup style="font-size: 0.6em;">{preis_jetzt_str[-1]}</sup> €
                                    </div>
                                    <div style="color: {d_color}; font-size: 0.9rem; font-weight: bold; margin-top: 8px;">
                                        {d_text}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.metric("Aktueller Preis", f"{preis_jetzt:.2f} €", delta=f"{differenz:+.2f} €", delta_color="inverse")
                                
                        with c3:
                            if st.session_state.preis_modus == "Klassisch (3-stellig, wie an der Zapfsäule)":
                                preis_damals_str = f"{preis_damals:.3f}"
                                st.markdown(f"""
                                <div class="pro-metric" style="height: 100%;">
                                    <div style="font-size: 0.9rem; opacity: 0.7; margin-bottom: 4px;">Preis damals</div>
                                    <div style="font-size: 1.8rem; font-weight: bold; line-height: 1;">
                                        {preis_damals_str[:-1]}<sup style="font-size: 0.6em;">{preis_damals_str[-1]}</sup> €
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.metric("Preis damals", f"{preis_damals:.2f} €")
    
    elif menue == "🚟 Wuppertal Tankt 2.0":
        # 1. Wir prüfen direkt, ob "Klassisch" gewählt ist und speichern True oder False
        exakte_preise = (st.session_state.preis_modus == "Klassisch (3-stellig, wie an der Zapfsäule)")
        
        # 2. Wir geben diese Info direkt in der Klammer mit an die Analyse-Seite!
        zeige_analyse_tab('spritpreise.db', exakte_preise)

# --- RECHTLICHES (POP-UPS) ---
@st.dialog("Impressum")
def open_impressum():
    rechtliches.zeige_impressum()

@st.dialog("Datenschutz")
def open_datenschutz():
    rechtliches.zeige_datenschutz()

# --- RECHTLICHES (POP-UPS) ---
@st.dialog("Impressum")
def open_impressum():
    rechtliches.zeige_impressum()

@st.dialog("Datenschutz")
def open_datenschutz():
    rechtliches.zeige_datenschutz()

# --- FOOTER BEREICH ---
st.markdown("---") 

# CSS-Trick: "Tertiary" Buttons exakt wie die Text-Links auf hoelter-digital.de aussehen lassen
st.markdown(f"""
<style>
button[kind="tertiary"] {{
    background-color: transparent !important;
    padding: 0 !important;
}}
button[kind="tertiary"] * {{
    color: #8b949e !important;
    font-size: 0.9rem !important;
}}
button[kind="tertiary"]:hover * {{
    color: {HOELTER_BLAU} !important;
    text-decoration: underline !important;
}}
</style>
""", unsafe_allow_html=True)

# Die Links schön nah beieinander mittig zentrieren
col_leer1, col_imp, col_dat, col_leer2 = st.columns([3, 1, 1, 3])
with col_imp:
    if st.button("Impressum", type="tertiary", width='stretch'):
        open_impressum()
with col_dat:
    if st.button("Datenschutz", type="tertiary", width='stretch'):
        open_datenschutz()

# Dein bestehendes Hölter Digital Branding inkl. Copyright-Hinweis
footer_html = """
<div style="text-align: center; color: #8b949e; font-size: 0.8rem; margin-top: -5px;">
    <p>© 2026 Hölter Digital</p>
    <p style="margin-top: 10px;">Datenquelle: <b><a href="https://www.tankerkoenig.de" target="_blank" style="color: #8b949e;">Tankerkönig.de</a></b> 
    | Rohdaten der MTS-K (Bundeskartellamt)</p>
</div>
<div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 10px; margin-bottom: 20px;">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="20" height="20">
      <rect width="512" height="512" rx="120" fill="#0d1117" />
      <g fill="none" stroke="#3b82f6" stroke-width="45" stroke-linecap="round" stroke-linejoin="round">
        <path d="M 220 130 L 100 256 L 220 382" />
        <path d="M 292 130 L 412 256 L 292 382" />
        <path d="M 140 256 L 372 256" />
      </g>
    </svg>
    <a href="https://hoelter-digital.de" target="_blank" style="color: #8b949e; text-decoration: none;">
        powered by <b>Hölter Digital</b>
    </a>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)