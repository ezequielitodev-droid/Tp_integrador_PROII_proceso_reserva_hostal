# Imports:

import logging
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QDialog, QMessageBox
from PyQt5.QtCore import QDate
from PyQt5 import uic

from views.GUI.dialogs.dialog_crear_reserva import DialogCrearReserva
from views.GUI.dialogs.dialog_modificar_reserva import DialogModificarReserva
from views.GUI.dialogs.dialog_detalles_reserva import DialogDetallesReserva

from services.cliente_service import ClienteService
from services.huesped_service import HuespedService
from services.habitacion_service import HabitacionService
from services.reserva_service import ReservaService
from utils.datatypes.EstadoReserva import EstadoReserva
from backups.backup_manager import BackupManager

# Constants:

# Paths:

FILE_UI_PATH = Path(__file__).resolve().parent / "page_reservas.ui"

# Global Variables:

logger = logging.getLogger("views.GUI.page_reservas")


# Class:

class PageReservas(QWidget):

    # Constructor:

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

        # Inyectamos las dependencias de los servicios:
        self.servicio_cliente = servicio_cliente or ClienteService()
        self.servicio_huesped = servicio_huesped or HuespedService()
        self.servicio_habitacion = servicio_habitacion or HabitacionService()
        self.servicio_reserva = servicio_reserva or ReservaService()

        # Caché local para filtrar instantáneamente sin volver a consultar la BD
        self._reservas_cache: list = []

        # Poblamos los valores iniciales de los widgets de filtro definidos en el .ui
        self.init_filtros_defaults()

        # Inicializamos las conexiones de señales y slots
        self.init_ui_connections()
        self.cargar_reservas()

    def init_filtros_defaults(self):
        """Inicializa las opciones del ComboBox de estados y el rango de fechas por defecto."""
        self.combo_filtro_estado.clear()
        self.combo_filtro_estado.addItem("Todos los estados", None)
        for estado in EstadoReserva:
            self.combo_filtro_estado.addItem(estado.value.capitalize(), estado)

        hoy = QDate.currentDate()
        self.date_filtro_desde.setDate(hoy.addMonths(-1))
        self.date_filtro_hasta.setDate(hoy.addMonths(1))

    # Metodo conector:
    def init_ui_connections(self):
        self.BotonAgregar.clicked.connect(self.agregar_una_reserva)
        self.BotonModificar.clicked.connect(self.modificar_reserva_seleccionada)
        self.BotonDetalles.clicked.connect(self.ver_detalles_reserva)
        self.BotonEliminar.clicked.connect(self.eliminar_reserva_seleccionada)

        # Conexiones de los filtros del .ui
        self.input_buscar_reserva.textChanged.connect(self.aplicar_filtros)
        self.combo_filtro_estado.currentIndexChanged.connect(self.aplicar_filtros)
        self.chk_filtrar_fechas.toggled.connect(self._toggle_filtro_fechas)
        self.date_filtro_desde.dateChanged.connect(self.aplicar_filtros)
        self.date_filtro_hasta.dateChanged.connect(self.aplicar_filtros)
        self.btn_limpiar_filtros.clicked.connect(self.limpiar_filtros)

        # Conexión para el botón de hacer copia de seguridad en la vista de reservas
        if hasattr(self, "BotonCopiaSeguridad"):
            self.BotonCopiaSeguridad.clicked.connect(self.generar_copia_seguridad_gui)

        logger.info("Conexiones de botones y filtros en PageReservas inicializadas.")

    def _toggle_filtro_fechas(self, activo: bool):
        self.date_filtro_desde.setEnabled(activo)
        self.date_filtro_hasta.setEnabled(activo)
        self.aplicar_filtros()

    def limpiar_filtros(self):
        """Restablece todos los controles de filtro a su estado inicial."""
        self.input_buscar_reserva.blockSignals(True)
        self.combo_filtro_estado.blockSignals(True)
        self.chk_filtrar_fechas.blockSignals(True)

        self.input_buscar_reserva.clear()
        self.combo_filtro_estado.setCurrentIndex(0)
        self.chk_filtrar_fechas.setChecked(False)
        self.date_filtro_desde.setEnabled(False)
        self.date_filtro_hasta.setEnabled(False)

        self.input_buscar_reserva.blockSignals(False)
        self.combo_filtro_estado.blockSignals(False)
        self.chk_filtrar_fechas.blockSignals(False)

        self.aplicar_filtros()

    def aplicar_filtros(self):
        """Filtra la caché local mediante ReservaService y actualiza el listado visual."""
        texto = self.input_buscar_reserva.text()
        estado_sel = self.combo_filtro_estado.currentData()

        f_desde = self.date_filtro_desde.date().toPyDate() if self.chk_filtrar_fechas.isChecked() else None
        f_hasta = self.date_filtro_hasta.date().toPyDate() if self.chk_filtrar_fechas.isChecked() else None

        reservas_filtradas = self.servicio_reserva.filtrar_reservas(
            reservas=self._reservas_cache,
            texto_busqueda=texto,
            estado=estado_sel,
            fecha_desde=f_desde,
            fecha_hasta=f_hasta
        )

        self._renderizar_lista_reservas(reservas_filtradas)

    def _renderizar_lista_reservas(self, reservas: list):
        """Renderiza los ítems filtrados en self.listWidget."""
        self.listWidget.clear()

        contador_cargadas = 0
        for item_tupla in reservas:
            if item_tupla is None:
                continue

            reserva_obj, id_cliente = item_tupla

            if reserva_obj.get_activo() == 1:
                estado_obj = reserva_obj.get_estado() if hasattr(reserva_obj, "get_estado") else EstadoReserva.RESERVADA
                estado_str = estado_obj.value if isinstance(estado_obj, EstadoReserva) else str(estado_obj)

                texto_visible = (
                    f"Reserva #{reserva_obj.get_id_reserva()} | "
                    f"Ingreso: {reserva_obj.get_fecha_ingreso()} | "
                    f"Salida: {reserva_obj.get_fecha_salida()} | "
                    f"Total: ${reserva_obj.get_monto_total()} | "
                    f"Estado: {estado_str.capitalize()}"
                )

                item = QListWidgetItem(texto_visible)
                item.setData(32, reserva_obj.get_id_reserva())
                self.listWidget.addItem(item)
                contador_cargadas += 1

        logger.info(f"Listado visual actualizado con éxito. Total de reservas mostradas: {contador_cargadas}")

    # Metodos de funcion:
    def agregar_una_reserva(self):
        """Abre el diálogo modal para registrar una nueva reserva y procesa los datos si se acepta."""
        logger.info("Usuario abrió el diálogo modal para crear una nueva reserva.")
        dialog = DialogCrearReserva(self)
        resultado = dialog.exec_()

        if resultado == QDialog.Accepted:
            try:
                datos_nueva_reserva = dialog.obtener_datos_reserva()
                print("Datos listos para guardar en la BD:", datos_nueva_reserva)
                logger.info("Datos recopilados del formulario de reserva con éxito. Procediendo a persistir.")

                id_reserva_creada = self.servicio_reserva.crear_reserva_completa(datos_nueva_reserva)

                print(f"Reserva creada exitosamente con ID: {id_reserva_creada}")
                logger.info(f"Reserva #{id_reserva_creada} registrada y guardada exitosamente desde la GUI.")

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
        """Consulta las reservas en la BD, actualiza la caché local y aplica los filtros activos."""
        self.listWidget.clear()

        reservas = self.servicio_reserva.obtener_reservas()

        if not reservas:
            self._reservas_cache = []
            print("No se encontraron reservas o hubo un error en la consulta.")
            logger.warning("No se encontraron reservas registradas para cargar en el listado visual.")
            return

        self._reservas_cache = reservas
        self.aplicar_filtros()

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

            from datetime import date
            if isinstance(f_ingreso, date) and isinstance(f_salida, date):
                qd_in = QDate(f_ingreso.year, f_ingreso.month, f_ingreso.day)
                qd_out = QDate(f_salida.year, f_salida.month, f_salida.day)
                noches = qd_in.daysTo(qd_out)
                precio_noche_unitario = (monto_actual / noches) if noches > 0 else 0.0
            else:
                precio_noche_unitario = 0.0

            dialog = DialogModificarReserva(
                fecha_ingreso_actual=f_ingreso,
                fecha_salida_actual=f_salida,
                precio_total_por_noche=precio_noche_unitario,
                estado_actual=estado_actual,
                parent=self
            )

            if dialog.exec_() == QDialog.Accepted:
                nuevos_datos = dialog.obtener_nuevos_datos()

                self.servicio_reserva.modificar_reserva(
                    id_reserva=reserva_id,
                    fecha_ingreso=nuevos_datos["fecha_ingreso"],
                    fecha_salida=nuevos_datos["fecha_salida"],
                    monto_total=nuevos_datos["monto_total"],
                    estado=nuevos_datos["estado"]
                )

                logger.info(f"Reserva ID {reserva_id} modificada exitosamente desde la GUI.")

                # Sincronizamos caché y filtros activos
                self.cargar_reservas()

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
            detalles_completos = self.servicio_reserva.obtener_detalles_completos_reserva(reserva_id)

            reserva_obj = detalles_completos.get("reserva")
            cliente_obj = detalles_completos.get("cliente")
            huespedes_lista = detalles_completos.get("huespedes", [])

            if not reserva_obj:
                QMessageBox.warning(self, "Error", "No se encontró la información detallada de la reserva.")
                return

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
        item_seleccionado = self.listWidget.currentItem()

        if not item_seleccionado:
            print("Por favor, selecciona una reserva de la lista para eliminar.")
            logger.warning("Intento de eliminar reserva sin haber seleccionado ningún ítem en la lista.")
            return

        reserva_id = item_seleccionado.data(32)

        try:
            self.servicio_reserva.eliminar_reserva(reserva_id)

            row = self.listWidget.row(item_seleccionado)
            self.listWidget.takeItem(row)
            self._reservas_cache = [
                item for item in self._reservas_cache
                if not (item and item[0] and item[0].get_id_reserva() == reserva_id)
            ]
            print("Reserva dada de baja y removida de la interfaz con éxito.")
            logger.info(f"Reserva ID {reserva_id} dada de baja y removida de la interfaz visual con éxito.")

        except Exception as e:
            print(f"Error al intentar dar de baja la reserva: {e}")
            logger.error(f"Error crítico al intentar dar de baja la reserva ID {reserva_id} desde la GUI: {e}")

    def generar_copia_seguridad_gui(self):
        """Genera una copia de seguridad en JSON de toda la base de datos al hacer clic en el botón."""
        try:
            ruta_backup = BackupManager.generar_copia_seguridad()
            if ruta_backup:
                QMessageBox.information(
                    self,
                    "Copia de Seguridad Exitosa",
                    f"El respaldo de la base de datos se ha generado correctamente en:\n\n{ruta_backup}"
                )
                logger.info(f"Copia de seguridad generada desde la interfaz en: {ruta_backup}")
            else:
                QMessageBox.critical(
                    self,
                    "Error de Respaldo",
                    "No se pudo generar la copia de seguridad. Revisa los logs para más detalles."
                )
        except Exception as e:
            logger.error(f"Error crítico al generar copia de seguridad desde la GUI: {e}")
            QMessageBox.warning(self, "Error", f"Ocurrió un error inesperado:\n{e}")