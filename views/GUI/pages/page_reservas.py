# Imports:

import logging
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QDialog, QMessageBox
from PyQt5 import uic

from views.GUI.dialogs.dialog_crear_reserva import DialogCrearReserva
from views.GUI.dialogs.dialog_modificar_reserva import DialogModificarReserva
from views.GUI.dialogs.dialog_detalles_reserva import DialogDetallesReserva

from services.cliente_service import ClienteService
from services.huesped_service import HuespedService
from services.habitacion_service import HabitacionService
from services.reserva_service import ReservaService
from utils.datatypes.EstadoReserva import EstadoReserva

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
        self.BotonModificar.clicked.connect(self.modificar_reserva_seleccionada)
        self.BotonDetalles.clicked.connect(self.ver_detalles_reserva)
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
                self.listWidget.clear()
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

                # Como reserva_obj es un objeto de la clase Reserva, extraemos su estado de forma limpia
                estado_obj = reserva_obj.get_estado() if hasattr(reserva_obj, "get_estado") else EstadoReserva.RESERVADA
                estado_str = estado_obj.value if isinstance(estado_obj, EstadoReserva) else str(estado_obj)
                
                texto_visible = (
                    f"Reserva #{reserva_obj.get_id_reserva()} | "
                    f"Ingreso: {reserva_obj.get_fecha_ingreso()} | "
                    f"Salida: {reserva_obj.get_fecha_salida()} | "
                    f"Total: ${reserva_obj.get_monto_total()} | "
                    f"Estado: {estado_str.capitalize()}"
                )

                # Creamos el ítem del listado visual con ese texto
                item = QListWidgetItem(texto_visible)
                
                # Guardamos el ID real de la reserva de forma oculta en el ítem (usando el rol 32)
                item.setData(32, reserva_obj.get_id_reserva())
                
                # Añadimos el ítem al QListWidget
                self.listWidget.addItem(item)
                contador_cargadas += 1

        logger.info(f"Listado visual actualizado con éxito. Total de reservas activas listadas: {contador_cargadas}")

    def modificar_reserva_seleccionada(self):
        """Abre el diálogo para modificar las fechas, el estado y el monto de la reserva seleccionada."""
        item_seleccionado = self.listWidget.currentItem()

        if not item_seleccionado:
            print("Por favor, selecciona una reserva de la lista para modificar.")
            logger.warning("Intento de modificar reserva sin haber seleccionado ningún ítem en la lista.")
            QMessageBox.warning(self, "Selección requerida", "Por favor, selecciona una reserva de la lista para modificar.")
            return

        reserva_id = item_seleccionado.data(32)

        try:
            # Buscamos el objeto reserva actual en la lista de reservas del servicio
            reservas = self.servicio_reserva.obtener_reservas()
            reserva_encontrada = None
            for item_tupla in reservas:
                if item_tupla and item_tupla[0]:
                    r_obj, _ = item_tupla
                    if r_obj.get_id_reserva() == reserva_id:
                        reserva_encontrada = r_obj
                        break

            if not reserva_encontrada:
                QMessageBox.warning(self, "Error", "No se encontró la información de la reserva seleccionada.")
                return

            f_ingreso = reserva_encontrada.get_fecha_ingreso()
            f_salida = reserva_encontrada.get_fecha_salida()
            monto_actual = float(reserva_encontrada.get_monto_total())
            estado_actual = reserva_encontrada.get_estado() if hasattr(reserva_encontrada, "get_estado") else EstadoReserva.RESERVADA

            # Calculamos el precio por noche actual para mantenerlo proporcional al cambiar fechas
            from PyQt5.QtCore import QDate
            from datetime import date
            if isinstance(f_ingreso, date) and isinstance(f_salida, date):
                qd_in = QDate(f_ingreso.year, f_ingreso.month, f_ingreso.day)
                qd_out = QDate(f_salida.year, f_salida.month, f_salida.day)
                noches = qd_in.daysTo(qd_out)
                precio_noche_unitario = (monto_actual / noches) if noches > 0 else 0.0
            else:
                precio_noche_unitario = 0.0

            # Instanciamos el diálogo de modificación pasando el estado actual
            dialog = DialogModificarReserva(
                fecha_ingreso_actual=f_ingreso,
                fecha_salida_actual=f_salida,
                precio_total_por_noche=precio_noche_unitario,
                estado_actual=estado_actual,
                parent=self
            )

            if dialog.exec_() == QDialog.Accepted:
                nuevos_datos = dialog.obtener_nuevos_datos()
                
                # Invocamos tu método de servicio enviando el objeto EstadoReserva correspondiente
                self.servicio_reserva.modificar_reserva(
                    id_reserva=reserva_id,
                    fecha_ingreso=nuevos_datos["fecha_ingreso"],
                    fecha_salida=nuevos_datos["fecha_salida"],
                    monto_total=nuevos_datos["monto_total"],
                    estado=nuevos_datos["estado"]
                )

                logger.info(f"Reserva ID {reserva_id} modificada exitosamente desde la GUI.")
                
                # Actualización directa inmediata del ítem visual en la lista
                nuevo_ingreso = nuevos_datos["fecha_ingreso"]
                nuevo_salida = nuevos_datos["fecha_salida"]
                nuevo_monto = nuevos_datos["monto_total"]
                nuevo_estado_enum = nuevos_datos["estado"]
                nuevo_estado_str = nuevo_estado_enum.value.capitalize() if isinstance(nuevo_estado_enum, EstadoReserva) else str(nuevo_estado_enum).capitalize()

                texto_actualizado = (
                    f"Reserva #{reserva_id} | "
                    f"Ingreso: {nuevo_ingreso} | "
                    f"Salida: {nuevo_salida} | "
                    f"Total: ${nuevo_monto} | "
                    f"Estado: {nuevo_estado_str}"
                )
                item_seleccionado.setText(texto_actualizado)
                
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    f"La reserva #{reserva_id} se ha modificado correctamente."
                )

        except Exception as e:
            print(f"Error al intentar modificar la reserva: {e}")
            logger.error(f"Error crítico al intentar modificar la reserva ID {reserva_id} desde la GUI: {e}")
            QMessageBox.warning(
                self, 
                "Error", 
                f"No se pudo modificar la reserva:\n{e}"
            )

    def ver_detalles_reserva(self):
        """Abre la ventana modal elegante con la información completa de la reserva seleccionada."""
        item_seleccionado = self.listWidget.currentItem()

        if not item_seleccionado:
            print("Por favor, selecciona una reserva de la lista para ver sus detalles.")
            logger.warning("Intento de ver detalles sin haber seleccionado ningún ítem en la lista.")
            QMessageBox.warning(self, "Selección requerida", "Por favor, selecciona una reserva de la lista para ver sus detalles.")
            return

        reserva_id = item_seleccionado.data(32)

        try:
            # Invocamos al servicio centralizado para obtener toda la estructura de la reserva
            detalles_completos = self.servicio_reserva.obtener_detalles_completos_reserva(reserva_id)

            reserva_obj = detalles_completos.get("reserva")
            cliente_obj = detalles_completos.get("cliente")
            huespedes_lista = detalles_completos.get("huespedes", [])

            if not reserva_obj:
                QMessageBox.warning(self, "Error", "No se encontró la información detallada de la reserva.")
                return

            # Instanciamos el diálogo modal profesional pasando los objetos reales
            dialog = DialogDetallesReserva(
                reserva_obj=reserva_obj,
                cliente_obj=cliente_obj,
                lista_huespedes_detalle=huespedes_lista,
                parent=self
            )
            dialog.exec_()
            logger.info(f"Visualización de detalles abierta para la reserva ID #{reserva_id}.")

        except Exception as e:
            print(f"Error al mostrar detalles de la reserva: {e}")
            logger.error(f"Error crítico al mostrar detalles de la reserva ID {reserva_id} desde la GUI: {e}")
            QMessageBox.warning(
                self, 
                "Error", 
                f"No se pudieron cargar los detalles:\n{e}"
            )

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