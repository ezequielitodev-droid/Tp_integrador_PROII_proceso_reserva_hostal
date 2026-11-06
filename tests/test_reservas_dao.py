# Imports:

import itertools
import pytest
from datetime import date, timedelta
from decimal import Decimal

from dao.db_connection import obtener_conexion
from dao.reserva_dao import ReservaDAO
from dao.cliente_dao import ClienteDAO
from models.reserva import Reserva
from models.cliente import Cliente
from utils.datatypes.EstadoReserva import EstadoReserva
from loggers.logger_config import configurar_logging

_contador = itertools.count(1)


def _datos_unicos() -> dict:
    n = next(_contador)
    hoy = date.today()
    ingreso = hoy + timedelta(days=n * 3)
    salida = ingreso + timedelta(days=2)
    
    return {
        "fecha_reserva": hoy,
        "fecha_ingreso": ingreso,
        "fecha_salida": salida,
        "estado": EstadoReserva.RESERVADA,
        "monto_total": Decimal("90000.00"),
    }


def _armar_reserva(datos: dict) -> Reserva:
    return Reserva(
        id_reserva=None,
        fecha_reserva=datos["fecha_reserva"],
        fecha_ingreso=datos["fecha_ingreso"],
        fecha_salida=datos["fecha_salida"],
        estado=datos["estado"],
        monto_total=datos["monto_total"],
        activo=True,
    )


@pytest.fixture
def reserva_dao() -> ReservaDAO:
    return ReservaDAO()


@pytest.fixture
def cliente_id(conexion) -> int:
    """Crea un cliente válido previo para cumplir con la clave foránea en reservas."""
    cliente_dao = ClienteDAO()
    n = next(_contador)
    
    # 10 dígitos numéricos exactos requeridos por es_telefono_valido
    telefono_10_digitos = f"3874{n:06d}"  # Ej: "3874000001" (10 dígitos)
    
    cliente = Cliente(
        id_cliente=None,
        nombre="Test",
        apellido="Reserva",
        dni=f"90{n:06d}",
        telefono=telefono_10_digitos,
        correo=f"test.reserva{n}@email.com",
        activo=True
    )
    return cliente_dao.crear_cliente(cliente, conexion_externa=conexion) # type: ignore


@pytest.fixture
def conexion():
    con = obtener_conexion()
    configurar_logging()
    yield con
    con.commit()
    con.close()


@pytest.fixture
def reserva_guardada(reserva_dao, cliente_id, conexion):
    datos = _datos_unicos()
    id_generado = reserva_dao.crear_reserva(_armar_reserva(datos), id_cliente=cliente_id, conexion_externa=conexion)
    assert id_generado is not None
    return id_generado, datos


# ---------- CREATE ----------

def test_crear_reserva_devuelve_un_id_positivo(reserva_dao, cliente_id, conexion):
    id_generado = reserva_dao.crear_reserva(_armar_reserva(_datos_unicos()), id_cliente=cliente_id, conexion_externa=conexion)

    assert id_generado is not None
    assert id_generado > 0


# ---------- READ ----------

def test_obtener_reserva_por_id_devuelve_sus_datos(reserva_dao, reserva_guardada, conexion):
    id_reserva, datos = reserva_guardada

    reserva = reserva_dao.obtener_reserva_por_id(id_reserva, conexion_externa=conexion)

    assert reserva is not None
    assert reserva.get_id_reserva() == id_reserva
    assert reserva.get_fecha_reserva() == datos["fecha_reserva"]
    assert reserva.get_fecha_ingreso() == datos["fecha_ingreso"]
    assert reserva.get_fecha_salida() == datos["fecha_salida"]
    assert reserva.get_estado() == datos["estado"]
    assert reserva.get_monto_total() == datos["monto_total"]
    assert reserva.get_activo() is True


def test_obtener_reserva_por_id_inexistente_devuelve_none(reserva_dao, conexion):
    assert reserva_dao.obtener_reserva_por_id(999999999, conexion_externa=conexion) is None


def test_obtener_reservas_incluye_las_reservas_creadas(reserva_dao, reserva_guardada, conexion):
    id_reserva, _ = reserva_guardada

    ids = [r.get_id_reserva() for r, _ in reserva_dao.obtener_reservas(conexion_externa=conexion) if r]

    assert id_reserva in ids


# ---------- UPDATE ----------

def test_modificar_reserva_cambia_solo_el_campo_indicado(reserva_dao, reserva_guardada, conexion):
    id_reserva, datos = reserva_guardada

    modificada = reserva_dao.modificar_reserva(
        id_reserva=id_reserva, 
        monto_total=Decimal("120000.00"), 
        conexion_externa=conexion
    )

    assert modificada is not None
    assert modificada.get_monto_total() == Decimal("120000.00")
    assert modificada.get_fecha_ingreso() == datos["fecha_ingreso"]


def test_modificar_reserva_queda_guardado_en_la_base(reserva_dao, reserva_guardada, conexion):
    id_reserva, _ = reserva_guardada
    reserva_dao.modificar_reserva(
        id_reserva=id_reserva, 
        estado=EstadoReserva.CANCELADA, 
        conexion_externa=conexion
    )

    recuperada = reserva_dao.obtener_reserva_por_id(id_reserva, conexion_externa=conexion)

    assert recuperada is not None
    assert recuperada.get_estado() == EstadoReserva.CANCELADA


def test_modificar_reserva_inexistente_devuelve_none(reserva_dao, conexion):
    resultado = reserva_dao.modificar_reserva(
        id_reserva=999999999, 
        monto_total=Decimal("50000.00"), 
        conexion_externa=conexion
    )

    assert resultado is None


# ---------- DELETE (baja lógica) ----------

def test_eliminar_reserva_hace_baja_logica(reserva_dao, reserva_guardada, conexion):
    id_reserva, _ = reserva_guardada

    assert reserva_dao.eliminar_reserva(id_reserva, conexion_externa=conexion) is True

    reserva = reserva_dao.obtener_reserva_por_id(id_reserva, conexion_externa=conexion)
    assert reserva is not None
    assert reserva.get_activo() is False


def test_eliminar_reserva_inexistente_devuelve_false(reserva_dao, conexion):
    assert reserva_dao.eliminar_reserva(999999999, conexion_externa=conexion) is False