import time
import subprocess
import sys
from datetime import datetime

def run_collector():
    while True:
        now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        print(f"[{now}] Starte automatischen Datenabruf...")
        
        try:
            # Führt das collector-Skript aus, als würdest du es im Terminal tippen
            subprocess.run([sys.executable, "collector.py"], check=True)
            print("Abruf erfolgreich beendet. Schlafe für 60 Minuten...")
        except Exception as e:
            print(f"Fehler beim Abruf: {e}")

        # Warte 3600 Sekunden (1 Stunde)
        time.sleep(3600)

if __name__ == "__main__":
    run_collector()