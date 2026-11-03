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

def obtener_conexion():
    return mysql.connector.connect(
        host = os.getenv("DB_HOST"), 
        port = int(os.getenv("DB_PORT")), 
        user = os.getenv("DB_USER"), 
        password = os.getenv("DB_PASSWORD"), 
        database = os.getenv("DB_NAME"), 
        ssl_ca = str(PATH_SSL_CA)
    )


#Prueba conexion

if __name__ == "__main__":
    conexion = obtener_conexion()
    print("Conectado: ", conexion.is_connected())
    conexion.close()