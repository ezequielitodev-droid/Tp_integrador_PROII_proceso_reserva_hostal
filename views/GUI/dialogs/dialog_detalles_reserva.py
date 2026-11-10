# Imports:
import logging
from pathlib import Path
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from PyQt5 import uic

UI_PATH = Path(__file__).resolve().parent / "dialog_detalles_reserva.ui"
logger = logging.getLogger("views.GUI.dialog_detalles_reserva")

class DialogDetallesReserva(QDialog):
    def __init__(self, reserva_obj, cliente_obj, lista_huespedes_detalle: list, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        
        logger.info(f"Abriendo diálogo de detalles para la reserva ID #{reserva_obj.get_id_reserva()}")
        
        # Rellenar datos generales
        self.lbl_reserva_id.setText(f"<b>Reserva ID:</b> #{reserva_obj.get_id_reserva()}")
        
        if cliente_obj:
            nombre = getattr(cliente_obj, 'nombre', None) or (cliente_obj.get_nombre() if hasattr(cliente_obj, 'get_nombre') else '')
            apellido = getattr(cliente_obj, 'apellido', None) or (cliente_obj.get_apellido() if hasattr(cliente_obj, 'get_apellido') else '')
            dni = getattr(cliente_obj, 'dni', None) or (cliente_obj.get_dni() if hasattr(cliente_obj, 'get_dni') else 'N/D')
            
            # Nota: le puse un espacio entre {nombre} y {apellido} para que no aparezcan pegados
            nombre_completo = f"{nombre} {apellido}".strip()
            
            self.lbl_cliente_nombre.setText(f"<b>Titular:</b> {nombre_completo if nombre_completo else 'No disponible'}")
            self.lbl_cliente_dni.setText(f"<b>DNI:</b> {dni}")
        else:
            self.lbl_cliente_nombre.setText("<b>Titular:</b> No disponible")
            self.lbl_cliente_dni.setText("<b>DNI:</b> N/D")

        self.lbl_fechas.setText(f"<b>Estadía:</b> {reserva_obj.get_fecha_ingreso()} al {reserva_obj.get_fecha_salida()}")
        self.lbl_monto.setText(f"<b>Monto Total:</b> ${reserva_obj.get_monto_total():,.2f}")
        
        estado_obj = reserva_obj.get_estado()
        estado_str = estado_obj.value if hasattr(estado_obj, "value") else str(estado_obj)
        self.lbl_estado.setText(f"<b>Estado:</b> {estado_str.capitalize()}")

        # Rellenar tabla de huéspedes y habitaciones asociadas
        self.cargar_tabla_huespedes(lista_huespedes_detalle)

        # Conexión botón cerrar
        self.btn_cerrar.clicked.connect(self.accept)

    def cargar_tabla_huespedes(self, lista_huespedes):
        """Llena la tabla con los huéspedes vinculados a esta reserva."""
        self.table_detalles_huespedes.setRowCount(0)
        if not lista_huespedes:
            return

        for fila, h_data in enumerate(lista_huespedes):
            self.table_detalles_huespedes.insertRow(fila)
            
            # h_data puede ser un diccionario o tupla según cómo te lo devuelva tu servicio/DAO
            # (Ajusta las claves o índices según tu implementación de backend)
            nombre = h_data.get("nombre", "") if isinstance(h_data, dict) else getattr(h_data, "nombre", "")
            apellido = h_data.get("apellido", "") if isinstance(h_data, dict) else getattr(h_data, "apellido", "")
            dni = h_data.get("dni", "") if isinstance(h_data, dict) else getattr(h_data, "dni", "")
            telefono = h_data.get("telefono", "") if isinstance(h_data, dict) else getattr(h_data, "telefono", "")
            habitacion = h_data.get("habitacion", "N/D") if isinstance(h_data, dict) else getattr(h_data, "habitacion", "N/D")
            precio = h_data.get("precio", 0.0) if isinstance(h_data, dict) else getattr(h_data, "precio", 0.0)

            self.table_detalles_huespedes.setItem(fila, 0, QTableWidgetItem(f"{nombre} {apellido}".strip()))
            self.table_detalles_huespedes.setItem(fila, 1, QTableWidgetItem(str(dni)))
            self.table_detalles_huespedes.setItem(fila, 2, QTableWidgetItem(str(telefono)))
            self.table_detalles_huespedes.setItem(fila, 3, QTableWidgetItem(str(habitacion)))
            self.table_detalles_huespedes.setItem(fila, 4, QTableWidgetItem(f"${float(precio):,.2f}"))