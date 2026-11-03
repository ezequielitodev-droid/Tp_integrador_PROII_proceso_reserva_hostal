#Imports:

from abc import ABC
from utils.validators.datavalidators import (
    es_id_persona_valido, 
    es_nombre_valido, 
    es_apellido_valido, 
    es_dni_valido, 
    es_telefono_valido, 
    es_correo_valido
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
            correo: str
    ) -> None: 

        if not es_id_persona_valido(id_persona):
            raise ValueError("Identificador unico invalido...")
        self.__id_persona: int = id_persona

        if not es_nombre_valido(nombre): 
            raise ValueError("Nombre invalido...")
        self.__nombre: str = nombre

        if not es_apellido_valido(apellido): 
            raise ValueError("Apellido invalido...")
        self.__apellido: str = apellido

        if not es_dni_valido(dni):
            raise ValueError("DNI invalido...")
        self.__dni: str = dni

        if not es_telefono_valido(telefono):
            raise ValueError("Telefono invalido...")
        self.__telefono: str = telefono

        if not es_correo_valido(correo): 
            raise ValueError("Correo invalido...")
        self.__correo = correo

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

    def get_correo(self) -> str:
        
        return self.__correo

    #Getters:--------------------