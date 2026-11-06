#Imports

from utils.validators.datavalidators import(
    es_id_habitacion_valida, 
    es_numero_valido, 
    es_capacidad_valida,
    es_precio_noche_valido,
    es_estado_valido, 
    es_activo_valido
)
from utils.datatypes.EstadoHabitacion import EstadoHabitacion
from decimal import Decimal

#Constants

#Class

class Habitacion():
    
    def __init__(
        self,
        id_habitacion: int | None, 
        numero: int, 
        capacidad: int,
        precio_noche: Decimal, 
        estado: EstadoHabitacion, 
        activo: bool
    ) -> None:
    
        if not es_id_habitacion_valida(id_habitacion):
            raise ValueError("Id habitación inválido...")
        self.__id_habitacion: int | None = id_habitacion
        
        if not es_numero_valido(numero):
            raise ValueError("Número habitación inválido...")
        self.__numero: int = numero

        if not es_capacidad_valida(capacidad):
            raise ValueError("Capacidad habitación inválida...")
        self.__capacidad: int = capacidad

        if not es_precio_noche_valido(precio_noche):
            raise ValueError("Precio por noche habitación inváido...")
        self.__precio_noche: Decimal = precio_noche

        if not es_estado_valido(estado):
            raise ValueError("Estado habitación inválido...")
        self.__estado: EstadoHabitacion = estado

        if not es_activo_valido(activo):
            raise ValueError("Activo inválido...")
        self.__activo: bool = activo

    #Getters:--------------------
    
    def get_id_habitacion(self) -> int | None:
        
        return self.__id_habitacion

    def get_numero(self) -> int:
        
        return self.__numero

    def get_capacidad(self) -> int:
        
        return self.__capacidad

    def get_precio_noche(self) -> Decimal:
        
        return self.__precio_noche

    def get_estado(self) -> EstadoHabitacion:
        
        return self.__estado

    def get_activo(self) -> bool:

        return self.__activo
    
    #Getters:--------------------

    #Setters:--------------------

    def set_id_habitacion(self, id_habitacion: int) -> None:

        if self.__id_habitacion is not None:
            raise ValueError("El identificador ya fue asignado...")
        
        if id_habitacion is None or not es_id_habitacion_valida(id_habitacion):
            raise ValueError("Id habitación inválido...")
        
        self.__id_habitacion = id_habitacion

    def set_numero(self, numero: int) -> None:

        if not es_numero_valido(numero):
            raise ValueError("Número habitación inválido...")
        
        self.__numero = numero

    def set_capacidad(self, capacidad: int) -> None:

        if not es_capacidad_valida(capacidad):
            raise ValueError("Capacidad habitación inválida...")
        
        self.__capacidad = capacidad

    def set_precio_noche(self, precio_noche: Decimal) -> None:

        if not es_precio_noche_valido(precio_noche):
            raise ValueError("Precio por noche habitación inválido...")
        
        self.__precio_noche = precio_noche

    def set_estado(self, estado: EstadoHabitacion) -> None:

        if not es_estado_valido(estado):
            raise ValueError("Estado habitación inválido...")
        
        self.__estado = estado

    def set_activo(self, activo: bool) -> None:

        if not es_activo_valido(activo):
            raise ValueError("Activo inválido...")
        
        self.__activo = activo
    
    #Setters:--------------------