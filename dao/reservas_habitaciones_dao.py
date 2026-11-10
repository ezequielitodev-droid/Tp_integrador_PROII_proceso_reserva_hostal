# Imports:
import logging

from dao.db_connection import obtener_conexion
from models.habitacion import Habitacion
from utils.datatypes.EstadoHabitacion import EstadoHabitacion
from database.queries import (
    instruccion_asociar_habitacion_reserva,
    instruccion_obtener_habitaciones_por_reserva,
    instruccion_eliminar_asociacion_reserva_habitacion
)

# Global Variables:

logger = logging.getLogger("dao.reservas_habitaciones_dao")

# Constants:

# Class:

class ReservasHabitacionesDAO:

    # Methods:

    def asociar_habitacion_a_reserva(
            self, 
            id_reserva: int, 
            id_habitacion: int, 
            conexion_externa = None
    ) -> bool:

        """
            Asocia una habitación a una reserva específica en la tabla intermedia.
        """
        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        try:
            cursor = conexion.cursor()
            instruccion_sql = instruccion_asociar_habitacion_reserva

            valores = (id_reserva, id_habitacion)
            cursor.execute(instruccion_sql, valores)

            if debe_cerrar:
                conexion.commit()

            logging.info(f"Habitación ID {id_habitacion} asociada exitosamente a la reserva ID {id_reserva}.")
            return True

        except Exception as e:
            logging.error(f"Error al asociar habitación {id_habitacion} a la reserva {id_reserva}: {e}")
            if debe_cerrar and conexion:
                conexion.rollback()
            return False

        finally:
            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()

    def obtener_habitaciones_por_reserva(self, id_reserva: int, conexion_externa = None) -> list[Habitacion]:

        """
            Retorna una lista con todos los objetos Habitacion asociados a una reserva específica.
        """
        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        lista_habitaciones = []

        try:
            cursor = conexion.cursor()
            instruccion_sql = instruccion_obtener_habitaciones_por_reserva
            
            cursor.execute(instruccion_sql, (id_reserva,))
            resultados = cursor.fetchall()

            for registro in resultados:
                habitacion = Habitacion(
                    id_habitacion=registro[0],                       # type: ignore
                    numero=registro[1],                              # type: ignore
                    capacidad=registro[2],                           # type: ignore
                    precio_noche=registro[3],                        # type: ignore
                    estado=EstadoHabitacion(str(registro[4]).lower()), # type: ignore
                    activo=bool(registro[5])                         # type: ignore
                )
                lista_habitaciones.append(habitacion)

            logging.info(f"Se obtuvieron {len(lista_habitaciones)} habitaciones para la reserva ID {id_reserva}.")
            return lista_habitaciones
            
        except Exception as e: 
            logging.error(f"Error al obtener habitaciones de la reserva ID {id_reserva}: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()

    def eliminar_asociacion(self, id_reserva: int, id_habitacion: int, conexion_externa = None) -> bool:
        
        """
            Elimina el vínculo (desasocia) entre una reserva y una habitación en la tabla intermedia.
        """
        conexion = conexion_externs = conexion_externa or obtener_conexion() # type: ignore
        debe_cerrar = conexion_externa is None
        cursor = None

        try:
            cursor = conexion.cursor()
            instruccion_sql = instruccion_eliminar_asociacion_reserva_habitacion

            valores = (id_reserva, id_habitacion)
            cursor.execute(instruccion_sql, valores)
            
            if debe_cerrar:
                conexion.commit()

            if cursor.rowcount == 0:
                logging.warning(f"No se encontró la asociación entre la reserva {id_reserva} y la habitación {id_habitacion}.")
                return False

            logging.info(f"Asociación eliminada con éxito entre reserva {id_reserva} y habitación {id_habitacion}.")
            return True

        except Exception as e:
            logging.error(f"Error al eliminar asociación de habitación: {e}")
            if debe_cerrar and conexion:
                conexion.rollback()
            return False

        finally:
            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()