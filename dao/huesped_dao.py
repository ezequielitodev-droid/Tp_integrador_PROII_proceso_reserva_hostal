# Imports:
import logging

from dao.db_connection import obtener_conexion
from models.huesped import Huesped
from database.queries import (
    instruccion_crear_huesped, 
    instruccion_obtener_huespedes, 
    instruccion_obtener_huesped_por_id, 
    instruccion_obtener_huesped_por_dni, 
    instruccion_modificar_huesped
)

#Global Variables:

logger = logging.getLogger("dao.huesped_dao")

#Constants:

#Class:

class HuespedDAO:

    #Methods: 

    def crear_huesped(self, huesped: Huesped, conexion_externa = None) -> int | None:

        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        try:
            cursor = conexion.cursor()

            instruccion_sql = instruccion_crear_huesped

            valores = (
                huesped.get_nombre(),
                huesped.get_apellido(),
                huesped.get_dni(),
                huesped.get_telefono(),
                huesped.get_activo()
            )

            cursor.execute(instruccion_sql, valores)
            
            if debe_cerrar:
                conexion.commit()

            id_generado = cursor.lastrowid

            logging.info(f"Huésped creado exitosamente con ID: {id_generado}")

            return id_generado

        except Exception as e:

            logging.error(f"Error al crear el huésped: {e}")

            if debe_cerrar and conexion:
                conexion.rollback()

            return None

        finally:

            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()

    def obtener_huespedes(self, conexion_externa = None) -> list[Huesped | None]:

        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        list_huespedes = []

        try:
            cursor = conexion.cursor()

            instruccion_sql = instruccion_obtener_huespedes
            
            cursor.execute(instruccion_sql)
            resultados = cursor.fetchall()

            for registro in resultados:

                huesped = Huesped(
                    id_huesped=registro[0],  # type: ignore
                    nombre=registro[1],      # type: ignore
                    apellido=registro[2],    # type: ignore
                    dni=registro[3],         # type: ignore
                    telefono=registro[4],    # type: ignore
                    activo=bool(registro[5]) # type: ignore
                )

                list_huespedes.append(huesped)

            logging.info(f"Se obtuvieron {len(list_huespedes)} huéspedes exitosamente.")

            return list_huespedes
            
        except Exception as e: 

            logging.error(f"Error al obtener los huéspedes: {e}")
            return []

        finally:

            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()

    def obtener_huesped_por_id(self, id_huesped: int, conexion_externa = None) -> Huesped | None:

        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        try:
            cursor = conexion.cursor()

            instruccion_sql = instruccion_obtener_huesped_por_id
            
            valor = (id_huesped, )

            cursor.execute(instruccion_sql, valor)
            resultado = cursor.fetchone()

            if not resultado:

                logging.warning(f"No se encontró ningún huésped con el ID: {id_huesped}")

                return None

            huesped = Huesped(
                id_huesped=resultado[0],  # type: ignore
                nombre=resultado[1],      # type: ignore
                apellido=resultado[2],    # type: ignore
                dni=resultado[3],         # type: ignore
                telefono=resultado[4],    # type: ignore
                activo=bool(resultado[5]) # type: ignore
            )

            logging.info(f"Huésped con ID {id_huesped} obtenido exitosamente.")

            return huesped

        except Exception as e:

            logging.error(f"Error al obtener el huésped por ID: {e}")

            return None

        finally:

            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()

    def obtener_huesped_por_dni(self, dni: str, conexion_externa = None) -> Huesped | None:

        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        try:

            cursor = conexion.cursor()
            dni_limpio = dni.strip().replace(".", "")
            
            instruccion_sql = instruccion_obtener_huesped_por_dni
            cursor.execute(instruccion_sql, (dni_limpio,))
            
            resultado = cursor.fetchone()
            if not resultado:
                return None

            return Huesped(
                id_huesped=resultado[0],
                nombre=resultado[1],
                apellido=resultado[2],
                dni=resultado[3],
                telefono=resultado[4],
                activo=bool(resultado[5])
            )
        except Exception as e:

            logging.error(f"Error al buscar huésped por DNI: {e}")

            return None
        
        finally:

            if cursor: cursor.close()
            if debe_cerrar: conexion.close()

    def modificar_huesped(
            self, 
            id_huesped: int, 
            nombre: str | None = None, 
            apellido: str | None = None, 
            dni: str | None = None, 
            telefono: str | None = None, 
            activo: bool | None = None,
            conexion_externa = None
    ) -> Huesped | None:

        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        try:
            cursor = conexion.cursor()

            instruccion_sql = instruccion_modificar_huesped

            valores = (nombre, apellido, dni, telefono, activo, id_huesped)

            cursor.execute(instruccion_sql, valores)
            
            if debe_cerrar:
                conexion.commit()

            if cursor.rowcount == 0:

                logging.warning(f"No se encontró ningún huésped con el ID: {id_huesped} para modificar.")

                return None

            logging.info(f"Huésped con ID {id_huesped} modificado exitosamente.")
            
            return self.obtener_huesped_por_id(id_huesped, conexion_externa=conexion)

        except Exception as e:

            logging.error(f"Error al modificar el huésped: {e}")

            if debe_cerrar and conexion: 
                conexion.rollback()

            return None

        finally:

            if cursor:
                cursor.close()

            if debe_cerrar and conexion:
                conexion.close()
    
    def eliminar_huesped(self, id_huesped: int, conexion_externa = None) -> bool:
        
        """
            Realiza una baja lógica del huésped cambiando su estado 'activo' a False,
            preservando el historial de reservas y la integridad de la base de datos.
        """
        try:
            
            huesped_modificado = self.modificar_huesped(
                id_huesped=id_huesped, 
                activo=False,
                conexion_externa=conexion_externa
            )

            if huesped_modificado is None:

                logging.warning(f"No se encontró ningún huésped con el ID: {id_huesped} para dar de baja.")

                return False

            logging.info(f"Huésped con ID {id_huesped} dado de baja lógica (activo = False) exitosamente.")

            return True

        except Exception as e:

            logging.error(f"Error crítico al intentar dar de baja al huésped con ID {id_huesped}: {e}")
            
            return False