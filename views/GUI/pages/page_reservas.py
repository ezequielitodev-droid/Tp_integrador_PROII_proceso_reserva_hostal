#Imports:

from pathlib import Path
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QHBoxLayout, QLabel, QPushButton
from PyQt5 import uic
from PyQt5 import uic

from services.cliente_service import ClienteService
from services.huesped_service import HuespedService
from services.habitacion_service import HabitacionService
from services.reserva_service import ReservaService

#Constants:

#Paths:

FILE_UI_PATH = Path(__file__).resolve().parent / "pages.ui"

#Class:

class PageReservas(QWidget):

    #Constructor:

    def __init__(
            self, 
            servicio_cliente: ClienteService | None = None, 
            servicio_huesped: HuespedService | None = None, 
            servicio_habitacion: HabitacionService | None = None, 
            servicio_reserva: ReservaService | None = None
    ):

        super().__init__()

        uic.loadUi(FILE_UI_PATH, self)

        #Inyectamos las dependencias de los servicios:
        self.servicio_cliente = servicio_cliente or ClienteService()
        self.servicio_huesped = servicio_huesped or HuespedService()
        self.servicio_habitacion = servicio_habitacion or HabitacionService()
        self.servicio_reserva = servicio_reserva or ReservaService()

        # Inicializamos las conexiones de señales y slots
        self.init_ui_connections()
        self.cargar_reservas()

    #Metodo conector:
    def init_ui_connections(self):

        #self.btnModificar.clicked.connect(self.modificar_reserva_seleccionada)
        self.BotonEliminar.clicked.connect(self.eliminar_reserva_seleccionada)

    #Metodos de funcion:

    def cargar_reservas(self):
        # Limpiamos la lista por seguridad
        self.listWidget.clear()

        # Obtenemos los datos directamente desde tu servicio (que consulta la BD en la nube mediante el DAO)
        reservas = self.servicio_reserva.obtener_reservas()

        if not reservas:
            print("No se encontraron reservas o hubo un error en la consulta.")
            return

        for item_tupla in reservas:
            # Si algún elemento de la lista viniera como None, lo saltamos por seguridad
            if item_tupla is None:
                continue

            # Desempaquetamos la tupla: el objeto Reserva y el ID del cliente
            reserva_obj, id_cliente = item_tupla

            #Si tienen baja logica no tengo que hacer nada, porque estan eliminados:
            if reserva_obj.get_activo() == 1:

                # Como reserva_obj es un objeto de la clase Reserva, usamos notación de punto (.) 
                # para armar un texto descriptivo prolijo para la interfaz:
                texto_visible = (
                    f"Reserva #{reserva_obj.get_id_reserva()} | "
                    f"Ingreso: {reserva_obj.get_fecha_ingreso()} | "
                    f"Salida: {reserva_obj.get_fecha_salida()} | "
                    f"Total: ${reserva_obj.get_monto_total()}"
                )

                # Creamos el ítem del listado visual con ese texto
                item = QListWidgetItem(texto_visible)
                
                # Guardamos el ID real de la reserva de forma oculta en el ítem (usando el rol 32)
                item.setData(32, reserva_obj.get_id_reserva())
                
                # Añadimos el ítem al QListWidget
                self.listWidget.addItem(item)

    def modificar_reserva(self, reserva_id):
        print(f"Modificar reserva con ID: {reserva_id}")
        #Aquí abrirías tu ventana o lógica de modificación

    def eliminar_reserva_seleccionada(self):

        #Obtenemos el ítem seleccionado en la lista
        item_seleccionado = self.listWidget.currentItem()

        if not item_seleccionado:
            print("Por favor, selecciona una reserva de la lista para eliminar.")
            return

        # Recuperamos el ID oculto que guardamos con setData(32, ...)
        reserva_id = item_seleccionado.data(32)

        try:

            self.servicio_reserva.eliminar_reserva(reserva_id)

            #Borramos visualmente el ítem de la lista para reflejar el cambio al instante
            row = self.listWidget.row(item_seleccionado)
            self.listWidget.takeItem(row)
            print("Reserva dada de baja y removida de la interfaz con éxito.")

        except Exception as e:
            print(f"Error al intentar dar de baja la reserva: {e}")

        