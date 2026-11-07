# Imports:

import logging
from decimal import Decimal
from models.habitacion import Habitacion
from dao.habitacion_dao import HabitacionDAO
from utils.datatypes.EstadoHabitacion import EstadoHabitacion
from utils.validators.datavalidators import (
    es_numero_valido, 
    es_capacidad_valida, 
    es_precio_noche_valido, 
    es_estado_valido
)

# Constants:

# Global Variables:

logger = logging.getLogger(__name__)

# Class:

class HabitacionService:

    # Constructor:

    def __init__(
            self, 
            habitacion_dao: HabitacionDAO | None = None
    ):
        # Inyectamos la dependencia del DAO de habitaciones
        self.habitacion_dao = habitacion_dao or HabitacionDAO()

    # Métodos estratégicos:

    def crear_habitacion(
            self, 
            numero: int, 
            capacidad: int, 
            precio_noche: Decimal | float, 
            estado: EstadoHabitacion | str = EstadoHabitacion.DISPONIBLE
    ) -> int | None:
        """
        Aplica las reglas de negocio utilizando los validadores del sistema.
        """
        # 1. Validar número usando tu validador
        if not es_numero_valido(numero):
            raise ValueError(f"El número de habitación '{numero}' no es válido (debe ser un entero >= 1).")

        # 2. Validar capacidad usando tu validador (acepta [1, 2, 3, 4])
        if not es_capacidad_valida(capacidad):
            raise ValueError(f"La capacidad '{capacidad}' no es válida (debe ser 1, 2, 3 o 4).")

        # Convertimos a Decimal si viene como float para usar tu validador de precio
        precio_dec = Decimal(str(precio_noche)) if not isinstance(precio_noche, Decimal) else precio_noche
        
        if not es_precio_noche_valido(precio_dec):
            raise ValueError("El precio por noche no es válido (formato decimal incorrecto o fuera de rango).")

        # Verificamos duplicados en la base...
        habitaciones_existentes = self.habitacion_dao.obtener_habitaciones()
        for hab in habitaciones_existentes:
            if hab and hab.get_numero() == numero and hab.get_activo():
                logger.warning(f"Intento de registrar habitación duplicada con número: {numero}")
                raise ValueError(f"Ya existe una habitación activa con el número {numero}")

        # Normalizamos estado
        if isinstance(estado, str):
            estado = EstadoHabitacion(estado.lower())

        if not es_estado_valido(estado):
            raise ValueError("El estado de la habitación proporcionado no es válido.")

        nueva_habitacion = Habitacion(
            id_habitacion=None,
            numero=numero,
            capacidad=capacidad,
            precio_noche=precio_dec,
            estado=estado,
            activo=True
        )

        return self.habitacion_dao.crear_habitacion(nueva_habitacion)

    def obtener_habitaciones(self) -> list[Habitacion | None]:
        """Obtiene el listado completo de habitaciones."""
        return self.habitacion_dao.obtener_habitaciones()

    def obtener_habitacion_por_id(self, id_habitacion: int) -> Habitacion | None:
        """Busca una habitación específica por su ID."""
        return self.habitacion_dao.obtener_habitacion_por_id(id_habitacion)

    def modificar_habitacion(
            self, 
            id_habitacion: int, 
            numero: int | None = None, 
            capacidad: int | None = None, 
            precio_noche: Decimal | float | None = None, 
            estado: EstadoHabitacion | str | None = None, 
            activo: bool | None = None
    ) -> Habitacion | None:
        """Modifica los atributos de una habitación aplicando validaciones opcionales."""
        if capacidad is not None and not es_capacidad_valida(capacidad):
            raise ValueError("La capacidad proporcionada no es válida.")

        precio_dec = None
        if precio_noche is not None:
            precio_dec = Decimal(str(precio_noche)) if not isinstance(precio_noche, Decimal) else precio_noche
            if not es_precio_noche_valido(precio_dec):
                raise ValueError("El precio por noche no es válido.")

        estado_enum = None
        if estado is not None:
            estado_enum = EstadoHabitacion(estado.lower()) if isinstance(estado, str) else estado
            if not es_estado_valido(estado_enum):
                raise ValueError("El estado proporcionado no es válido.")

        return self.habitacion_dao.modificar_habitacion(
            id_habitacion=id_habitacion,
            numero=numero,
            capacidad=capacidad,
            precio_noche=precio_dec,
            estado=estado_enum,
            activo=activo
        )

    def eliminar_habitacion(self, id_habitacion: int) -> bool:
        """Realiza la baja lógica de la habitación (activo = False)."""
        return self.habitacion_dao.eliminar_habitacion(id_habitacion)