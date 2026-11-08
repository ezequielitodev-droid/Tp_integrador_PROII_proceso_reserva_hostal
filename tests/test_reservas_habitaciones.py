# Imports:

import itertools
import pytest
from datetime import date
from decimal import Decimal

from dao.db_connection import obtener_conexion
from dao.reservas_habitaciones_dao import ReservasHabitacionesDAO
from dao.reserva_dao import ReservaDAO
from dao.habitacion_dao import HabitacionDAO
from dao.cliente_dao import ClienteDAO
from models.reserva import Reserva
from models.habitacion import Habitacion
from models.cliente import Cliente
from utils.datatypes.EstadoReserva import EstadoReserva
from utils.datatypes.EstadoHabitacion import EstadoHabitacion
from loggers.logger_config import configurar_logging

_contador = itertools.count(1)


@pytest.fixture
def reservas_habitaciones_dao() -> ReservasHabitacionesDAO:
    return ReservasHabitacionesDAO()


@pytest.fixture
def reserva_dao() -> ReservaDAO:
    return ReservaDAO()


@pytest.fixture
def habitacion_dao() -> HabitacionDAO:
    return HabitacionDAO()


@pytest.fixture
def cliente_dao() -> ClienteDAO:
    return ClienteDAO()


@pytest.fixture
def conexion():
    """Abre la conexión antes del test y la cierra automáticamente al terminar."""
    con = obtener_conexion()
    configurar_logging()
    yield con
    con.commit()
    con.close()


@pytest.fixture
def contexto_asociacion_habitacion(reserva_dao, habitacion_dao, cliente_dao, conexion):
    """
        Crea previamente un cliente, una reserva y una habitación base en la base de datos 
        para poder probar la tabla intermedia respetando las llaves foráneas.
    """
    n = next(_contador)
    
    # 1. Creamos un cliente obligatorio para la reserva
    cliente = Cliente(
        id_cliente=None,
        nombre=f"ClienteHab_{n}",
        apellido="Prueba",
        dni=f"{35000000 + n}",
        telefono="3871234567",
        correo=f"testhab{n}@mail.com",
        activo=True
    )
    id_cliente = cliente_dao.crear_cliente(cliente, conexion_externa=conexion)
    assert id_cliente is not None

    # 2. Creamos una reserva válida
    reserva = Reserva(
        id_reserva=None,
        fecha_reserva=date.today(),
        fecha_ingreso=date(2026, 12, 1),
        fecha_salida=date(2026, 12, 10),
        estado=EstadoReserva.RESERVADA,
        monto_total=Decimal("150000.00"),
        activo=True
    )
    id_reserva = reserva_dao.crear_reserva(reserva, id_cliente=id_cliente, conexion_externa=conexion)
    assert id_reserva is not None

    # 3. Creamos una habitación base válida
    habitacion = Habitacion(
        id_habitacion=None,
        numero=200 + n,
        capacidad=2,
        precio_noche=Decimal("45000.00"),
        estado=EstadoHabitacion.DISPONIBLE,
        activo=True
    )
    id_habitacion = habitacion_dao.crear_habitacion(habitacion, conexion_externa=conexion)
    assert id_habitacion is not None

    return id_reserva, id_habitacion


# ---------- ASOCIACIÓN Y CONSULTA (VINCULACIONES) ----------

def test_asociar_habitacion_a_reserva_exitoso(reservas_habitaciones_dao, contexto_asociacion_habitacion, conexion):
    id_reserva, id_habitacion = contexto_asociacion_habitacion

    # Ejecutamos la asociación en la tabla intermedia
    resultado = reservas_habitaciones_dao.asociar_habitacion_a_reserva(
        id_reserva=id_reserva, 
        id_habitacion=id_habitacion, 
        conexion_externa=conexion
    )

    assert resultado is True


def test_obtener_habitaciones_por_reserva_devuelve_la_habitacion_asociada(reservas_habitaciones_dao, contexto_asociacion_habitacion, conexion):
    id_reserva, id_habitacion = contexto_asociacion_habitacion

    # Primero asociamos
    reservas_habitaciones_dao.asociar_habitacion_a_reserva(
        id_reserva=id_reserva, 
        id_habitacion=id_habitacion, 
        conexion_externa=conexion
    )

    # Luego consultamos las habitaciones de esa reserva
    habitaciones = reservas_habitaciones_dao.obtener_habitaciones_por_reserva(
        id_reserva=id_reserva, 
        conexion_externa=conexion
    )

    assert len(habitaciones) == 1
    assert habitaciones[0].get_id_habitacion() == id_habitacion


# ---------- MÚLTIPLES HABITACIONES EN UNA MISMA RESERVA ----------

def test_asociar_multiples_habitaciones_a_una_reserva(reservas_habitaciones_dao, habitacion_dao, contexto_asociacion_habitacion, conexion):
    id_reserva, id_habitacion_1 = contexto_asociacion_habitacion

    n = next(_contador)
    # Creamos una segunda habitación independiente
    habitacion_2 = Habitacion(
        id_habitacion=None,
        numero=300 + n,
        capacidad=3,
        precio_noche=Decimal("60000.00"),
        estado=EstadoHabitacion.DISPONIBLE,
        activo=True
    )
    id_habitacion_2 = habitacion_dao.crear_habitacion(habitacion_2, conexion_externa=conexion)
    assert id_habitacion_2 is not None

    # Asociamos ambas habitaciones a la misma reserva
    res_1 = reservas_habitaciones_dao.asociar_habitacion_a_reserva(id_reserva, id_habitacion_1, conexion_externa=conexion)
    res_2 = reservas_habitaciones_dao.asociar_habitacion_a_reserva(id_reserva, id_habitacion_2, conexion_externa=conexion)

    assert res_1 is True
    assert res_2 is True

    # Consultamos las habitaciones asociadas a la reserva
    habitaciones = reservas_habitaciones_dao.obtener_habitaciones_por_reserva(id_reserva, conexion_externa=conexion)

    # Verificamos que traiga exactamente las 2 habitaciones
    assert len(habitaciones) == 2
    ids_obtenidos = [h.get_id_habitacion() for h in habitaciones]
    assert id_habitacion_1 in ids_obtenidos
    assert id_habitacion_2 in ids_obtenidos


# ---------- ELIMINACIÓN DE ASOCIACIÓN ----------

def test_eliminar_asociacion_habitacion_existente(reservas_habitaciones_dao, contexto_asociacion_habitacion, conexion):
    # El contexto nos da una reserva y una habitación recién creadas
    id_reserva, id_habitacion = contexto_asociacion_habitacion

    # 1. Creamos explícitamente la asociación inicial
    exito_asociacion = reservas_habitaciones_dao.asociar_habitacion_a_reserva(
        id_reserva=id_reserva, 
        id_habitacion=id_habitacion, 
        conexion_externa=conexion
    )
    assert exito_asociacion is True

    # 2. Eliminamos la asociación de la tabla intermedia
    eliminado = reservas_habitaciones_dao.eliminar_asociacion(
        id_reserva=id_reserva, 
        id_habitacion=id_habitacion, 
        conexion_externa=conexion
    )
    
    # 3. Verificamos que se eliminó correctamente
    assert eliminado is True

    # Comprobamos que el vínculo ya no existe para esa reserva
    habitaciones = reservas_habitaciones_dao.obtener_habitaciones_por_reserva(
        id_reserva=id_reserva, 
        conexion_externa=conexion
    )
    assert len(habitaciones) == 0