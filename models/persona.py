#Imports:

from abc import ABC
from utils.validators.datavalidators import (
    es_id_persona_valido, 
    es_nombre_valido, 
    es_apellido_valido, 
    es_dni_valido, 
    es_telefono_valido, 
    es_activo_valido
)

#Constants:

#Class:

class Persona(ABC): 

    #Constructor:

    def __init__(
            self, 
            id_persona: int | None, 
            nombre: str, 
            apellido: str, 
            dni: str, 
            telefono: str, 
            activo: bool
    ) -> None: 

        if not es_id_persona_valido(id_persona):
            raise ValueError("Identificador unico invalido...")
        self.__id_persona: int | None = id_persona

        if not es_nombre_valido(nombre): 
            raise ValueError("Nombre invalido...")
        self.__nombre: str = nombre.strip()

        if not es_apellido_valido(apellido): 
            raise ValueError("Apellido invalido...")
        self.__apellido: str = apellido.strip()

        if not es_dni_valido(dni):
            raise ValueError("DNI invalido...")
        self.__dni: str = dni.strip().replace(".", "")

        if not es_telefono_valido(telefono):
            raise ValueError("Telefono invalido...")
        self.__telefono: str = telefono

        if not es_activo_valido(activo):
            raise ValueError("Activo invalido...")
        self.__activo: bool = activo

    #Methods:

    #Getters:--------------------
    
    def get_id_persona(self) -> int | None:
        
        return self.__id_persona

    def get_nombre(self) -> str:

        return self.__nombre

    def get_apellido(self) -> str:

        return self.__apellido

    def get_dni(self) -> str:

        return self.__dni

    def get_telefono(self) -> str:

        return self.__telefono

    def get_activo(self) -> bool:

        return self.__activo

    #Getters:--------------------

    #Setters:--------------------

    def set_nombre(self, nombre: str) -> None:

        if not es_nombre_valido(nombre):
            raise ValueError("Nombre invalido...")
        
        self.__nombre = nombre.strip()

    def set_apellido(self, apellido: str) -> None:

        if not es_apellido_valido(apellido):
            raise ValueError("Apellido invalido...")
        
        self.__apellido = apellido.strip()

    def set_dni(self, dni: str) -> None:

        if not es_dni_valido(dni):
            raise ValueError("DNI invalido...")
        
        self.__dni = dni.strip().replace(".", "")

    def set_telefono(self, telefono: str) -> None:

        if not es_telefono_valido(telefono):
            raise ValueError("Telefono invalido...")
        
        self.__telefono = telefono

    def set_activo(self, activo: bool) -> None:

        if not es_activo_valido(activo):
            raise ValueError("Activo invalido...")
        self.__activo = activo

    #Setters:--------------------