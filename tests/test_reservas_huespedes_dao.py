# Imports:

import itertools
import pytest
from datetime import date
from decimal import Decimal

from dao.db_connection import obtener_conexion
from dao.reservas_huespedes_dao import ReservasHuespedesDAO
from dao.reserva_dao import ReservaDAO
from dao.huesped_dao import HuespedDAO
from dao.cliente_dao import ClienteDAO
from models.reserva import Reserva
from models.huesped import Huesped
from models.cliente import Cliente
from utils.datatypes.EstadoReserva import EstadoReserva
from loggers.logger_config import configurar_logging

_contador = itertools.count(1)


@pytest.fixture
def reservas_huespedes_dao() -> ReservasHuespedesDAO:
    return ReservasHuespedesDAO()


@pytest.fixture
def reserva_dao() -> ReservaDAO:
    return ReservaDAO()


@pytest.fixture
def huesped_dao() -> HuespedDAO:
    return HuespedDAO()


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
def contexto_asociacion(reserva_dao, huesped_dao, cliente_dao, conexion):
    """
        Crea previamente un cliente, una reserva y un huésped base en la base de datos 
        para poder probar la tabla intermedia respetando las llaves foráneas.
    """
    n = next(_contador)
    
    # 1. Creamos un cliente obligatorio para la reserva
    cliente = Cliente(
        id_cliente=None,
        nombre=f"ClienteTest_{n}",
        apellido="Prueba",
        dni=f"{30000000 + n}",
        telefono="3871234567",
        correo=f"test{n}@mail.com",
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

    # 3. Creamos un huésped base válido
    huesped = Huesped(
        id_huesped=None,
        nombre=f"HuespedTest_{n}",
        apellido="Prueba",
        dni=f"{40000000 + n}",
        telefono="3879876543",
        activo=True
    )
    id_huesped = huesped_dao.crear_huesped(huesped, conexion_externa=conexion)
    assert id_huesped is not None

    return id_reserva, id_huesped


# ---------- ASOCIACIÓN Y CONSULTA (VINCULACIONES) ----------

def test_asociar_huesped_a_reserva_exitoso(reservas_huespedes_dao, contexto_asociacion, conexion):
    id_reserva, id_huesped = contexto_asociacion

    # Ejecutamos la asociación en la tabla intermedia
    resultado = reservas_huespedes_dao.asociar_huesped_a_reserva(
        id_reserva=id_reserva, 
        id_huesped=id_huesped, 
        conexion_externa=conexion
    )

    assert resultado is True


def test_obtener_huespedes_por_reserva_devuelve_el_huesped_asociado(reservas_huespedes_dao, contexto_asociacion, conexion):
    id_reserva, id_huesped = contexto_asociacion

    # Primero asociamos
    reservas_huespedes_dao.asociar_huesped_a_reserva(
        id_reserva=id_reserva, 
        id_huesped=id_huesped, 
        conexion_externa=conexion
    )

    # Luego consultamos los huéspedes de esa reserva
    huespedes = reservas_huespedes_dao.obtener_huespedes_por_reserva(
        id_reserva=id_reserva, 
        conexion_externa=conexion
    )

    assert len(huespedes) == 1
    assert huespedes[0].get_id_persona() == id_huesped


# ---------- MÚLTIPLES HUÉSPEDES EN UNA MISMA RESERVA ----------

def test_asociar_multiples_huespedes_a_una_reserva(reservas_huespedes_dao, huesped_dao, contexto_asociacion, conexion):
    id_reserva, id_huesped_1 = contexto_asociacion

    n = next(_contador)
    # Creamos un segundo huésped independiente
    huesped_2 = Huesped(
        id_huesped=None,
        nombre=f"SegundoHuesped_{n}",
        apellido="Prueba",
        dni=f"{45000000 + n}",
        telefono="3875554433",
        activo=True
    )
    id_huesped_2 = huesped_dao.crear_huesped(huesped_2, conexion_externa=conexion)
    assert id_huesped_2 is not None

    # Asociamos ambos huéspedes a la misma reserva
    res_1 = reservas_huespedes_dao.asociar_huesped_a_reserva(id_reserva, id_huesped_1, conexion_externa=conexion)
    res_2 = reservas_huespedes_dao.asociar_huesped_a_reserva(id_reserva, id_huesped_2, conexion_externa=conexion)

    assert res_1 is True
    assert res_2 is True

    # Consultamos los huéspedes asociados a la reserva
    huespedes = reservas_huespedes_dao.obtener_huespedes_por_reserva(id_reserva, conexion_externa=conexion)

    # Verificamos que traiga exactamente los 2 huéspedes
    assert len(huespedes) == 2
    ids_obtenidos = [h.get_id_persona() for h in huespedes]
    assert id_huesped_1 in ids_obtenidos
    assert id_huesped_2 in ids_obtenidos


# ---------- ELIMINACIÓN DE ASOCIACIÓN (Comentado para probar después) ----------

def test_eliminar_asociacion_existente(reservas_huespedes_dao, contexto_asociacion, conexion):
    # El contexto ya nos da una reserva y un huésped recién creados e independientes
    id_reserva, id_huesped = contexto_asociacion

    # 1. Creamos explícitamente la asociación inicial (simulando que ya existe en la DB)
    exito_asociacion = reservas_huespedes_dao.asociar_huesped_a_reserva(
        id_reserva=id_reserva, 
        id_huesped=id_huesped, 
        conexion_externa=conexion
    )
    assert exito_asociacion is True

    # (En este punto, si vas a tu base de datos antes de que termine el test, ya ves el registro insertado).

    # 2. Le pasamos esos parámetros existentes al método de eliminación
    eliminado = reservas_huespedes_dao.eliminar_asociacion(
        id_reserva=id_reserva, 
        id_huesped=id_huesped, 
        conexion_externa=conexion
    )
    
    # 3. Verificamos que se eliminó correctamente
    assert eliminado is True

    # Comprobamos que el vínculo ya no existe para esa reserva
    huespedes = reservas_huespedes_dao.obtener_huespedes_por_reserva(
        id_reserva=id_reserva, 
        conexion_externa=conexion
    )
    assert len(huespedes) == 0