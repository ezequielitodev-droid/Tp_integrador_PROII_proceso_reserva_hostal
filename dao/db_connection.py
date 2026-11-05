#Imports: 

import os
import mysql.connector
import dotenv
from pathlib import Path
from dotenv import load_dotenv

#Constants: 

#Paths: 
PATH_SSL_CA = Path(__file__).resolve().parent.parent / "certs" / "ca.pem"

#Global Configs: 

load_dotenv()

#Moduls: 

def _leer_variable(nombre: str) -> str:
    
    valor = os.getenv(nombre)
    if valor is None or valor.strip() == "":
        raise RuntimeError(f"Falta la variable de entorno {nombre}. Revisá el archivo .env")
    
    return valor

def obtener_conexion():
    return mysql.connector.connect(
        host=_leer_variable("DB_HOST"),
        port=int(_leer_variable("DB_PORT")),
        user=_leer_variable("DB_USER"),
        password=_leer_variable("DB_PASSWORD"),
        database=_leer_variable("DB_NAME"),
        ssl_ca=str(PATH_SSL_CA)
    )


#Prueba conexion

if __name__ == "__main__":
    conexion = obtener_conexion()
    print("Conectado: ", conexion.is_connected())
    conexion.close()