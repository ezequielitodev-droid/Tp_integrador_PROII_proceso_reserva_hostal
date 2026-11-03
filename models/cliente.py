#Imports:

from models.persona import Persona

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
            correo: str
    ) -> None:

        super().__init__(id_cliente, nombre, apellido, dni, telefono, correo)