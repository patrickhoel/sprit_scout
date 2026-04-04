import streamlit as st

def zeige_impressum():
    st.title("Impressum")
    st.markdown("""
    **Patrick Hölter**<br>
    Osteroder Str. 21<br>
    42277 Wuppertal  

    **Kontakt** Telefon: +491746890706  
    E-Mail: patrick@hoelter-digital.de  

    Quelle: [https://www.e-recht24.de](https://www.e-recht24.de)
    """, unsafe_allow_html=True) # Wichtig für das <br>

def zeige_datenschutz():
    st.title("Datenschutzerklärung")
    st.markdown("""
    ### 1. Datenschutz auf einen Blick
    **Allgemeine Hinweise** Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen Daten passiert, wenn Sie diese Website besuchen. Personenbezogene Daten sind alle Daten, mit denen Sie persönlich identifiziert werden können. 

    **Wer ist verantwortlich für die Datenerfassung auf dieser Website?** Die Datenverarbeitung auf dieser Website erfolgt durch den Websitebetreiber. Dessen Kontaktdaten können Sie dem Abschnitt „Hinweis zur Verantwortlichen Stelle“ in dieser Datenschutzerklärung entnehmen.

    ### 2. Hosting
    **Hetzner** Wir hosten die Inhalte unserer Website bei folgendem Anbieter: Anbieter ist die Hetzner Online GmbH, Industriestr. 25, 91710 Gunzenhausen (nachfolgend Hetzner). Details entnehmen Sie der Datenschutzerklärung von Hetzner: [https://www.hetzner.com/de/legal/privacy-policy/](https://www.hetzner.com/de/legal/privacy-policy/). Die Verwendung von Hetzner erfolgt auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO.

    ### 3. Allgemeine Hinweise und Pflichtinformationen
    **Datenschutz** Die Betreiber dieser Seiten nehmen den Schutz Ihrer persönlichen Daten sehr ernst. Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend den gesetzlichen Datenschutzvorschriften sowie dieser Datenschutzerklärung.

    **Hinweis zur verantwortlichen Stelle** Die verantwortliche Stelle für die Datenverarbeitung auf dieser Website ist:  
    Patrick Hölter  
    Osteroder Str. 21  
    42277 Wuppertal  

    Telefon: 01746890706  
    E-Mail: patrick@hoelter-digital.de  

    ### 4. Datenerfassung auf dieser Website
    **Server-Log-Dateien** Der Provider der Seiten erhebt und speichert automatisch Informationen in so genannten Server-Log-Dateien, die Ihr Browser automatisch an uns übermittelt. Dies sind:
    * Browsertyp und Browserversion
    * verwendetes Betriebssystem
    * Referrer URL
    * Hostname des zugreifenden Rechners
    * Uhrzeit der Serveranfrage
    * IP-Adresse

    Eine Zusammenführung dieser Daten mit anderen Datenquellen wird nicht vorgenommen. Die Erfassung dieser Daten erfolgt auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO.

    ### 5. Plugins und Tools
    **Google Maps** Diese Seite nutzt den Kartendienst Google Maps. Anbieter ist die Google Ireland Limited („Google“), Gordon House, Barrow Street, Dublin 4, Irland. Mit Hilfe dieses Dienstes können wir Kartenmaterial auf unserer Website einbinden. Zur Nutzung der Funktionen von Google Maps ist es notwendig, Ihre IP-Adresse zu speichern. Diese Informationen werden in der Regel an einen Server von Google in den USA übertragen und dort gespeichert.

    Quelle: [https://www.e-recht24.de](https://www.e-recht24.de)
    """)