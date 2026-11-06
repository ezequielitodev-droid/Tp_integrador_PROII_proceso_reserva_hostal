#Imports:

from models.persona import Persona
from utils.validators.datavalidators import es_correo_valido

#Constants:

#Class:

class Cliente(Persona):

    #Constructor:

    def __init__(
            self, 
            id_cliente: int | None, 
            nombre: str, 
            apellido: str, 
            dni: str, 
            telefono: str, 
            correo: str, 
            activo: bool
    ) -> None:

        super().__init__(id_cliente, nombre, apellido, dni, telefono, activo)

        if not es_correo_valido(correo):
            raise ValueError("Correo invalido...")
        self.__correo: str = correo

    #Getters:--------------------

    def get_correo(self) -> str:
        return self.__correo
    
    #Getters:--------------------

    #Setters:--------------------
    
    def set_correo(self, correo: str) -> None:
        if not es_correo_valido(correo):
            raise ValueError("Correo invalido...")
        self.__correo = correo
    
    #Setters:--------------------