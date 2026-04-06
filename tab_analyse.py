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
        return f"{preis:.2f} €".replace('.', ',')
        
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

    # Zeitstempel für Deutschland aufbereiten
    # NEU (Einfach die Zeit nehmen, die da steht)
    df['zeitstempel'] = pd.to_datetime(df['zeitstempel'])

    # 2. Auswahlmenü
    col1, col2 = st.columns(2)
    with col1:
        tankstellen_liste = sorted(df['tankstelle'].unique())
        gewaehlte_tanke = st.selectbox("Wähle deine Tankstelle", tankstellen_liste)
    with col2:
        sorte = st.selectbox("Welchen Sprit tankst du?", ["e5", "e10", "diesel"], index=0)

    # 3. Filterung
    df_tanke = df[df['tankstelle'] == gewaehlte_tanke].sort_values('zeitstempel')

    if df_tanke.empty:
        st.info("Für diese Tankstelle haben wir aktuell keine 24h-Daten.")
        return

    # 4. Die Mathe-Magie
    letzter_eintrag = df_tanke.iloc[-1]
    aktueller_preis = letzter_eintrag[sorte]
    aktueller_zeitstempel = letzter_eintrag['zeitstempel']
    
    tanke_schnitt = df_tanke[sorte].mean()
    wuppertal_schnitt = df[sorte].mean()
    differenz = aktueller_preis - wuppertal_schnitt

    # Zeitstempel formatieren
    heute = pd.Timestamp.now(tz='Europe/Berlin').date()
    if aktueller_zeitstempel.date() == heute:
        zeit_display = f"Heute, {aktueller_zeitstempel.strftime('%H:%M')} Uhr"
    else:
        zeit_display = f"{aktueller_zeitstempel.strftime('%d.%m., %H:%M')} Uhr"

    # --- DIE EMPFEHLUNGS-AMPEL ---
    st.write("---")
    st.subheader("✧ Soll ich jetzt tanken?")
    
    if differenz <= -0.015:
        st.success(f"🟢 **Gute Gelegenheit!** Mit {aktueller_preis:.2f} € tankst du hier aktuell spürbar günstiger als der stadtweite Durchschnitt.")
    elif differenz > 0.015:
        st.error(f"🔴 **Eventuell noch etwas warten.** Mit {aktueller_preis:.2f} € liegt der Preis momentan etwas über dem Wuppertaler Durchschnitt.")
    else:
        st.warning(f"🟡 **Fairer Preis.** Mit {aktueller_preis:.2f} € bewegt sich die Tankstelle absolut im normalen städtischen Mittelfeld.")

    # --- METRIKEN ---
    col_a, col_b, col_c = st.columns(3)
    delta_text = f"{differenz:+.2f} € zum Stadt-Ø".replace('.', ',')
    
    with col_a:
        st.metric("Aktueller Preis", format_tankpreis(aktueller_preis, exakte_preise), delta_text, delta_color="inverse")
        st.caption(f":material/schedule: Stand: {zeit_display}")
        
    with col_b:
        st.metric("Ø Wuppertal (24h)", format_tankpreis(wuppertal_schnitt, exakte_preise))
        st.caption("Stadtweiter Durchschnitt")
        
    with col_c:
        st.metric("Ø Diese Tankstelle (24h)", format_tankpreis(tanke_schnitt, exakte_preise))
        st.caption("Eigener Durchschnitt")

    # --- DER PLOTLY GRAPH (Hölter-Blue Style) ---
    st.write("---")
    st.subheader("⎍ Preisverlauf (Letzte 24h)")
    
    fig = px.line(
        df_tanke, 
        x='zeitstempel', 
        y=sorte, 
        markers=True,
        line_shape='hv',
        color_discrete_sequence=["#1e5aa0"] # Hölter Blau
    )
    
    # Styling-Anpassungen
    fig.update_traces(line_width=3, marker=dict(size=8))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis_title="Uhrzeit",
        yaxis_title="Preis in €",
        hovermode="x unified"
    )
    
    # Gitterlinien und Achsen-Zuschnitt
    fig.update_yaxes(gridcolor='rgba(128,128,128,0.2)')
    fig.update_xaxes(gridcolor='rgba(128,128,128,0.2)')
    
    ymin = df_tanke[sorte].min() - 0.02
    ymax = df_tanke[sorte].max() + 0.02
    fig.update_layout(yaxis_range=[ymin, ymax])

    st.plotly_chart(fig, width='stretch')