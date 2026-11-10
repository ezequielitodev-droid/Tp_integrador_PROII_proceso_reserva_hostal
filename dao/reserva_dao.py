# Imports:
import logging
from datetime import date
from decimal import Decimal

from dao.db_connection import obtener_conexion
from models.reserva import Reserva
from utils.datatypes.EstadoReserva import EstadoReserva
from database.queries import (
    instruccion_crear_reserva, 
    instruccion_obtener_reservas, 
    instruccion_obtener_reserva_por_id, 
    instruccion_modificar_reserva,
    instruccion_obtener_huespedes_por_reserva,
    instruccion_obtener_habitaciones_detalladas_por_reserva
)

#Global Variables:
logger = logging.getLogger("dao.reserva_dao")

class ReservaDAO:

    def crear_reserva(self, reserva: Reserva, id_cliente: int, conexion_externa = None) -> int | None:
        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        try:
            cursor = conexion.cursor()
            instruccion_sql = instruccion_crear_reserva
            estado_valor = reserva.get_estado().value if hasattr(reserva.get_estado(), "value") else reserva.get_estado()

            valores = (
                reserva.get_fecha_reserva(),
                reserva.get_fecha_ingreso(),
                reserva.get_fecha_salida(),
                estado_valor,
                float(reserva.get_monto_total()),
                id_cliente,
                reserva.get_activo()
            )

            cursor.execute(instruccion_sql, valores)
            if debe_cerrar:
                conexion.commit()

            id_generado = cursor.lastrowid
            logging.info(f"Reserva creada exitosamente con ID: {id_generado}")
            return id_generado

        except Exception as e:
            logging.error(f"Error al crear la reserva: {e}")
            if debe_cerrar and conexion:
                conexion.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()

    def obtener_reservas(self, conexion_externa = None) -> list[tuple[Reserva, int] | None]:
        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None
        list_reservas = []

        try:
            cursor = conexion.cursor()
            cursor.execute(instruccion_obtener_reservas)
            resultados = cursor.fetchall()

            for registro in resultados:
                reserva = Reserva(
                    id_reserva=registro[0],  # type: ignore
                    fecha_reserva=registro[1] if isinstance(registro[1], date) else date.fromisoformat(str(registro[1])),  # type: ignore
                    fecha_ingreso=registro[2] if isinstance(registro[2], date) else date.fromisoformat(str(registro[2])),  # type: ignore
                    fecha_salida=registro[3] if isinstance(registro[3], date) else date.fromisoformat(str(registro[3])),  # type: ignore
                    estado=EstadoReserva(str(registro[4]).lower()),  # type: ignore
                    monto_total=Decimal(str(registro[5])),  # type: ignore
                    activo=bool(registro[7])  # type: ignore
                )
                list_reservas.append((reserva, registro[6]))

            logging.info(f"Se obtuvieron {len(list_reservas)} reservas exitosamente.")
            return list_reservas
            
        except Exception as e: 
            logging.error(f"Error al obtener las reservas: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()

    def obtener_reserva_por_id(self, id_reserva: int, conexion_externa = None) -> Reserva | None:
        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        try:
            cursor = conexion.cursor()
            cursor.execute(instruccion_obtener_reserva_por_id, (id_reserva,))
            resultado = cursor.fetchone()

            if not resultado:
                logging.warning(f"No se encontró ninguna reserva con el ID: {id_reserva}")
                return None

            reserva = Reserva(
                id_reserva=resultado[0],  # type: ignore
                fecha_reserva=resultado[1] if isinstance(resultado[1], date) else date.fromisoformat(str(resultado[1])),  # type: ignore
                fecha_ingreso=resultado[2] if isinstance(resultado[2], date) else date.fromisoformat(str(resultado[2])),  # type: ignore
                fecha_salida=resultado[3] if isinstance(resultado[3], date) else date.fromisoformat(str(resultado[3])),  # type: ignore
                estado=EstadoReserva(str(resultado[4]).lower()),  # type: ignore
                monto_total=Decimal(str(resultado[5])),  # type: ignore
                activo=bool(resultado[7])  # type: ignore
            )
            return reserva

        except Exception as e:
            logging.error(f"Error al obtener la reserva por ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()

    def obtener_detalles_completos_por_reserva(self, id_reserva: int, conexion_externa = None) -> list[dict]:
        """Consulta los huéspedes y la habitación asociada a la reserva usando las tablas intermedias."""
        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None
        detalles = []

        try:
            cursor = conexion.cursor()
            
            # Obtener huéspedes
            cursor.execute(instruccion_obtener_huespedes_por_reserva, (id_reserva,))
            res_huespedes = cursor.fetchall()
            
            # Obtener habitaciones
            cursor.execute(instruccion_obtener_habitaciones_detalladas_por_reserva, (id_reserva,))
            res_habitaciones = cursor.fetchall()

            habitacion_numero = "N/D"
            precio_habitacion = 0.0
            if res_habitaciones:
                habitacion_numero = str(res_habitaciones[0][1])
                precio_habitacion = float(res_habitaciones[0][3])

            for h in res_huespedes:
                detalles.append({
                    "nombre": h[1] if len(h) > 1 else "",
                    "apellido": h[2] if len(h) > 2 else "",
                    "dni": h[3] if len(h) > 3 else "",
                    "telefono": h[4] if len(h) > 4 else "",
                    "habitacion": habitacion_numero,
                    "precio": precio_habitacion
                })

            return detalles

        except Exception as e:
            logging.error(f"Error al obtener detalles completos de la reserva #{id_reserva}: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()

    def modificar_reserva(
            self, 
            id_reserva: int, 
            fecha_reserva: date | None = None,
            fecha_ingreso: date | None = None, 
            fecha_salida: date | None = None, 
            estado: EstadoReserva | None = None, 
            monto_total: Decimal | None = None, 
            id_cliente: int | None = None,
            activo: bool | None = None,
            conexion_externa = None
    ) -> Reserva | None:
        conexion = conexion_externa or obtener_conexion()
        debe_cerrar = conexion_externa is None
        cursor = None

        try:
            cursor = conexion.cursor()
            monto_valor = float(monto_total) if monto_total is not None else None
            estado_valor = estado.value if estado is not None and hasattr(estado, "value") else estado

            valores = (fecha_reserva, fecha_ingreso, fecha_salida, estado_valor, monto_valor, id_cliente, activo, id_reserva)
            cursor.execute(instruccion_modificar_reserva, valores)
            
            if debe_cerrar:
                conexion.commit()

            if cursor.rowcount == 0:
                return None

            return self.obtener_reserva_por_id(id_reserva, conexion_externa=conexion)

        except Exception as e:
            logging.error(f"Error al modificar la reserva: {e}")
            if debe_cerrar and conexion: 
                conexion.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if debe_cerrar and conexion:
                conexion.close()
    
    def eliminar_reserva(self, id_reserva: int, conexion_externa = None) -> bool:
        
        try:
            reserva_modificada = self.modificar_reserva(id_reserva=id_reserva, activo=False, conexion_externa=conexion_externa)
            return reserva_modificada is not None
        except Exception as e:
            logging.error(f"Error crítico al intentar dar de baja a la reserva con ID {id_reserva}: {e}")
            return False