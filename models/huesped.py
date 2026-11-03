#Imports:

from models.persona import Persona

#Constants:

#Class:

class Huesped(Persona):

    #Constructor:

    def __init__(
            self, 
            id_huesped: int | None, 
            nombre: str, 
            apellido: str, 
            dni: str, 
            telefono: str
    ) -> None:

        super().__init__(id_huesped, nombre, apellido, dni, telefono, None)