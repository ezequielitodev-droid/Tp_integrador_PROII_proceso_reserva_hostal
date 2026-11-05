#Imports:

from enum import Enum

#DataTypes: EstadoHabitacion

class EstadoHabitacion(Enum):

    """
        Estados posibles de una habitación: DISPONIBLE | OCUPADA.

        Attributes:
            DISPONIBLE: La habitación está libre y puede asignarse a una reserva.
            OCUPADA: La habitación tiene huéspedes alojados en este momento.
    """

    DISPONIBLE = "disponible"
    OCUPADA = "ocupada"