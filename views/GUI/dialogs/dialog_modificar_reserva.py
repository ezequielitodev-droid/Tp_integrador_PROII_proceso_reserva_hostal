# Imports:

import logging
from decimal import Decimal
from pathlib import Path
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import QDate
from PyQt5 import uic

from utils.datatypes.EstadoReserva import EstadoReserva  # Ajusta la ruta de import si es necesario

UI_PATH = Path(__file__).resolve().parent / "dialog_modificar_reserva.ui"

# Global Variables:
logger = logging.getLogger("views.GUI.dialog_modificar_reserva")

class DialogModificarReserva(QDialog):

    def __init__(self, fecha_ingreso_actual, fecha_salida_actual, precio_total_por_noche: float, estado_actual=None, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        
        logger.info("Diálogo modal DialogModificarReserva cargado correctamente.")
        
        self.precio_total_por_noche = float(precio_total_por_noche)
        self._monto_calculado_actual = Decimal("0.00")

        # Configuración del checkbox según el estado real de la reserva
        if hasattr(self, 'check_cancelar'):
            # Si el estado actual es CANCELADA (ya sea como Enum o string), tildamos el checkbox. De lo contrario, queda destildado.
            es_cancelada = False
            if estado_actual:
                if isinstance(estado_actual, EstadoReserva):
                    es_cancelada = (estado_actual == EstadoReserva.CANCELADA)
                else:
                    es_cancelada = ("cancelada" in str(estado_actual).lower() or "cancel" in str(estado_actual).lower())
            
            self.check_cancelar.setChecked(es_cancelada)

        # Configuración mínima del calendario (año actual 2026)
        hoy = QDate.currentDate()
        if hasattr(self, 'input_fecha_ingreso'):
            self.input_fecha_ingreso.setMinimumDate(hoy)
            self.input_fecha_ingreso.setCalendarPopup(True)
            if fecha_ingreso_actual:
                self.input_fecha_ingreso.setDate(QDate(fecha_ingreso_actual.year, fecha_ingreso_actual.month, fecha_ingreso_actual.day))
            self.input_fecha_ingreso.dateChanged.connect(self.recalcular_monto_total)

        if hasattr(self, 'input_fecha_salida'):
            self.input_fecha_salida.setMinimumDate(hoy)
            self.input_fecha_salida.setCalendarPopup(True)
            if fecha_salida_actual:
                self.input_fecha_salida.setDate(QDate(fecha_salida_actual.year, fecha_salida_actual.month, fecha_salida_actual.day))
            self.input_fecha_salida.dateChanged.connect(self.recalcular_monto_total)

        # Conexiones de botones
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_guardar.clicked.connect(self.validar_y_aceptar)

        # Cálculo inicial con los datos precargados
        self.recalcular_monto_total()

    def recalcular_monto_total(self):
        """Calcula de forma automática en base a las nuevas fechas y el precio por noche fijo."""
        if not hasattr(self, 'input_fecha_ingreso') or not hasattr(self, 'input_fecha_salida'):
            return

        qdate_ingreso = self.input_fecha_ingreso.date()
        qdate_salida = self.input_fecha_salida.date()

        noches = qdate_ingreso.daysTo(qdate_salida)
        
        if noches <= 0:
            self._monto_calculado_actual = Decimal("0.00")
            if hasattr(self, 'label_monto_total_valor'):
                self.label_monto_total_valor.setText("$ 0.00 (Fechas inválidas)")
            return

        total_val = Decimal(str(noches)) * Decimal(str(self.precio_total_por_noche))
        self._monto_calculado_actual = total_val.quantize(Decimal("0.01"))

        if hasattr(self, 'label_monto_total_valor'):
            self.label_monto_total_valor.setText(f"$ {self._monto_calculado_actual:,.2f}  ({noches} noches)")
            
        logger.debug(f"Monto recalculado para modificación: {noches} noches * ${self.precio_total_por_noche} = ${self._monto_calculado_actual}")

    def validar_y_aceptar(self):
        """Validación previa antes de cerrar el diálogo exitosamente."""
        qdate_ingreso = self.input_fecha_ingreso.date()
        qdate_salida = self.input_fecha_salida.date()

        if qdate_ingreso.daysTo(qdate_salida) <= 0:
            QMessageBox.warning(self, "Fechas inválidas", "La fecha de salida debe ser posterior a la fecha de ingreso.")
            return

        self.accept()

    def obtener_nuevos_datos(self) -> dict:
        """Retorna las fechas actualizadas, el EstadoReserva correspondiente y el monto recalculado."""
        estado_nuevo = EstadoReserva.CANCELADA if self.check_cancelar.isChecked() else EstadoReserva.RESERVADA
        return {
            "fecha_ingreso": self.input_fecha_ingreso.date().toPyDate(),
            "fecha_salida": self.input_fecha_salida.date().toPyDate(),
            "monto_total": self._monto_calculado_actual,
            "estado": estado_nuevo
        }