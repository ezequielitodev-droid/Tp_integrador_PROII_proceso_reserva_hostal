#Imports:

import re
from datetime import date, datetime
from decimal import Decimal
from utils.datatypes.EstadoHabitacion import EstadoHabitacion
from utils.datatypes.EstadoReserva import EstadoReserva

#Constants:

PATRON_CORREO_VALIDO = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")

#Validators:

#Activo:

def es_activo_valido(activo: bool) -> bool:

    return isinstance(activo, bool)

#Personas:-------------------------

def es_id_persona_valido(id_persona: int | None) -> bool:

    """
        Verifica que el identificador de una persona sea válido.

        Se considera válido si es None (persona nueva, todavía sin guardar en
        la base) o si es un entero positivo que entra en una columna INT de
        MySQL.

        Args:
            id_persona (int | None): Identificador a validar.

        Returns:
            bool: True si es None o un int entre 1 y 2147483647, False en caso
            contrario (incluye bool y cualquier tipo que no sea int).

        Examples:
            >>> es_id_persona_valido(None)
            True
            >>> es_id_persona_valido(15)
            True
            >>> es_id_persona_valido(0)
            False
            >>> es_id_persona_valido(True)
            False
    """

    if id_persona is None: return True
    
    return (
        isinstance(id_persona, int)
        and not isinstance(id_persona, bool)
        and 0 < id_persona <= 2147483647
    )

def es_nombre_valido(nombre: str) -> bool:

    """
        Verifica que un nombre sea válido.

        Se considera válido si es un string que contiene al menos un
        carácter distinto de espacio. Los espacios al inicio y al final
        se ignoran.

        Args:
            nombre (str): Nombre a validar.

        Returns:
            bool: True si el nombre es un str no vacío, False en caso
            contrario (incluye el caso en que nombre no sea un str).

        Examples:
            >>> es_nombre_valido("Ezequiel")
            True
            >>> es_nombre_valido("   ")
            False
            >>> es_nombre_valido(123)
            False
    """

    return isinstance(nombre, str) and len(nombre.strip()) > 0

def es_apellido_valido(apellido: str) -> bool:

    """
        Verifica que un apellido sea válido.
    
        Se considera válido si es un string que contiene al menos un
        carácter distinto de espacio. Los espacios al inicio y al final
        se ignoran.
    
        Args:
            apellido (str): Apellido a validar.
    
        Returns:
            bool: True si el apellido es un str no vacío, False en caso
            contrario (incluye el caso en que apellido no sea un str).
    
        Examples:
            >>> es_apellido_valido("Ezequiel")
            True
            >>> es_apellido_valido("   ")
            False
            >>> es_apellido_valido(123)
            False
    """
    
    return isinstance(apellido, str) and len(apellido.strip()) > 0

def es_dni_valido(dni: str) -> bool:

    """
        Verifica que un DNI tenga un formato válido.

        Se considera válido si es un string compuesto únicamente por
        dígitos, con 7 u 8 de largo. Los espacios al inicio y al final,
        y los puntos separadores (por ejemplo "12.345.678"), se ignoran
        al validar.

        Args:
            dni (str): DNI a validar, con o sin puntos.

        Returns:
            bool: True si el DNI cumple el formato, False en caso
            contrario (incluye el caso en que dni no sea un str).

        Examples:
            >>> es_dni_valido("12.345.678")
            True
            >>> es_dni_valido("1234567")
            True
            >>> es_dni_valido("1234")
            False
    """

    if not isinstance(dni, str): return False

    dni = dni.strip().replace(".", "")

    return dni.isdigit() and len(dni) in (7, 8)

def es_telefono_valido(telefono: str) -> bool:

    if not isinstance(telefono, str): return False
        
    return telefono.isascii() and telefono.isdigit() and len(telefono) == 10

def es_correo_valido(correo: str) -> bool:

    if not isinstance(correo, str): return False

    return len(correo) <= 100 and PATRON_CORREO_VALIDO.fullmatch(correo) is not None

#Personas:-------------------------

#Habitaciones:---------------------

def es_id_habitacion_valida(id_habitacion: int | None) -> bool:
       
       if id_habitacion is None: return True

       return (
           isinstance(id_habitacion, int)
           and not isinstance(id_habitacion, bool)
           and id_habitacion > 0
       )

def es_numero_valido(numero: int) -> bool:

    return isinstance(numero, int) and numero >= 1

def es_capacidad_valida(capacidad: int) -> bool:

    return isinstance(capacidad, int) and capacidad in [1, 2, 3, 4]

def es_precio_noche_valido(precio_noche: Decimal) -> bool:

    return (
        isinstance(precio_noche, Decimal) 
        and precio_noche.is_finite()
        and 0 <= precio_noche <= Decimal("99999999.99")
        and precio_noche == precio_noche.quantize(Decimal("0.01"))
    )

def es_estado_valido(estado: EstadoHabitacion) -> bool:

    return isinstance(estado, EstadoHabitacion) 

#Habitaciones:---------------------

#Reservas:-------------------------

def es_id_reserva_valido(id_reserva: int | None) -> bool:

    """
        Verifica que el identificador de una reserva sea válido.

        Se considera válido si es None (reserva nueva, todavía sin guardar
        en la base) o si es un entero positivo que entra en una columna INT
        de MySQL.

        Args:
            id_reserva (int | None): Identificador a validar.

        Returns:
            bool: True si es None o un int entre 1 y 2147483647, False en
            caso contrario (incluye bool y cualquier tipo que no sea int).

        Examples:
            >>> es_id_reserva_valido(None)
                        True
            >>> es_id_reserva_valido(0)
                        False
            >>> es_id_reserva_valido(True)
                        False
    """

    if id_reserva is None: return True

    return (
        isinstance(id_reserva, int)
        and not isinstance(id_reserva, bool)
        and 0 < id_reserva <= 2147483647
    )

def es_fecha_reserva_valida(fecha_reserva: date) -> bool:

    return isinstance(fecha_reserva, date) and not isinstance(fecha_reserva, datetime)

def es_fecha_ingreso_valida(fecha_ingreso: date) -> bool:

    return isinstance(fecha_ingreso, date) and not isinstance(fecha_ingreso, datetime)

def es_fecha_salida_valida(fecha_salida: date) -> bool:

    return isinstance(fecha_salida, date) and not isinstance(fecha_salida, datetime)

def es_rango_fechas_valido(fecha_ingreso: date, fecha_salida: date) -> bool:

    """
        Verifica que la fecha de salida sea posterior a la de ingreso.

        Args:
            fecha_ingreso (date): Fecha de ingreso, ya validada.
            fecha_salida (date): Fecha de salida, ya validada.

        Returns:
            bool: True si fecha_salida es estrictamente mayor que
            fecha_ingreso.

        Examples:
            >>> es_rango_fechas_valido(date(2026, 11, 10), date(2026, 11, 13))
                        True
            >>> es_rango_fechas_valido(date(2026, 11, 10), date(2026, 11, 10))
                        False
    """

    return fecha_salida > fecha_ingreso

def es_estado_reserva_valido(estado: EstadoReserva) -> bool:

    return isinstance(estado, EstadoReserva)

def es_monto_total_valido(monto_total: Decimal) -> bool:

    return (
        isinstance(monto_total, Decimal)
        and monto_total.is_finite()
        and 0 <= monto_total <= Decimal("99999999.99")
        and monto_total == monto_total.quantize(Decimal("0.01"))
    )

#Reservas:-------------------------