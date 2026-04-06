import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

def format_tankpreis(preis, exakte_preise=True):
    """
    Formatiert den Preis entweder als 1,75⁹ € (exakt) 
    oder als 1,76 € (gerundet, auf 2 Nachkommastellen).
    """
    if not exakte_preise:
        # Wenn der User gerundete Preise will (2 Nachkommastellen)
        return f"{preis:.2f} €".replace('.', ',')
        
    # Wenn der User exakte Preise will (3 Nachkommastellen mit Hochzahl)
    p_str = f"{preis:.3f}".replace('.', ',')
    hauptteil = p_str[:-1]
    letzte_ziffer = p_str[-1]
    
    hochzahlen = {'0':'⁰', '1':'¹', '2':'²', '3':'³', '4':'⁴', '5':'⁵', '6':'⁶', '7':'⁷', '8':'⁸', '9':'⁹'}
    hoch_ziffer = hochzahlen.get(letzte_ziffer, letzte_ziffer)
    
    return f"{hauptteil}{hoch_ziffer} €"

def zeige_analyse_tab(db_pfad, exakte_preise):
    st.header("◱ Tank-Analyse & Empfehlung")
    st.write("Wann ist der beste Zeitpunkt zum Tanken? Finde es hier heraus.")

    # 1. Daten der letzten 24 Stunden laden
    conn = sqlite3.connect(db_pfad)
    # Wir holen nur die Daten von gestern bis jetzt
    query = """
        SELECT zeitstempel, tankstelle, e5, e10, diesel 
        FROM preise 
        WHERE zeitstempel >= datetime('now', '-1 day')
    """
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        st.warning("Noch nicht genug Daten für eine Analyse gesammelt. Bitte warte auf den Collector!")
        return

    # Zeitstempel reparieren (damit Pandas versteht, dass es sich um echte Uhrzeiten handelt)
    # Zeitstempel von UTC in die deutsche Zeit (inkl. Sommerzeit) umwandeln.
    df['zeitstempel'] = pd.to_datetime(df['zeitstempel'], utc=True).dt.tz_convert('Europe/Berlin').dt.tz_localize(None)

    # 2. Auswahlmenü für den User
    col1, col2 = st.columns(2)
    with col1:
        tankstellen_liste = df['tankstelle'].unique()
        gewaehlte_tanke = st.selectbox("Wähle deine Tankstelle", sorted(tankstellen_liste))
    with col2:
        sorte = st.selectbox("Welchen Sprit tankst du?", ["e5", "e10", "diesel"], index=0)

    # 3. Daten nur für diese EINE Tankstelle filtern
    df_tanke = df[df['tankstelle'] == gewaehlte_tanke].sort_values('zeitstempel')

    if df_tanke.empty:
        st.info("Für diese Tankstelle haben wir aktuell keine 24h-Daten.")
        return

    # 4. Die Mathe-Magie (Wuppertal-Schnitt & Aktueller Preis)
    aktueller_preis = df_tanke.iloc[-1][sorte] # Der neueste Preis der gewählten Tankstelle
    tanke_schnitt = df_tanke[sorte].mean()     # Der 24h-Schnitt NUR dieser Tankstelle
    wuppertal_schnitt = df[sorte].mean()       # Der 24h-Schnitt ALLER Tankstellen in Wuppertal
    
    # Wir berechnen die Differenz zum WUPPERTAL-Schnitt
    differenz = aktueller_preis - wuppertal_schnitt

    # --- DIE EMPFEHLUNGS-AMPEL ---
    st.write("---")
    st.subheader("✧ Soll ich jetzt tanken?")
    
    if differenz <= -0.015: # Mehr als 1,5 Cent GÜNSTIGER als der Stadt-Schnitt
        st.success(f"🟢 **Gute Gelegenheit!** Mit {aktueller_preis:.2f} € tankst du hier aktuell spürbar günstiger als der stadtweite Durchschnitt.")
    elif differenz > 0.015:  # Mehr als 1,5 Cent TEURER als der Stadt-Schnitt
        st.error(f"🔴 **Eventuell noch etwas warten.** Mit {aktueller_preis:.2f} € liegt der Preis momentan etwas über dem Wuppertaler Durchschnitt.")
    else:                   # Alles dazwischen (+/- 1,5 Cent)
        st.warning(f"🟡 **Fairer Preis.** Mit {aktueller_preis:.2f} € bewegt sich die Tankstelle absolut im normalen städtischen Mittelfeld.")

    # Schicke Metriken in 3 Spalten (Aktueller Preis | Stadt-Schnitt | Tanken-Schnitt)
    # Schicke Metriken in 3 Spalten
    col_a, col_b, col_c = st.columns(3)
    delta_text = f"{differenz:+.2f} € zum Stadt-Ø".replace('.', ',')
    
    col_a.metric("Aktueller Preis", format_tankpreis(aktueller_preis, exakte_preise), delta_text, delta_color="inverse")
    col_b.metric("Ø Wuppertal (24h)", format_tankpreis(wuppertal_schnitt, exakte_preise))
    col_c.metric("Ø Diese Tankstelle (24h)", format_tankpreis(tanke_schnitt, exakte_preise))

    # --- DER PLOTLY GRAPH ---
    st.write("---")
    st.subheader("⎍ Preisverlauf (Letzte 24h)")
    
    # Plotly macht automatisch wunderschöne interaktive Charts
    fig = px.line(
        df_tanke, 
        x='zeitstempel', 
        y=sorte, 
        markers=True,
        line_shape='hv' 
    )
    
    # Die Y-Achse zuschneiden
    ymin = df_tanke[sorte].min() - 0.05
    ymax = df_tanke[sorte].max() + 0.05
    fig.update_layout(yaxis_range=[ymin, ymax], xaxis_title="Uhrzeit", yaxis_title="Preis in €")

    st.plotly_chart(fig, width='stretch')