#Imports:

import re

#Constants:

PATRON_CORREO_VALIDO = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")

#Validators:

#Personas:-------------------------

def es_id_persona_valido(nombre: int) -> bool:

    return nombre is not None and isinstance(nombre, int)

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
            contrario (incluye el caso en que `nombre` no sea un str).

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
            contrario (incluye el caso en que `apellido` no sea un str).
    
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
            contrario (incluye el caso en que `dni` no sea un str).

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

