#Imports

from datetime import date
from decimal import Decimal
from utils.datatypes.EstadoReserva import EstadoReserva
from utils.validators.datavalidators import (
    es_id_reserva_valido,
    es_fecha_reserva_valida,
    es_fecha_ingreso_valida,
    es_fecha_salida_valida,
    es_rango_fechas_valido,
    es_estado_reserva_valido,
    es_monto_total_valido
)

#Constants

#Class

class Reserva():

    def __init__(
        self, 
        id_reserva: int | None, 
        fecha_reserva: date, 
        fecha_ingreso: date, 
        fecha_salida: date, 
        estado: EstadoReserva, 
        monto_total: Decimal 
    ) -> None:

        if not es_id_reserva_valido(id_reserva):
            raise ValueError("Id reserva inválido...")
        self.__id_reserva: int | None = id_reserva

        if not es_fecha_reserva_valida(fecha_reserva):
            raise ValueError("Fecha de reserva inválida...")
        self.__fecha_reserva: date = fecha_reserva

        if not es_fecha_ingreso_valida(fecha_ingreso):
            raise ValueError("Fecha de ingreso inválida...")
        self.__fecha_ingreso: date = fecha_ingreso

        if not es_fecha_salida_valida(fecha_salida):
            raise ValueError("Fecha de salida inválida...")
        self.__fecha_salida: date = fecha_salida

        if not es_rango_fechas_valido(fecha_ingreso, fecha_salida):
            raise ValueError("La fecha de salida debe ser posterior a la de ingreso...")

        if not es_estado_reserva_valido(estado):
            raise ValueError("Estado reserva inválido...")
        self.__estado: EstadoReserva = estado

        if not es_monto_total_valido(monto_total):
            raise ValueError("Monto total inválido...")
        self.__monto_total: Decimal = monto_total

    #Getters:-------------------

    def get_id_reserva(self) -> int | None:
        
        return self.__id_reserva

    def get_fecha_reserva(self) -> date:
        
        return self.__fecha_reserva

    def get_fecha_ingreso(self) -> date:
        
        return self.__fecha_ingreso

    def get_fecha_salida(self) -> date:
        
        return self.__fecha_salida

    def get_estado(self) -> EstadoReserva:
        
        return self.__estado

    def get_monto_total(self) -> Decimal:
        
        return self.__monto_total

    #Getters:-------------------
    
    #Setters:-------------------

    def set_id_reserva(self, id_reserva: int) -> None:

        if self.__id_reserva is not None:
            raise ValueError("El identificador ya fue asignado...")
        
        if id_reserva is None or not es_id_reserva_valido(id_reserva):
            raise ValueError("Id reserva inválido...")
        
        self.__id_reserva = id_reserva

    def set_fechas(self, fecha_ingreso: date, fecha_salida: date) -> None:

        if not es_fecha_ingreso_valida(fecha_ingreso):
            raise ValueError("Fecha de ingreso inválida...")
        
        if not es_fecha_salida_valida(fecha_salida):
            raise ValueError("Fecha de salida inválida...")
        
        if not es_rango_fechas_valido(fecha_ingreso, fecha_salida):
            raise ValueError("La fecha de salida debe ser posterior a la de ingreso...")
        
        self.__fecha_ingreso = fecha_ingreso
        self.__fecha_salida = fecha_salida

    def set_fecha_ingreso(self, fecha_ingreso: date) -> None:

        self.set_fechas(fecha_ingreso, self.__fecha_salida)

    def set_fecha_salida(self, fecha_salida: date) -> None:

        self.set_fechas(self.__fecha_ingreso, fecha_salida)

    def set_estado(self, estado: EstadoReserva) -> None:

        if not es_estado_reserva_valido(estado):
            raise ValueError("Estado reserva inválido...")
        
        if self.__estado is EstadoReserva.CANCELADA and estado is not EstadoReserva.CANCELADA:
            raise ValueError("Una reserva cancelada no puede reactivarse...")
        
        self.__estado = estado

    def set_monto_total(self, monto_total: Decimal) -> None:

        if not es_monto_total_valido(monto_total):
            raise ValueError("Monto total inválido...")
        
        self.__monto_total = monto_total
    
    #Setters:-------------------