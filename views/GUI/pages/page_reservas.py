# Imports:

import logging
from pathlib import Path
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QDialog, QMessageBox
from PyQt5 import uic

from views.GUI.dialogs.dialog_crear_reserva import DialogCrearReserva

from services.cliente_service import ClienteService
from services.huesped_service import HuespedService
from services.habitacion_service import HabitacionService
from services.reserva_service import ReservaService

#Constants:

#Paths:

FILE_UI_PATH = Path(__file__).resolve().parent / "page_reservas.ui"

# Global Variables:

# Apuntamos al parlante específico de la capa de GUI / Vistas
logger = logging.getLogger("views.GUI.page_reservas")

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
        logger.info("Interfaz de PageReservas cargada correctamente desde el archivo UI.")

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
        self.BotonAgregar.clicked.connect(self.agregar_una_reserva)
        #self.btnModificar.clicked.connect(self.modificar_reserva_seleccionada)
        self.BotonEliminar.clicked.connect(self.eliminar_reserva_seleccionada)
        logger.info("Conexiones de botones en PageReservas inicializadas.")

    #Metodos de funcion:
    def agregar_una_reserva(self):
        """Abre el diálogo modal para registrar una nueva reserva y procesa los datos si se acepta."""
        
        logger.info("Usuario abrió el diálogo modal para crear una nueva reserva.")
        # Instanciamos el modal pasando 'self' como padre
        dialog = DialogCrearReserva(self)
        
        # Ejecutamos el diálogo de forma modal (.exec_())
        resultado = dialog.exec_()
        
        # Verificamos si el usuario presionó el botón de Guardar (Aceptar)
        if resultado == QDialog.Accepted:
            try:
                # Obtenemos los datos recopilados del cliente y de la tabla de huéspedes
                datos_nueva_reserva = dialog.obtener_datos_reserva()
                
                print("Datos listos para guardar en la BD:", datos_nueva_reserva)
                logger.info("Datos recopilados del formulario de reserva con éxito. Procediendo a persistir.")
                
                # LLAMADA AL SERVICIO: Persistimos la reserva completa de forma transaccional
                id_reserva_creada = self.servicio_reserva.crear_reserva_completa(datos_nueva_reserva)
                
                print(f"Reserva creada exitosamente con ID: {id_reserva_creada}")
                logger.info(f"Reserva #{id_reserva_creada} registrada y guardada exitosamente desde la GUI.")
                
                # Recargamos la lista visual de reservas para reflejar la nueva
                self.cargar_reservas()
                
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    f"La reserva #{id_reserva_creada} se ha registrado correctamente."
                )
                
            except Exception as e:
                print(f"Error al intentar guardar la reserva: {e}")
                logger.warning(f"Error al intentar guardar la reserva desde la interfaz: {e}")
                QMessageBox.warning(
                    self, 
                    "Error", 
                    f"No se pudo guardar la reserva:\n{e}"
                )
        else:
            logger.info("El usuario canceló el diálogo de creación de reserva.")

    def cargar_reservas(self):
        # Limpiamos la lista por seguridad
        self.listWidget.clear()

        # Obtenemos los datos directamente desde tu servicio (que consulta la BD en la nube mediante el DAO)
        reservas = self.servicio_reserva.obtener_reservas()

        if not reservas:
            print("No se encontraron reservas o hubo un error en la consulta.")
            logger.warning("No se encontraron reservas registradas para cargar en el listado visual.")
            return

        contador_cargadas = 0
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
                contador_cargadas += 1

        logger.info(f"Listado visual actualizado con éxito. Total de reservas activas listadas: {contador_cargadas}")

    def modificar_reserva(self, reserva_id):
        print(f"Modificar reserva con ID: {reserva_id}")
        logger.info(f"Acción de modificación solicitada para la reserva ID: {reserva_id}")
        #Aquí abrirías tu ventana o lógica de modificación

    def eliminar_reserva_seleccionada(self):
        #Obtenemos el ítem seleccionado en la lista
        item_seleccionado = self.listWidget.currentItem()

        if not item_seleccionado:
            print("Por favor, selecciona una reserva de la lista para eliminar.")
            logger.warning("Intento de eliminar reserva sin haber seleccionado ningún ítem en la lista.")
            return

        # Recuperamos el ID oculto que guardamos con setData(32, ...)
        reserva_id = item_seleccionado.data(32)

        try:
            self.servicio_reserva.eliminar_reserva(reserva_id)

            #Borramos visualmente el ítem de la lista para reflejar el cambio al instante
            row = self.listWidget.row(item_seleccionado)
            self.listWidget.takeItem(row)
            print("Reserva dada de baja y removida de la interfaz con éxito.")
            logger.info(f"Reserva ID {reserva_id} dada de baja y removida de la interfaz visual con éxito.")

        except Exception as e:
            print(f"Error al intentar dar de baja la reserva: {e}")
            logger.error(f"Error crítico al intentar dar de baja la reserva ID {reserva_id} desde la GUI: {e}")