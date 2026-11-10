# Imports:

import sys
import os
from pathlib import Path

from dotenv import load_dotenv
from mysql.connector import pooling

# Constants:

TAMANO_POOL = 2

# Paths:

PATH_SSL_CA = Path(__file__).resolve().parent.parent / "certs" / "ca.pem"

# Global Configs:

load_dotenv()

_pool: pooling.MySQLConnectionPool | None = None


# Modules:

def obtener_ruta_recurso(relativo: str) -> Path:
    """Obtiene la ruta absoluta de un recurso, compatible con ejecución normal y PyInstaller."""
    # Usamos getattr para que Pylance no intente buscar un atributo estático que solo crea PyInstaller
    base_path = getattr(sys, '_MEIPASS', None)
    
    if base_path:
        return Path(base_path) / relativo
    return Path(__file__).resolve().parent.parent / relativo

def _leer_variable(nombre: str) -> str:

    valor = os.getenv(nombre)

    if valor is None or valor.strip() == "":
        raise RuntimeError(f"Falta la variable de entorno {nombre}. Revisá el archivo .env")
    
    return valor


def _obtener_pool() -> pooling.MySQLConnectionPool:

    global _pool

    # ANTES (daba error al compilar porque buscaba una ruta física relativa al archivo)
    # ruta_cert = Path(__file__).resolve().parent.parent / "certs" / "ca.pem"

    # AHORA (funciona tanto en desarrollo como compilado)
    ruta_cert = obtener_ruta_recurso("certs/ca.pem")

    if _pool is None:

        _pool = pooling.MySQLConnectionPool(
            pool_name="hostal_pool",
            pool_size=TAMANO_POOL,
            pool_reset_session=False,
            host=_leer_variable("DB_HOST"),
            port=int(_leer_variable("DB_PORT")),
            user=_leer_variable("DB_USER"),
            password=_leer_variable("DB_PASSWORD"),
            database=_leer_variable("DB_NAME"),
            ssl_ca=str(ruta_cert),
            connection_timeout=10,
        )

    return _pool


def obtener_conexion():

    """
        Devuelve una conexión reutilizable del pool.

        El pool se crea la primera vez que se llama a esta función, y no al
        importar el módulo. Al llamar a close() sobre la conexión devuelta, no se
        cierra: vuelve al pool para que otra operación la reutilice.
    """
    return _obtener_pool().get_connection()


# Prueba conexion

if __name__ == "__main__":
    conexion = obtener_conexion()
    print("Conectado: ", conexion.is_connected())
    conexion.close()