#Imports:

from enum import Enum

#DataTypes: EstadoReserva

class EstadoReserva(Enum):

    """
        Estados posibles de una reserva: RESERVADA | CANCELADA.

        Attributes:
            RESERVADA: La reserva está vigente.
            CANCELADA: La reserva fue cancelada. No se elimina, se conserva
                con este estado.
    """

    RESERVADA = "reservada"
    CANCELADA = "cancelada"