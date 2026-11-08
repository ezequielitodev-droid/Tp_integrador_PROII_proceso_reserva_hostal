# Imports:

from pathlib import Path
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import QObject

from views.GUI.pages.page_reservas import PageReservas

#Paths:

FILE_UI_PATH = Path(__file__).resolve().parent / "ventanaMain.ui"

# Constants:

# Class:

class MainWindow(QMainWindow):

    #Constructor:

    def __init__(
            self, 
            
    ):
        super().__init__()

        # Cargamos la interfaz gráfica dinámicamente con uic
        uic.loadUi(FILE_UI_PATH, self)
        
        # Inicializamos las conexiones de señales y slots
        self.init_ui_connections()

        #Instancio la pagina de reservas:
        self.page_reservas = PageReservas()

        # La agregamos al QStackedWidget que tienes en tu ventana principal
        self.stackedWidget.addWidget(self.page_reservas)

        # 2. Listemos TODOS los nombres de widgets que PyQt logró leer de ese archivo
        widgets_encontrados = [w.objectName() for w in self.findChildren(QObject) if w.objectName()]
        print("Widgets detectados por PyQt en el UI:", widgets_encontrados)
        
    def init_ui_connections(self):

        #Le pasos los botones para cambiar a la paginas correspondientes:
        self.BotonPaginaReserva.clicked.connect(self.cambiar_pagina_reservas)
        self.BotonPaginaDasboard.clicked.connect(self.cambiar_pagina_dasboard)

    #Metodos de funcion: 
    def cambiar_pagina_reservas(self):

        self.stackedWidget.setCurrentWidget(self.page_reservas)
        print("Cambiando a la página de Reservas...")

    def cambiar_pagina_dasboard(self):

        self.stackedWidget.setCurrentIndex(1)
        print("Cambiando a la pagina del Dasboard...")