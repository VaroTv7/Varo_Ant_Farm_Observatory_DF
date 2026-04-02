import time
import os
import threading
from parser import parse_legends_file

LEGENDS_PATH = "/df-data/legends.xml"
CHECK_INTERVAL_SECONDS = 60

class WatchdogDaemon:
    def __init__(self):
        self.last_mtime = 0
        self.running = True
        self.thread = threading.Thread(target=self._watch, daemon=True)

    def start(self):
        print(f"[Watchdog] Iniciando monitorización de {LEGENDS_PATH} (cada {CHECK_INTERVAL_SECONDS}s)")
        # Carga inicial (arranque)
        self._check_file(force_parse=False)
        self.thread.start()

    def stop(self):
        self.running = False

    def _check_file(self, force_parse=False):
        if not os.path.exists(LEGENDS_PATH):
            return

        try:
            current_mtime = os.path.getmtime(LEGENDS_PATH)
            
            if current_mtime > self.last_mtime or force_parse:
                # Si es la primera vez que inicia, revisemos si la base de datos ya tiene datos
                # Para evitar re-parsear si no ha cambiado desde el último arranque.
                # Aquí lo simplificamos: si cambió el mtime, parseamos.
                if self.last_mtime != 0 or force_parse:
                    print(f"[Watchdog] Cambios detectados en {LEGENDS_PATH}. Disparando parser...")
                    parse_legends_file()
                
                self.last_mtime = current_mtime
        except Exception as e:
            print(f"[Watchdog] Error chequeando archivo: {e}")

    def _watch(self):
        while self.running:
            time.sleep(CHECK_INTERVAL_SECONDS)
            self._check_file()

# Instancia global
watchdog = WatchdogDaemon()
