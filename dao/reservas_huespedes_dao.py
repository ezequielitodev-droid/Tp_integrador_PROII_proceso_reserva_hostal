# Imports:
import logging

from dao.db_connection import obtener_conexion
from models.huesped import Huesped
from database.queries import (
    instruccion_asociar_huesped_reserva,
    instruccion_obtener_huespedes_por_reserva,
    instruccion_eliminar_asociacion_reserva_huesped
)

# Global Variables:

logger = logging.getLogger(__name__)

# Constants:

# Class:

class ReservasHuespedesDAO:

    #Methods:

    def asociar_huesped_a_reserva(
            self, 
            id_reserva: int, 
            id_huesped: int, 
            conexion_externa = None
    ) -> bool:

        """
            Asocia un huésped a una reserva específica en la tabla intermedia.
        """

        #Inyeccion de la conexion:
        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        try:

            cursor = conexion.cursor()

            instruccion_sql = instruccion_asociar_huesped_reserva

            valores = (id_reserva, id_huesped)
            cursor.execute(instruccion_sql, valores)

            if debe_cerrar:
                conexion.commit()

            logging.info(f"Huésped ID {id_huesped} asociado exitosamente a la reserva ID {id_reserva}.")
            return True

        except Exception as e:
            logging.error(f"Error al asociar huésped {id_huesped} a la reserva {id_reserva}: {e}")
            if debe_cerrar and conexion:
                conexion.rollback()
            return False

        finally:
            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()

    def obtener_huespedes_por_reserva(self, id_reserva: int, conexion_externa = None) -> list[Huesped]:

        """
            Retorna una lista con todos los objetos Huesped asociados a una reserva específica.
        """
        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        lista_huespedes = []

        try:
            cursor = conexion.cursor()
            instruccion_sql = instruccion_obtener_huespedes_por_reserva
            
            cursor.execute(instruccion_sql, (id_reserva,))
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
                lista_huespedes.append(huesped)

            logging.info(f"Se obtuvieron {len(lista_huespedes)} huéspedes para la reserva ID {id_reserva}.")
            return lista_huespedes
            
        except Exception as e: 
            logging.error(f"Error al obtener huéspedes de la reserva ID {id_reserva}: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()


    def eliminar_asociacion(self, id_reserva: int, id_huesped: int, conexion_externa = None) -> bool:
        
        """
            Elimina el vínculo entre una reserva y un huésped en la tabla intermedia.
        """
        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        try:
            cursor = conexion.cursor()
            instruccion_sql = instruccion_eliminar_asociacion_reserva_huesped

            valores = (id_reserva, id_huesped)
            cursor.execute(instruccion_sql, valores)
            
            if debe_cerrar:
                conexion.commit()

            if cursor.rowcount == 0:
                logging.warning(f"No se encontró la asociación entre la reserva {id_reserva} y el huésped {id_huesped}.")
                return False

            logging.info(f"Asociación eliminada con éxito entre reserva {id_reserva} y huésped {id_huesped}.")
            return True

        except Exception as e:
            logging.error(f"Error al eliminar asociación: {e}")
            if debe_cerrar and conexion:
                conexion.rollback()
            return False

        finally:
            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()