# Imports:

import logging
from models.huesped import Huesped
from dao.huesped_dao import HuespedDAO
from dao.reserva_dao import ReservaDAO
from utils.validators.datavalidators import (
    es_nombre_valido,
    es_apellido_valido,
    es_dni_valido,
    es_telefono_valido,
    es_correo_valido
)

# Constants:

# Global Variables:

logger = logging.getLogger(__name__)

# Class:

class HuespedService:

    # Constructor:

    def __init__(
            self, 
            huesped_dao: HuespedDAO | None = None,
            reserva_dao: ReservaDAO | None = None
    ):
        self.huesped_dao = huesped_dao or HuespedDAO()
        self.reserva_dao = reserva_dao or ReservaDAO()

    # Métodos estratégicos:

    def crear_huesped(
            self, 
            nombre: str, 
            apellido: str, 
            dni: str, 
            telefono: str, 
            correo: str 
    ) -> int | None:
        """
        Aplica las reglas de negocio y validaciones antes de persistir un huésped.
        """
        # 1. Validaciones estructurales con tus validadores del sistema
        if not es_nombre_valido(nombre):
            raise ValueError(f"El nombre '{nombre}' no es válido.")

        if not es_apellido_valido(apellido):
            raise ValueError(f"El apellido '{apellido}' no es válido.")

        if not es_dni_valido(dni):
            raise ValueError(f"El DNI '{dni}' no tiene un formato válido (7 u 8 dígitos).")

        if not es_telefono_valido(telefono):
            raise ValueError(f"El teléfono '{telefono}' no es válido (debe tener exactamente 10 dígitos).")

        if not es_correo_valido(correo):
            raise ValueError(f"El correo '{correo}' no tiene un formato válido o excede el límite.")

        dni_limpio = dni.strip().replace(".", "")
        huesped_existente = self.huesped_dao.obtener_huesped_por_dni(dni_limpio)

        if huesped_existente and huesped_existente.get_activo():
            logger.warning(f"Intento de registrar huésped con DNI duplicado: {dni_limpio}")
            raise ValueError(f"Ya existe un huésped activo con el DNI {dni}")

        nuevo_huesped = Huesped(
            id_huesped=None, 
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            dni=dni_limpio,
            telefono=telefono.strip(),
            activo=True
        )

        id_generado = self.huesped_dao.crear_huesped(nuevo_huesped)

        return id_generado

    def obtener_huespedes(self) -> list[Huesped | None]:
        return self.huesped_dao.obtener_huespedes()

    def obtener_huesped_por_id(self, id_huesped: int) -> Huesped | None:
        return self.huesped_dao.obtener_huesped_por_id(id_huesped)

    def obtener_huesped_por_dni(self, dni: str) -> Huesped | None:
        dni_limpio = dni.strip().replace(".", "")
        return self.huesped_dao.obtener_huesped_por_dni(dni_limpio)

    def eliminar_huesped(self, id_huesped: int) -> bool:

        #Pendiende validar, nececito una consulta compleja

        return self.huesped_dao.eliminar_huesped(id_huesped)