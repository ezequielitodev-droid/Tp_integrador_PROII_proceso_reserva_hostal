# Imports:

import logging
from datetime import date
from decimal import Decimal
from models.reserva import Reserva
from dao.reserva_dao import ReservaDAO
from dao.cliente_dao import ClienteDAO
from utils.datatypes.EstadoReserva import EstadoReserva
from utils.validators.datavalidators import (
    es_fecha_reserva_valida,
    es_fecha_ingreso_valida,
    es_fecha_salida_valida,
    es_rango_fechas_valido,
    es_estado_reserva_valido,
    es_monto_total_valido,
    es_id_persona_valido
)

# Constants:

# Global Variables:

# Apuntamos al parlante específico de la capa de Servicios
logger = logging.getLogger("services.reserva_service")

# Class:

class ReservaService:

    # Constructor:

    def __init__(
            self, 
            reserva_dao: ReservaDAO | None = None,
            cliente_dao: ClienteDAO | None = None
    ):
        # Inyectamos las dependencias necesarias para las reglas cruzadas
        self.reserva_dao = reserva_dao or ReservaDAO()
        self.cliente_dao = cliente_dao or ClienteDAO()

    # Métodos estratégicos:

    def crear_reserva(
            self, 
            fecha_reserva: date,
            fecha_ingreso: date, 
            fecha_salida: date, 
            monto_total: Decimal | float, 
            id_cliente: int,
            estado: EstadoReserva | str = EstadoReserva.RESERVADA,
            conexion_externa = None
    ) -> int | None:
        """
            Aplica reglas de negocio y validaciones antes de persistir una reserva.
            Verifica la existencia del cliente y la coherencia en las fechas y montos.
        """
        if not es_fecha_reserva_valida(fecha_reserva):
            raise ValueError("La fecha de reserva no es válida.")

        if not es_fecha_ingreso_valida(fecha_ingreso):
            raise ValueError("La fecha de ingreso no es válida.")

        if not es_fecha_salida_valida(fecha_salida):
            raise ValueError("La fecha de salida no es válida.")

        if not es_rango_fechas_valido(fecha_ingreso, fecha_salida):
            raise ValueError("La fecha de salida debe ser posterior a la fecha de ingreso.")

        monto_dec = Decimal(str(monto_total)) if not isinstance(monto_total, Decimal) else monto_total
        if not es_monto_total_valido(monto_dec):
            raise ValueError("El monto total de la reserva no es válido.")

        if not es_id_persona_valido(id_cliente):
            raise ValueError("El ID del cliente asociado no es válido.")

        # Pasamos la conexión externa al DAO del cliente
        cliente = self.cliente_dao.obtener_cliente_por_id(id_cliente, conexion_externa=conexion_externa)
        if not cliente or not cliente.get_activo():
            logger.warning(f"Intento de crear reserva para un cliente inexistente o inactivo ID: {id_cliente}")
            raise ValueError(f"El cliente con ID {id_cliente} no existe o no se encuentra activo.")

        if isinstance(estado, str):
            estado = EstadoReserva(estado.lower())

        if not es_estado_reserva_valido(estado):
            raise ValueError("El estado de la reserva proporcionado no es válido.")

        nueva_reserva = Reserva(
            id_reserva=None,
            fecha_reserva=fecha_reserva,
            fecha_ingreso=fecha_ingreso,
            fecha_salida=fecha_salida,
            estado=estado,
            monto_total=monto_dec,
            activo=True
        )

        # Pasamos la conexión externa al DAO de reservas
        id_generado = self.reserva_dao.crear_reserva(nueva_reserva, id_cliente, conexion_externa=conexion_externa)
        
        if id_generado:
            logger.info(f"Reserva principal creada con éxito con ID: {id_generado}")

        return id_generado

    def crear_reserva_completa(self, datos_formulario: dict, conexion_externa = None) -> int:
        
        cliente_info = datos_formulario.get("cliente", {})
        fechas = datos_formulario.get("fechas", {})
        huespedes_lista = datos_formulario.get("huespedes", [])

        if not huespedes_lista:
            raise ValueError("La reserva debe contener al menos un huésped asignado a una habitación.")

        dni_cliente_titular = cliente_info.get("dni")
        if not dni_cliente_titular:
            raise ValueError("El DNI del cliente titular es obligatorio.")

        print("🔍 A punto de llamar a obtener_cliente_por_dni con el DNI:", dni_cliente_titular)
        cliente_existente = self.cliente_dao.obtener_cliente_por_dni(dni_cliente_titular, conexion_externa=conexion_externa)
        print("🔍 Resultado obtenido:", cliente_existente)
        if not cliente_existente:
            print("El cliente esta en NONE")
        else:
            print("El cliente si tiene datos...")
            print(cliente_existente)
            print(cliente_existente.get_id_persona())
            print(cliente_existente.get_activo())
            print(cliente_existente.get_nombre())
            print(cliente_existente.get_telefono())
            print(cliente_existente.get_apellido())
            print(cliente_existente.get_correo())
        if not cliente_existente or not cliente_existente.get_activo():
            logger.warning(f"Intento de reserva completa con DNI titular inexistente o inactivo: {dni_cliente_titular}")
            raise ValueError(
                f"El cliente titular con DNI {dni_cliente_titular} no existe o no se encuentra activo."
            )
        
        id_cliente = cliente_existente.get_id_persona()

        # Crear la reserva principal pasando la conexión externa
        id_reserva = self.crear_reserva(
            fecha_reserva=date.today(),
            fecha_ingreso=fechas.get("fecha_ingreso"),
            fecha_salida=fechas.get("fecha_salida"),
            monto_total=fechas.get("monto_total", 0.0),
            id_cliente=id_cliente, #type: ignore
            estado=EstadoReserva.RESERVADA,
            conexion_externa=conexion_externa
        )

        if not id_reserva:
            raise RuntimeError("No se pudo generar el registro principal de la reserva.")

        from dao.huesped_dao import HuespedDAO
        from dao.reservas_huespedes_dao import ReservasHuespedesDAO
        from dao.reservas_habitaciones_dao import ReservasHabitacionesDAO
        from models.huesped import Huesped

        huesped_dao = HuespedDAO()
        reserva_huesped_dao = ReservasHuespedesDAO()
        reserva_habitacion_dao = ReservasHabitacionesDAO()

        try:
            habitaciones_procesadas = set()

            for h_info in huespedes_lista:
                dni_huesped = h_info.get("dni")
                id_habitacion = h_info.get("id_habitacion")

                if not id_habitacion:
                    raise ValueError(f"El huésped {h_info.get('nombre')} no tiene una habitación asignada.")

                if not dni_huesped:
                    raise ValueError("Todos los huéspedes deben tener un DNI válido.")

                # Pasar conexion_externa aquí también
                huesped_obj = huesped_dao.obtener_huesped_por_dni(dni_huesped, conexion_externa=conexion_externa)
                
                if huesped_obj:
                    id_huesped = huesped_obj.get_id_persona()
                else:
                    nuevo_huesped = Huesped(
                        id_huesped=None,
                        nombre=h_info.get("nombre"),
                        apellido=h_info.get("apellido"),
                        dni=dni_huesped,
                        telefono=h_info.get("telefono", ""),
                        activo=True
                    )
                    # Pasar conexion_externa al crear huésped
                    id_huesped = huesped_dao.crear_huesped(nuevo_huesped, conexion_externa=conexion_externa)
                    if not id_huesped:
                        raise RuntimeError(f"No se pudo registrar al huésped con DNI {dni_huesped}.")

                # Asociar huésped pasando conexion_externa
                asociacion_huesped_ok = reserva_huesped_dao.asociar_huesped_a_reserva(
                    id_reserva=id_reserva, 
                    id_huesped=id_huesped, #type: ignore
                    conexion_externa=conexion_externa
                )
                if not asociacion_huesped_ok:
                    raise RuntimeError(f"Falló la asociación del huésped ID {id_huesped} a la reserva.")

                # Asociar habitación pasando conexion_externa
                if id_habitacion not in habitaciones_procesadas:
                    asociacion_hab_ok = reserva_habitacion_dao.asociar_habitacion_a_reserva(
                        id_reserva=id_reserva,
                        id_habitacion=int(id_habitacion),
                        conexion_externa=conexion_externa
                    )
                    if not asociacion_hab_ok:
                        raise RuntimeError(f"Falló la asociación de la habitación ID {id_habitacion} a la reserva.")
                    
                    habitaciones_procesadas.add(id_habitacion)

            logger.info(f"Reserva compleja ID {id_reserva} creada y asociada con éxito.")
            return id_reserva

        except Exception as e:
            logger.error(f"Error crítico en transacción de reserva compleja. Revirtiendo... Detalle: {e}")
            self.eliminar_reserva(id_reserva)
            raise RuntimeError(f"Error al procesar la reserva completa: {e}")

    def obtener_reservas(self) -> list[tuple[Reserva, int] | None]:
        """Obtiene el listado completo de reservas junto con el ID de su cliente."""
        logger.info("Solicitud para obtener listado completo de reservas.")
        return self.reserva_dao.obtener_reservas()

    def obtener_reserva_por_id(self, id_reserva: int, conexion_externa = None) -> Reserva | None:
        """Busca una reserva específica por su ID."""
        logger.info(f"Solicitud para obtener reserva por ID: {id_reserva}")
        return self.reserva_dao.obtener_reserva_por_id(id_reserva, conexion_externa=conexion_externa)

    def modificar_reserva(
            self, 
            id_reserva: int, 
            fecha_reserva: date | None = None,
            fecha_ingreso: date | None = None, 
            fecha_salida: date | None = None, 
            estado: EstadoReserva | str | None = None, 
            monto_total: Decimal | float | None = None, 
            id_cliente: int | None = None,
            activo: bool | None = None
    ) -> Reserva | None:
        """Modifica atributos de la reserva aplicando validaciones de coherencia."""
        if fecha_ingreso is not None and not es_fecha_ingreso_valida(fecha_ingreso):
            raise ValueError("La nueva fecha de ingreso no es válida.")

        if fecha_salida is not None and not es_fecha_salida_valida(fecha_salida):
            raise ValueError("La nueva fecha de salida no es válida.")

        monto_dec = None
        if monto_total is not None:
            monto_dec = Decimal(str(monto_total)) if not isinstance(monto_total, Decimal) else monto_total
            if not es_monto_total_valido(monto_dec):
                raise ValueError("El monto total proporcionado no es válido.")

        estado_enum = None
        if estado is not None:
            estado_enum = EstadoReserva(estado.lower()) if isinstance(estado, str) else estado
            if not es_estado_reserva_valido(estado_enum):
                raise ValueError("El estado de reserva proporcionado no es válido.")

        if id_cliente is not None:
            cliente = self.cliente_dao.obtener_cliente_por_id(id_cliente)
            if not cliente or not cliente.get_activo():
                raise ValueError(f"El cliente con ID {id_cliente} no existe o no está activo.")

        logger.info(f"Solicitud para modificar la reserva ID: {id_reserva}")
        return self.reserva_dao.modificar_reserva(
            id_reserva=id_reserva,
            fecha_reserva=fecha_reserva,
            fecha_ingreso=fecha_ingreso,
            fecha_salida=fecha_salida,
            estado=estado_enum,
            monto_total=monto_dec,
            id_cliente=id_cliente,
            activo=activo
        )

    def eliminar_reserva(self, id_reserva: int) -> bool:
        """Realiza la baja lógica de la reserva (activo = False)."""
        logger.info(f"Solicitud para eliminar (baja lógica) reserva con ID: {id_reserva}")
        return self.reserva_dao.eliminar_reserva(id_reserva)