#Imports:

import sys
import os
from dotenv import load_dotenv

#Globals Call:
load_dotenv()

def main():
    
    interfaz = os.getenv("APP_INTERFACE", "gui").lower()

    if interfaz == "gui":

        #Importamos localmente:
        from PyQt5.QtWidgets import QApplication
        from views.GUI.main_window import MainWindow
        
        app = QApplication(sys.argv)
        ventana = MainWindow()
        ventana.show()
        sys.exit(app.exec_())

    elif interfaz == "web":
        #Aqui iria una futura vinculacion con WEB...
        print("Módulo WEB en desarrollo...")

    elif interfaz == "cli":
        #Aqui iria una futura vinculacion CLI...
        print("Lanzando interfaz de comandos...")
        
    else:
        print(f"Error: Interfaz '{interfaz}' no reconocida.")
        sys.exit(1)

if __name__ == "__main__":
    main()