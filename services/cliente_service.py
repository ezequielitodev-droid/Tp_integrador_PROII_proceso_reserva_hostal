# Imports:

import logging
from models.cliente import Cliente
from dao.cliente_dao import ClienteDAO
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

class ClienteService:

    # Constructor:

    def __init__(
            self, 
            cliente_dao: ClienteDAO | None = None
    ):
        # Inyectamos la dependencia del DAO
        self.cliente_dao = cliente_dao or ClienteDAO()

    # Métodos estratégicos:

    def crear_cliente(
            self, 
            nombre: str, 
            apellido: str, 
            dni: str, 
            telefono: str, 
            correo: str 
    ) -> int | None:
        """
        Aplica las reglas de negocio y validaciones antes de persistir a cliente.
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
        cliente_existente = self.cliente_dao.obtener_cliente_por_dni(dni_limpio)

        if cliente_existente and cliente_existente.get_activo():
            logger.warning(f"Intento de registrar cliente con DNI duplicado: {dni_limpio}")
            raise ValueError(f"Ya existe un cliente activo con el DNI {dni}")

        nuevo_cliente = Cliente(
            id_cliente=None, 
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            dni=dni_limpio,
            telefono=telefono.strip(),
            correo=correo.strip(),
            activo=True
        )

        id_generado = self.cliente_dao.crear_cliente(nuevo_cliente)

        return id_generado

    def obtener_clientes(self) -> list[Cliente | None]:
        return self.cliente_dao.obtener_clientes()

    def obtener_cliente_por_id(self, id_cliente: int) -> Cliente | None:
        return self.cliente_dao.obtener_cliente_por_id(id_cliente)
        
    def eliminar_cliente(self, id_cliente: int) -> bool:
        return self.cliente_dao.eliminar_cliente(id_cliente)