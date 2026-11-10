# Imports:

import logging
from pathlib import Path
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import QObject

from views.GUI.pages.page_reservas import PageReservas
from views.GUI.pages.page_dashboard import PageDashboard

#Paths:

FILE_UI_PATH = Path(__file__).resolve().parent / "ventanaMain.ui"

# Constants:

# Global Variables:

# Apuntamos al parlante específico de la capa de GUI / Vistas
logger = logging.getLogger("views.GUI.main_window")

# Class:

class MainWindow(QMainWindow):

    #Constructor:

    def __init__(
            self, 
            
    ):
        super().__init__()

        # Cargamos la interfaz gráfica dinámicamente con uic
        uic.loadUi(FILE_UI_PATH, self)
        logger.info("Ventana principal cargada correctamente desde el archivo UI.")
        
        # Inicializamos las conexiones de señales y slots
        self.init_ui_connections()

        # Instancio la pagina de reservas:
        self.page_reservas = PageReservas()

        # La agregamos al QStackedWidget de la ventana principal
        self.stackedWidget.addWidget(self.page_reservas)
        logger.info("Página de reservas añadida al gestor de páginas (stackedWidget).")

        print("Cantidad total de páginas en el stackedWidget:", self.stackedWidget.count())
        print("Widget activo actual:", self.stackedWidget.currentIndex())

        # Instanciamos la pagina del dasboard:
        self.page_dasboard = PageDashboard()

        print("Cantidad total de páginas en el stackedWidget:", self.stackedWidget.count())
        print("Widget activo actual:", self.stackedWidget.currentIndex())

        # La agregamos al QStackedWidget de la ventana principal:
        self.stackedWidget.addWidget(self.page_dasboard)
        logger.info("Página de dashboard añadida al gestor de páginas (stackedWidget).")

        # Ponemos la pagina de reservas como la default:
        self.stackedWidget.setCurrentWidget(self.page_reservas)
        logger.info("Página de reservas establecida como vista por defecto al iniciar.")

        # 2. Listemos TODOS los nombres de widgets que PyQt logró leer de ese archivo
        widgets_encontrados = [w.objectName() for w in self.findChildren(QObject) if w.objectName()]
        print("Widgets detectados por PyQt en el UI:", widgets_encontrados)
        logger.debug(f"Widgets detectados en UI: {len(widgets_encontrados)} componentes encontrados.")
        
    def init_ui_connections(self):
        # Le paso los botones para cambiar a la páginas correspondientes:
        self.BotonPaginaReserva.clicked.connect(self.cambiar_pagina_reservas)
        self.BotonPaginaDasboard.clicked.connect(self.cambiar_pagina_dasboard)
        logger.info("Conexiones de señales y slots de navegación inicializadas.")

    #Metodos de funcion: 
    def cambiar_pagina_reservas(self):
        self.stackedWidget.setCurrentWidget(self.page_reservas)
        print("Cambiando a la página de Reservas...")
        logger.info("Usuario navegó hacia la página de Reservas.")

    def cambiar_pagina_dasboard(self):
        self.stackedWidget.setCurrentWidget(self.page_dasboard)
        print("Cambiando a la página del Dashboard...")
        logger.info("Usuario navegó hacia la página del Dashboard.")