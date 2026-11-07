# Imports:

import logging
from datetime import date
from decimal import Decimal
from models.reserva import Reserva
from dao.reserva_dao import ReservaDAO
from dao.cliente_dao import ClienteDAO
from utils.datatypes.EstadoReserva import EstadoReserva
from utils.validators.datavalidators import (
    es_fecha_reserva_valida,
    es_fecha_ingreso_valida,
    es_fecha_salida_valida,
    es_rango_fechas_valido,
    es_estado_reserva_valido,
    es_monto_total_valido,
    es_id_persona_valido
)

# Constants:

# Global Variables:

logger = logging.getLogger(__name__)

# Class:

class ReservaService:

    # Constructor:

    def __init__(
            self, 
            reserva_dao: ReservaDAO | None = None,
            cliente_dao: ClienteDAO | None = None
    ):
        # Inyectamos las dependencias necesarias para las reglas cruzadas
        self.reserva_dao = reserva_dao or ReservaDAO()
        self.cliente_dao = cliente_dao or ClienteDAO()

    # Métodos estratégicos:

    def crear_reserva(
            self, 
            fecha_reserva: date,
            fecha_ingreso: date, 
            fecha_salida: date, 
            monto_total: Decimal | float, 
            id_cliente: int,
            estado: EstadoReserva | str = EstadoReserva.RESERVADA  # <--- Corregido aquí
    ) -> int | None:
        """
            Aplica reglas de negocio y validaciones antes de persistir una reserva.
            Verifica la existencia del cliente y la coherencia en las fechas y montos.
        """
        # 1. Validaciones estructurales con los validadores del sistema
        if not es_fecha_reserva_valida(fecha_reserva):
            raise ValueError("La fecha de reserva no es válida.")

        if not es_fecha_ingreso_valida(fecha_ingreso):
            raise ValueError("La fecha de ingreso no es válida.")

        if not es_fecha_salida_valida(fecha_salida):
            raise ValueError("La fecha de salida no es válida.")

        if not es_rango_fechas_valido(fecha_ingreso, fecha_salida):
            raise ValueError("La fecha de salida debe ser posterior a la fecha de ingreso.")

        # Convertimos y validamos monto total
        monto_dec = Decimal(str(monto_total)) if not isinstance(monto_total, Decimal) else monto_total
        if not es_monto_total_valido(monto_dec):
            raise ValueError("El monto total de la reserva no es válido.")

        if not es_id_persona_valido(id_cliente):
            raise ValueError("El ID del cliente asociado no es válido.")

        # 2. Regla de negocio: Validar que el cliente exista y esté activo
        cliente = self.cliente_dao.obtener_cliente_por_id(id_cliente)
        if not cliente or not cliente.get_activo():
            logger.warning(f"Intento de crear reserva para un cliente inexistente o inactivo ID: {id_cliente}")
            raise ValueError(f"El cliente con ID {id_cliente} no existe o no se encuentra activo.")

        # Normalizamos estado si viene como string
        if isinstance(estado, str):
            estado = EstadoReserva(estado.lower())

        if not es_estado_reserva_valido(estado):
            raise ValueError("El estado de la reserva proporcionado no es válido.")

        nueva_reserva = Reserva(
            id_reserva=None,
            fecha_reserva=fecha_reserva,
            fecha_ingreso=fecha_ingreso,
            fecha_salida=fecha_salida,
            estado=estado,
            monto_total=monto_dec,
            activo=True
        )

        id_generado = self.reserva_dao.crear_reserva(nueva_reserva, id_cliente)
        return id_generado

    def obtener_reservas(self) -> list[tuple[Reserva, int] | None]:
        """Obtiene el listado completo de reservas junto con el ID de su cliente."""
        return self.reserva_dao.obtener_reservas()

    def obtener_reserva_por_id(self, id_reserva: int) -> Reserva | None:
        """Busca una reserva específica por su ID."""
        return self.reserva_dao.obtener_reserva_por_id(id_reserva)

    def modificar_reserva(
            self, 
            id_reserva: int, 
            fecha_reserva: date | None = None,
            fecha_ingreso: date | None = None, 
            fecha_salida: date | None = None, 
            estado: EstadoReserva | str | None = None, 
            monto_total: Decimal | float | None = None, 
            id_cliente: int | None = None,
            activo: bool | None = None
    ) -> Reserva | None:
        """Modifica atributos de la reserva aplicando validaciones de coherencia."""
        if fecha_ingreso is not None and not es_fecha_ingreso_valida(fecha_ingreso):
            raise ValueError("La nueva fecha de ingreso no es válida.")

        if fecha_salida is not None and not es_fecha_salida_valida(fecha_salida):
            raise ValueError("La nueva fecha de salida no es válida.")

        monto_dec = None
        if monto_total is not None:
            monto_dec = Decimal(str(monto_total)) if not isinstance(monto_total, Decimal) else monto_total
            if not es_monto_total_valido(monto_dec):
                raise ValueError("El monto total proporcionado no es válido.")

        estado_enum = None
        if estado is not None:
            estado_enum = EstadoReserva(estado.lower()) if isinstance(estado, str) else estado
            if not es_estado_reserva_valido(estado_enum):
                raise ValueError("El estado de reserva proporcionado no es válido.")

        if id_cliente is not None:
            cliente = self.cliente_dao.obtener_cliente_por_id(id_cliente)
            if not cliente or not cliente.get_activo():
                raise ValueError(f"El cliente con ID {id_cliente} no existe o no está activo.")

        return self.reserva_dao.modificar_reserva(
            id_reserva=id_reserva,
            fecha_reserva=fecha_reserva,
            fecha_ingreso=fecha_ingreso,
            fecha_salida=fecha_salida,
            estado=estado_enum,
            monto_total=monto_dec,
            id_cliente=id_cliente,
            activo=activo
        )

    def eliminar_reserva(self, id_reserva: int) -> bool:
        """Realiza la baja lógica de la reserva (activo = False)."""
        return self.reserva_dao.eliminar_reserva(id_reserva)