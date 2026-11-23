# Imports:

import logging
from decimal import Decimal
from pathlib import Path
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox, QCompleter, QLabel
from PyQt5.QtCore import QDate, Qt, QTimer
from PyQt5 import uic

from models.cliente import Cliente
from services.cliente_service import ClienteService
from views.GUI.dialogs.dialog_agregar_huesped import DialogAgregarHuesped

UI_PATH = Path(__file__).resolve().parent / "dialog_crear_reserva.ui"

# Global Variables:
logger = logging.getLogger("views.GUI.dialog_crear_reserva")


class DialogCrearReserva(QDialog):

    def __init__(self, parent=None, servicio_cliente: ClienteService | None = None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)

        logger.info("Diálogo modal DialogCrearReserva cargado correctamente desde el archivo UI.")

        self.servicio_cliente = servicio_cliente or ClienteService()
        self._clientes_map: dict[str, Cliente] = {}

        self.lista_huespedes_temporal = []
        self._monto_calculado_actual = Decimal("0.00")

        # 1. Configuramos los calendarios (mínimo hoy, año 2026)
        hoy = QDate.currentDate()
        maniana = hoy.addDays(1)

        if hasattr(self, 'input_fecha_ingreso'):
            self.input_fecha_ingreso.setMinimumDate(hoy)
            self.input_fecha_ingreso.setDate(hoy)
            self.input_fecha_ingreso.setCalendarPopup(True)
            self.input_fecha_ingreso.dateChanged.connect(self.recalcular_monto_total)

        if hasattr(self, 'input_fecha_salida'):
            self.input_fecha_salida.setMinimumDate(hoy)
            self.input_fecha_salida.setDate(maniana)
            self.input_fecha_salida.setCalendarPopup(True)
            self.input_fecha_salida.dateChanged.connect(self.recalcular_monto_total)

        # 2. Inicializamos el autocompletado de clientes existentes
        self.init_autocompletado_cliente()

        # 3. Conexiones de botones principales
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_guardar.clicked.connect(self.accept)
        self.btn_agregar_huesped.clicked.connect(self.abrir_modal_huesped)

        # 4. Calculamos el monto inicial por defecto
        self.recalcular_monto_total()

        logger.info("Conexiones de botones principales en DialogCrearReserva inicializadas.")

    def init_autocompletado_cliente(self):
        """Precarga los clientes activos una sola vez y habilita el desplegable al tipear."""
        self.lbl_estado_cliente = QLabel("")
        self.lbl_estado_cliente.setStyleSheet("color: #36966B; font-size: 11px; font-weight: bold;")
        if hasattr(self, "verticalLayout_cliente"):
            self.verticalLayout_cliente.insertWidget(1, self.lbl_estado_cliente)

        try:
            clientes = self.servicio_cliente.obtener_clientes() or []
        except Exception as e:
            logger.warning(f"No se pudieron precargar clientes para autocompletado: {e}")
            clientes = []

        etiquetas = []
        for cli in clientes:
            if cli and cli.get_activo():
                etiqueta = f"{cli.get_nombre()} {cli.get_apellido()} — DNI: {cli.get_dni()}"
                etiquetas.append(etiqueta)
                self._clientes_map[etiqueta] = cli

        self.completer_cliente = QCompleter(etiquetas, self)
        self.completer_cliente.setCaseSensitivity(Qt.CaseInsensitive) # type: ignore[attr-defined]
        self.completer_cliente.setFilterMode(Qt.MatchContains) # type: ignore[attr-defined]
        self.completer_cliente.setCompletionMode(QCompleter.PopupCompletion) # type: ignore[attr-defined]

        popup = self.completer_cliente.popup()
        if popup is not None:
            popup.setStyleSheet("""
                QListView {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                    border: 1px solid #FDB93B;
                    border-radius: 5px;
                    padding: 4px;
                    font-size: 12px;
                }
                QListView::item {
                    padding: 6px;
                }
                QListView::item:selected {
                    background-color: #FDB93B;
                    color: #232323;
                    font-weight: bold;
                }
            """)

        self.input_cliente_nombre.setCompleter(self.completer_cliente)
        self.input_cliente_apellido.setCompleter(self.completer_cliente)
        self.input_cliente_dni.setCompleter(self.completer_cliente)

        self.completer_cliente.activated[str].connect(self._autocompletar_datos_cliente)
        self.input_cliente_dni.textEdited.connect(lambda: self.lbl_estado_cliente.setText(""))

    def _autocompletar_datos_cliente(self, etiqueta_seleccionada: str):
        """Rellena todos los campos del cliente al elegir una coincidencia del desplegable."""
        cliente = self._clientes_map.get(etiqueta_seleccionada)
        if not cliente:
            return

        def rellenar():
            self.input_cliente_nombre.setText(str(cliente.get_nombre() or ""))
            self.input_cliente_apellido.setText(str(cliente.get_apellido() or ""))
            self.input_cliente_dni.setText(str(cliente.get_dni() or ""))
            self.input_cliente_telefono.setText(str(cliente.get_telefono() or ""))
            self.input_cliente_correo.setText(str(cliente.get_correo() or ""))
            self.lbl_estado_cliente.setText(f"✓ Cliente existente seleccionado (ID #{cliente.get_id_persona()})")

        QTimer.singleShot(0, rellenar)

    def recalcular_monto_total(self):
        """Calcula dinámicamente: (Noches * Suma de precios por noche de las habitaciones)."""
        if not hasattr(self, 'input_fecha_ingreso') or not hasattr(self, 'input_fecha_salida'):
            return

        qdate_ingreso = self.input_fecha_ingreso.date()
        qdate_salida = self.input_fecha_salida.date()

        noches = qdate_ingreso.daysTo(qdate_salida)

        # Si la fecha de salida es menor o igual a la de ingreso, el monto es 0
        if noches <= 0:
            self._monto_calculado_actual = Decimal("0.00")
            if hasattr(self, 'label_monto_total_valor'):
                self.label_monto_total_valor.setText("$ 0.00")
            return

        # Sumamos el precio por noche de todas las habitaciones en la lista temporal de huéspedes
        precio_total_por_noche = sum(float(h.get("precio_noche", 0.0)) for h in self.lista_huespedes_temporal)

        # Multiplicamos noches por la suma de tarifas
        total_val = Decimal(str(noches)) * Decimal(str(precio_total_por_noche))
        self._monto_calculado_actual = total_val.quantize(Decimal("0.01"))

        # Actualizamos dinámicamente el label visual del UI
        if hasattr(self, 'label_monto_total_valor'):
            self.label_monto_total_valor.setText(f"$ {self._monto_calculado_actual:,.2f}")

        logger.debug(f"Monto recalculado: {noches} noches * ${precio_total_por_noche} = ${self._monto_calculado_actual}")

    def abrir_modal_huesped(self):
        """Abre el diálogo para registrar un huésped y asociarlo a una habitación."""
        logger.info("Usuario abrió el diálogo secundario para añadir huésped y habitación.")

        dialog_huesped = DialogAgregarHuesped(parent=self)
        resultado = dialog_huesped.exec_()

        if resultado == QDialog.Accepted:
            datos_huesped = dialog_huesped.obtener_datos_huesped()
            self.lista_huespedes_temporal.append(datos_huesped)

            # Reflejamos en la tabla y recalculamos el monto al instante
            self.actualizar_tabla_huespedes_visual()
            self.recalcular_monto_total()

            logger.info(f"Huésped {datos_huesped.get('nombre')} añadido. Monto actualizado.")

    def actualizar_tabla_huespedes_visual(self):
        """Rellena la tabla del UI con los huéspedes agregados y ajusta las columnas."""
        if hasattr(self, 'table_huespedes'):
            self.table_huespedes.setRowCount(len(self.lista_huespedes_temporal))

            # Aseguramos que tenga 5 columnas
            self.table_huespedes.setColumnCount(5)
            self.table_huespedes.setHorizontalHeaderLabels(["Nombre y Apellido", "DNI", "Teléfono", "Habitación", "Precio / Noche"])

            for row, h in enumerate(self.lista_huespedes_temporal):
                nombre_completo = f"{h.get('nombre', '')} {h.get('apellido', '')}"
                precio_noche = h.get("precio_noche", 0.0)

                self.table_huespedes.setItem(row, 0, QTableWidgetItem(nombre_completo))
                self.table_huespedes.setItem(row, 1, QTableWidgetItem(h.get("dni", "")))
                self.table_huespedes.setItem(row, 2, QTableWidgetItem(h.get("telefono", "")))
                self.table_huespedes.setItem(row, 3, QTableWidgetItem(str(h.get("id_habitacion", ""))))
                self.table_huespedes.setItem(row, 4, QTableWidgetItem(f"$ {float(precio_noche):,.2f}"))

            # Hacemos que las columnas se estiren de forma equilibrada para que no se corte nada
            header = self.table_huespedes.horizontalHeader()
            header.setSectionResizeMode(0, header.Stretch)  # Nombre se estira más
            header.setSectionResizeMode(1, header.ResizeToContents)
            header.setSectionResizeMode(2, header.ResizeToContents)
            header.setSectionResizeMode(3, header.ResizeToContents)
            header.setSectionResizeMode(4, header.ResizeToContents)

    def obtener_datos_reserva(self) -> dict:
        """Extrae la estructura completa incluyendo fechas y el monto calculado automáticamente."""
        logger.info("Extrayendo estructura completa del formulario de reserva...")

        fecha_ingreso_obj = self.input_fecha_ingreso.date().toPyDate() if hasattr(self, 'input_fecha_ingreso') else None
        fecha_salida_obj = self.input_fecha_salida.date().toPyDate() if hasattr(self, 'input_fecha_salida') else None

        datos_finales = {
            "cliente": {
                "nombre": self.input_cliente_nombre.text().strip(),
                "apellido": self.input_cliente_apellido.text().strip(),
                "dni": self.input_cliente_dni.text().strip(),
                "telefono": self.input_cliente_telefono.text().strip(),
                "correo": self.input_cliente_correo.text().strip()
            },
            "fechas": {
                "fecha_ingreso": fecha_ingreso_obj,
                "fecha_salida": fecha_salida_obj,
                "monto_total": self._monto_calculado_actual  # <--- Se va directo a la BD
            },
            "huespedes": self.lista_huespedes_temporal
        }

        logger.debug(f"Diccionario de reserva generado con éxito para titular DNI: {datos_finales['cliente'].get('dni')}")
        return datos_finales