import json
import logging
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from dao.db_connection import obtener_conexion

logger = logging.getLogger("backups.backup_manager")

class BackupManager:
    """Administrador para generar copias de seguridad (backup) y restaurar la base de datos en formato JSON."""

    @staticmethod
    def _serializador_personalizado(obj):
        """Convierte objetos que JSON nativamente no entiende (como Date, Decimal, Datetime) a formatos serializables."""
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Tipo de objeto {type(obj)} no es serializable en JSON")

    @classmethod
    def generar_copia_seguridad(cls, ruta_destino: str | Path | None = None) -> str | None:
        """
        Extrae todas las tablas de la base de datos respetando su estructura y las guarda en un archivo JSON.
        Retorna la ruta absoluta del archivo generado o None si ocurre un error.
        """
        conexion = obtener_conexion()
        if not conexion:
            logger.error("No se pudo establecer conexión con la base de datos para generar la copia de seguridad.")
            return None

        cursor = conexion.cursor(dictionary=True)
        datos_backup = {
            "version_sistema": "1.0",
            "fecha_copia": datetime.now().isoformat(),
            "tablas": {}
        }

        # Orden estricto de tablas para mantener la consistencia relacional
        tablas = [
            "clientes",
            "habitaciones",
            "huespedes",
            "reservas",
            "reservas_x_huespedes",
            "reservas_x_habitaciones"
        ]

        try:
            for tabla in tablas:
                cursor.execute(f"SELECT * FROM {tabla}")
                registros = cursor.fetchall()
                datos_backup["tablas"][tabla] = registros

            # Definir ruta por defecto si no se pasa una
            if not ruta_destino:
                directorio_actual = Path(__file__).resolve().parent / "storage"
                directorio_actual.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                ruta_destino = directorio_actual / f"backup_hostal_{timestamp}.json"
            else:
                ruta_destino = Path(ruta_destino)

            with open(ruta_destino, "w", encoding="utf-8") as archivo_json:
                json.dump(datos_backup, archivo_json, ensure_ascii=False, indent=4, default=cls._serializador_personalizado)

            logger.info(f"Copia de seguridad generada con éxito en: {ruta_destino}")
            return str(ruta_destino)

        except Exception as e:
            logger.error(f"Error crítico al generar la copia de seguridad: {e}")
            return None

        finally:
            cursor.close()
            conexion.close()

    @classmethod
    def restaurar_base_datos(cls, ruta_archivo: str | Path) -> bool:
        """
        Lee un archivo JSON de respaldo y reconstruye la base de datos completa.
        Desactiva temporalmente las restricciones de claves foráneas para evitar conflictos de orden.
        Retorna True si la restauración fue exitosa, False en caso contrario.
        """
        ruta_archivo = Path(ruta_archivo)
        if not ruta_archivo.exists():
            logger.error(f"El archivo de respaldo especificado no existe: {ruta_archivo}")
            return False

        try:
            with open(ruta_archivo, "r", encoding="utf-8") as archivo_json:
                contenido = json.load(archivo_json)
        except Exception as e:
            logger.error(f"Error al leer o parsear el archivo JSON de respaldo: {e}")
            return False

        tablas_datos = contenido.get("tablas", {})
        if not tablas_datos:
            logger.error("El archivo JSON no contiene la estructura de tablas esperada.")
            return False

        conexion = obtener_conexion()
        if not conexion:
            logger.error("No se pudo establecer conexión con la base de datos para realizar la restauración.")
            return False

        cursor = conexion.cursor()

        # Orden inverso para vaciar las tablas sin romper restricciones de FK
        orden_vaciado = [
            "reservas_x_habitaciones",
            "reservas_x_huespedes",
            "reservas",
            "huespedes",
            "habitaciones",
            "clientes"
        ]

        # Orden normal para volver a insertar los datos respetando las dependencias
        orden_insercion = [
            "clientes",
            "habitaciones",
            "huespedes",
            "reservas",
            "reservas_x_huespedes",
            "reservas_x_habitaciones"
        ]

        try:
            # Desactivar validación de claves foráneas y limpiar la BD
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            
            for tabla in orden_vaciado:
                if tabla in tablas_datos:
                    cursor.execute(f"DELETE FROM {tabla}")

            # Insertar los datos tabla por tabla
            for tabla in orden_insercion:
                registros = tablas_datos.get(tabla, [])
                if not registros:
                    continue

                for fila in registros:
                    columnas = list(fila.keys())
                    valores = list(fila.values())

                    placeholders = ", ".join(["%s"] * len(columnas))
                    cols_str = ", ".join(columnas)
                    
                    query = f"INSERT INTO {tabla} ({cols_str}) VALUES ({placeholders})"
                    cursor.execute(query, valores)

            conexion.commit()
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            logger.info("Base de datos restaurada exitosamente desde el archivo JSON.")
            return True

        except Exception as e:
            conexion.rollback()
            try:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            except Exception:
                pass
            logger.error(f"Error crítico durante la restauración de la base de datos: {e}")
            return False

        finally:
            cursor.close()
            conexion.close()