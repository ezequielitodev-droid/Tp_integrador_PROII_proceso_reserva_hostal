#Imports:

import sys
from pathlib import Path
from dao.db_connection import obtener_conexion

#Paths:

PATH_FOLDER = Path(__file__).resolve().parent

#Constants:

#Moduls:

def ejecutar_archivo(nombre) -> None:

    #Leo todo el archivo que contiene las instrucciones SQL: 
    instrucciones_sql = (PATH_FOLDER / nombre).read_text(encoding="utf-8")

    #Inicio la conexion con la Nube: 
    conexion = obtener_conexion()

    #Guardo el curson para las instruciones:
    cursor = conexion.cursor()

    #Separo las instrucciones y las ejecuto:
    for instruccion in instrucciones_sql.split(";"):
        instruccion = instruccion.strip()
        if instruccion:
            cursor.execute(instruccion)

    #Al haber modificado algo en la DB commiteo: 
    conexion.commit()
    cursor.close()
    conexion.close()


#Ejecucion del archivo:

if __name__ == "__main__":

    nombre = sys.argv[1] if len(sys.argv) > 1 else "schema.sql"
    ejecutar_archivo(nombre)
    print(f"{nombre} ejecutado")