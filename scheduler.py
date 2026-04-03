import time
import subprocess
import sys
from datetime import datetime, timedelta

def run_collector():
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    print(f"[{now}] Starte automatischen Datenabruf...")
    try:
        subprocess.run([sys.executable, "collector.py"], check=True)
        print("Abruf erfolgreich.")
    except Exception as e:
        print(f"Fehler beim Abruf: {e}")

def start_scheduler():
    print("Präzisions-Scheduler gestartet. Warte auf die nächste volle/halbe Stunde...")
    
    while True:
        now = datetime.now()
        
        # 1. Sofort abrufen, wenn wir genau auf einer 00 oder 30 Minute sind (oder ganz knapp davor/danach)
        run_collector()
        
        # 2. Berechnen, wann der nächste Termin ist (00 oder 30)
        if now.minute < 30:
            # Nächster Termin ist Minute 30 der aktuellen Stunde
            nächster_termin = now.replace(minute=30, second=0, microsecond=0)
        else:
            # Nächster Termin ist Minute 00 der NÄCHSTEN Stunde
            nächster_termin = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        
        # 3. Differenz berechnen und schlafen
        wartezeit = (nächster_termin - datetime.now()).total_seconds()
        
        # Falls die Wartezeit negativ ist (weil der Abruf 2 Sek gedauert hat), sofort weiter
        if wartezeit > 0:
            print(f"Nächster Abruf um {nächster_termin.strftime('%H:%M:%S')}. Warte {int(wartezeit)} Sekunden...")
            time.sleep(wartezeit)

if __name__ == "__main__":
    start_scheduler()