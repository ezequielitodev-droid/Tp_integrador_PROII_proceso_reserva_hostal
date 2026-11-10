# Imports:

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Determinamos la ruta base dependiendo de si estamos compilados o en desarrollo
if hasattr(sys, 'frozen'):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

# Cargamos el .env explícitamente desde la ruta base del ejecutable o script
ruta_env = BASE_DIR / ".env"
load_dotenv(dotenv_path=ruta_env)

# Importamos tu módulo de configuración de logs
from loggers.logger_config import configurar_logging

def asegurar_directorios_trabajo():
    """Asegura que existan las carpetas de logs y backups locales junto al ejecutable o script."""
    (BASE_DIR / "logs").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "backups" / "storage").mkdir(parents=True, exist_ok=True)

def main():
    
    # 0. Aseguramos la existencia de directorios críticos de escritura antes de activar los logs
    asegurar_directorios_trabajo()

    # 1. Activamos los parlantes y archivos de log antes de levantar nada
    configurar_logging()

    interfaz = os.getenv("APP_INTERFACE", "gui").lower()

    if interfaz == "gui":

        # Importamos localmente:
        from PyQt5.QtWidgets import QApplication
        from views.GUI.main_window import MainWindow
        
        app = QApplication(sys.argv)
        ventana = MainWindow()
        ventana.show()
        sys.exit(app.exec_())

    elif interfaz == "web":
        # Aqui iria una futura vinculacion con WEB...
        print("Módulo WEB en desarrollo...")

    elif interfaz == "cli":
        # Aqui iria una futura vinculacion CLI...
        print("Lanzando interfaz de comandos...")
        
    else:
        print(f"Error: Interfaz '{interfaz}' no reconocida.")
        sys.exit(1)

if __name__ == "__main__":
    main()