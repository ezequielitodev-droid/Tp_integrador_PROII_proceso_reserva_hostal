# Imports:

import logging
from pathlib import Path
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic

from services.habitacion_service import HabitacionService

UI_PATH = Path(__file__).resolve().parent / "dialog_agregar_huesped.ui"

# Global Variables:
logger = logging.getLogger("views.GUI.dialog_agregar_huesped")

class DialogAgregarHuesped(QDialog):

    def __init__(self, servicio_habitacion: HabitacionService | None = None, parent=None):
        
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        
        logger.info("Diálogo modal DialogAgregarHuesped cargado correctamente.")

        # Inyectamos el servicio de habitación para poblar el combo box
        self.servicio_habitacion = servicio_habitacion or HabitacionService()

        # Conexiones principales
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_aceptar.clicked.connect(self.aceptar_huesped)

        # Cargamos las habitaciones en el ComboBox
        self.cargar_habitaciones_en_combo()

    def cargar_habitaciones_en_combo(self):
        try:
            habitaciones = self.servicio_habitacion.obtener_habitaciones()
            self.combo_habitaciones.clear()

            for hab in habitaciones:
                if hab and hab.get_activo():
                    precio = float(hab.get_precio_noche())
                    texto_combo = f"Habitación #{hab.get_numero()} (Cap: {hab.get_capacidad()} - ${precio:,.2f})"
                    
                    # Guardamos un diccionario con el ID y el Precio en el item data
                    data_habitacion = {
                        "id_habitacion": hab.get_id_habitacion(),
                        "precio_noche": precio
                    }
                    self.combo_habitaciones.addItem(texto_combo, data_habitacion)

            logger.info("Habitaciones activas cargadas exitosamente en el ComboBox del diálogo.")
        except Exception as e:
            logger.error(f"Error al cargar las habitaciones en el combo: {e}")
            QMessageBox.warning(self, "Error", f"No se pudieron cargar las habitaciones: {e}")

    def aceptar_huesped(self):
        """Valida que los campos no estén vacíos antes de aceptar."""
        nombre = self.input_huesped_nombre.text().strip()
        apellido = self.input_huesped_apellido.text().strip()
        dni = self.input_huesped_dni.text().strip()
        
        if not nombre or not apellido or not dni:
            QMessageBox.warning(self, "Campos incompletos", "Nombre, Apellido y DNI son obligatorios para el huésped.")
            return

        self.accept()

    def obtener_datos_huesped(self) -> dict:
        """Extrae la información ingresada, el ID de la habitación y su precio por noche."""
        data_habitacion = self.combo_habitaciones.currentData()
        
        id_hab = None
        precio_hab = 0.0

        if isinstance(data_habitacion, dict):
            id_hab = data_habitacion.get("id_habitacion")
            precio_hab = data_habitacion.get("precio_noche", 0.0)
        else:
            # Compatibilidad por si acaso quedó algún valor viejo suelto
            id_hab = data_habitacion

        return {
            "nombre": self.input_huesped_nombre.text().strip(),
            "apellido": self.input_huesped_apellido.text().strip(),
            "dni": self.input_huesped_dni.text().strip(),
            "telefono": self.input_huesped_telefono.text().strip(),
            "id_habitacion": id_hab,
            "precio_noche": precio_hab
        }