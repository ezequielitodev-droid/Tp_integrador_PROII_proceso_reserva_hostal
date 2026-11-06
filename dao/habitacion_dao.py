# Imports:
import logging

from dao.db_connection import obtener_conexion
from models.habitacion import Habitacion
from utils.datatypes.EstadoHabitacion import EstadoHabitacion
from decimal import Decimal
from database.queries import (
    instruccion_crear_habitacion, 
    instruccion_obtener_habitaciones, 
    instruccion_obtener_habitacion_por_id, 
    instruccion_modificar_habitacion
)

#Global Variables:

logger = logging.getLogger(__name__)

#Constants:

#Class:

class HabitacionDAO:

    #Methods: 

    def crear_habitacion(self, habitacion: Habitacion, conexion_externa = None) -> int | None:

        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        try:
            cursor = conexion.cursor()

            instruccion_sql = instruccion_crear_habitacion

            # Convertimos el Enum de estado a su valor string o primitivo esperado por la BD si corresponde
            estado_valor = habitacion.get_estado().value if hasattr(habitacion.get_estado(), "value") else habitacion.get_estado()

            valores = (
                habitacion.get_numero(),
                habitacion.get_capacidad(),
                float(habitacion.get_precio_noche()),  # Decimal de Python mapeado a float/decimal para MySQL
                estado_valor,
                habitacion.get_activo()
            )

            cursor.execute(instruccion_sql, valores)
            
            if debe_cerrar:
                conexion.commit()

            id_generado = cursor.lastrowid

            logging.info(f"Habitación creada exitosamente con ID: {id_generado}")

            return id_generado

        except Exception as e:

            logging.error(f"Error al crear la habitación: {e}")

            if debe_cerrar and conexion:
                conexion.rollback()

            return None

        finally:

            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()

    def obtener_habitaciones(self, conexion_externa = None) -> list[Habitacion | None]:

        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        list_habitaciones = []

        try:
            cursor = conexion.cursor()

            instruccion_sql = instruccion_obtener_habitaciones
            
            cursor.execute(instruccion_sql)
            resultados = cursor.fetchall()

            for registro in resultados:

                habitacion = Habitacion(
                    id_habitacion=registro[0],                        # type: ignore
                    numero=registro[1],                               # type: ignore
                    capacidad=registro[2],                            # type: ignore
                    precio_noche=Decimal(str(registro[3])),           # type: ignore
                    estado=EstadoHabitacion(str(registro[4]).lower()),# type: ignore  <--- CORREGIDO AQUÍ
                    activo=bool(registro[5])                          # type: ignore
                )

                list_habitaciones.append(habitacion)

            logging.info(f"Se obtuvieron {len(list_habitaciones)} habitaciones exitosamente.")

            return list_habitaciones
            
        except Exception as e: 

            logging.error(f"Error al obtener las habitaciones: {e}")
            return []

        finally:

            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()

    def obtener_habitacion_por_id(self, id_habitacion: int, conexion_externa = None) -> Habitacion | None:

        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        try:
            cursor = conexion.cursor()

            instruccion_sql = instruccion_obtener_habitacion_por_id
            
            valor = (id_habitacion, )

            cursor.execute(instruccion_sql, valor)
            resultado = cursor.fetchone()

            if not resultado:

                logging.warning(f"No se encontró ninguna habitación con el ID: {id_habitacion}")

                return None

            habitacion = Habitacion(
                id_habitacion=resultado[0],                       # type: ignore
                numero=resultado[1],                              # type: ignore
                capacidad=resultado[2],                           # type: ignore
                precio_noche=Decimal(str(resultado[3])),          # type: ignore
                estado=EstadoHabitacion(str(resultado[4]).lower()),# type: ignore <--- CORREGIDO AQUÍ
                activo=bool(resultado[5])                         # type: ignore
            )

            logging.info(f"Habitación con ID {id_habitacion} obtenida exitosamente.")

            return habitacion

        except Exception as e:

            logging.error(f"Error al obtener la habitación por ID: {e}")

            return None

        finally:

            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()

    def modificar_habitacion(
            self, 
            id_habitacion: int, 
            numero: int | None = None, 
            capacidad: int | None = None, 
            precio_noche: Decimal | None = None, 
            estado: EstadoHabitacion | None = None, 
            activo: bool | None = None,
            conexion_externa = None
    ) -> Habitacion | None:

        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        try:
            cursor = conexion.cursor()

            instruccion_sql = instruccion_modificar_habitacion

            precio_valor = float(precio_noche) if precio_noche is not None else None
            estado_valor = estado.value if estado is not None and hasattr(estado, "value") else estado

            valores = (numero, capacidad, precio_valor, estado_valor, activo, id_habitacion)

            cursor.execute(instruccion_sql, valores)
            
            if debe_cerrar:
                conexion.commit()

            if cursor.rowcount == 0:

                logging.warning(f"No se encontró ninguna habitación con el ID: {id_habitacion} para modificar.")

                return None

            logging.info(f"Habitación con ID {id_habitacion} modificada exitosamente.")
            
            return self.obtener_habitacion_por_id(id_habitacion, conexion_externa=conexion)

        except Exception as e:

            logging.error(f"Error al modificar la habitación: {e}")

            if debe_cerrar and conexion: 
                conexion.rollback()

            return None

        finally:

            if cursor:
                cursor.close()

            if debe_cerrar and conexion:
                conexion.close()
    
    def eliminar_habitacion(self, id_habitacion: int, conexion_externa = None) -> bool:
        
        """
            Realiza una baja lógica de la habitación cambiando su estado 'activo' a False,
            preservando el historial de reservas y la integridad de la base de datos.
        """
        try:
            
            habitacion_modificada = self.modificar_habitacion(
                id_habitacion=id_habitacion, 
                activo=False,
                conexion_externa=conexion_externa
            )

            if habitacion_modificada is None:

                logging.warning(f"No se encontró ninguna habitación con el ID: {id_habitacion} para dar de baja.")

                return False

            logging.info(f"Habitación con ID {id_habitacion} dada de baja lógica (activo = False) exitosamente.")

            return True

        except Exception as e:

            logging.error(f"Error crítico al intentar dar de baja a la habitación con ID {id_habitacion}: {e}")
            
            return False