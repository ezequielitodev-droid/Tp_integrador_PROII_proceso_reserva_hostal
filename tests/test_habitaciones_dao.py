# Imports:

import itertools
import pytest
from decimal import Decimal

from dao.db_connection import obtener_conexion
from dao.habitacion_dao import HabitacionDAO
from models.habitacion import Habitacion
from utils.datatypes.EstadoHabitacion import EstadoHabitacion
from loggers.logger_config import configurar_logging

_contador = itertools.count(1)


def _datos_unicos() -> dict:
    n = next(_contador)
    return {
        "numero": 100 + n,
        "capacidad": 2,
        "precio_noche": Decimal("45000.00"),
        "estado": EstadoHabitacion.DISPONIBLE,
    }


def _armar_habitacion(datos: dict) -> Habitacion:
    return Habitacion(
        id_habitacion=None,
        numero=datos["numero"],
        capacidad=datos["capacidad"],
        precio_noche=datos["precio_noche"],
        estado=datos["estado"],
        activo=True,
    )


@pytest.fixture
def habitacion_dao() -> HabitacionDAO:
    return HabitacionDAO()


@pytest.fixture
def conexion():
    """Abre la conexión antes del test y la cierra automáticamente al terminar."""
    con = obtener_conexion()
    configurar_logging()
    yield con
    con.commit()
    con.close()


@pytest.fixture
def habitacion_guardada(habitacion_dao, conexion):
    # Guarda una habitación nueva usando la conexión y devuelve (id, datos)
    datos = _datos_unicos()
    id_generado = habitacion_dao.crear_habitacion(_armar_habitacion(datos), conexion_externa=conexion)
    assert id_generado is not None
    return id_generado, datos


# ---------- CREATE ----------

def test_crear_habitacion_devuelve_un_id_positivo(habitacion_dao, conexion):
    id_generado = habitacion_dao.crear_habitacion(_armar_habitacion(_datos_unicos()), conexion_externa=conexion)

    assert id_generado is not None
    assert id_generado > 0


def test_crear_habitacion_con_numero_duplicado_devuelve_none(habitacion_dao, habitacion_guardada, conexion):
    _, datos = habitacion_guardada

    # Intentamos crear otra habitación con exactamente el mismo número
    id_repetido = habitacion_dao.crear_habitacion(_armar_habitacion(datos), conexion_externa=conexion)

    assert id_repetido is None


# ---------- READ ----------

def test_obtener_habitacion_por_id_devuelve_sus_datos(habitacion_dao, habitacion_guardada, conexion):
    id_habitacion, datos = habitacion_guardada

    habitacion = habitacion_dao.obtener_habitacion_por_id(id_habitacion, conexion_externa=conexion)

    assert habitacion is not None
    assert habitacion.get_id_habitacion() == id_habitacion
    assert habitacion.get_numero() == datos["numero"]
    assert habitacion.get_capacidad() == datos["capacidad"]
    assert habitacion.get_precio_noche() == datos["precio_noche"]
    assert habitacion.get_estado() == datos["estado"]
    assert habitacion.get_activo() is True


def test_obtener_habitacion_por_id_inexistente_devuelve_none(habitacion_dao, conexion):
    assert habitacion_dao.obtener_habitacion_por_id(999999999, conexion_externa=conexion) is None


def test_obtener_habitaciones_incluye_las_habitaciones_creadas(habitacion_dao, habitacion_guardada, conexion):
    id_habitacion, _ = habitacion_guardada

    ids = [h.get_id_habitacion() for h in habitacion_dao.obtener_habitaciones(conexion_externa=conexion) if h]

    assert id_habitacion in ids


# ---------- UPDATE ----------

def test_modificar_habitacion_cambia_solo_el_campo_indicado(habitacion_dao, habitacion_guardada, conexion):
    id_habitacion, datos = habitacion_guardada

    modificada = habitacion_dao.modificar_habitacion(
        id_habitacion=id_habitacion, 
        precio_noche=Decimal("60000.00"), 
        conexion_externa=conexion
    )

    assert modificada is not None
    assert modificada.get_precio_noche() == Decimal("60000.00")
    assert modificada.get_numero() == datos["numero"]


def test_modificar_habitacion_queda_guardado_en_la_base(habitacion_dao, habitacion_guardada, conexion):
    id_habitacion, _ = habitacion_guardada
    habitacion_dao.modificar_habitacion(
        id_habitacion=id_habitacion, 
        estado=EstadoHabitacion.OCUPADA, 
        conexion_externa=conexion
    )

    recuperada = habitacion_dao.obtener_habitacion_por_id(id_habitacion, conexion_externa=conexion)

    assert recuperada is not None
    assert recuperada.get_estado() == EstadoHabitacion.OCUPADA


def test_modificar_habitacion_inexistente_devuelve_none(habitacion_dao, conexion):
    resultado = habitacion_dao.modificar_habitacion(
        id_habitacion=999999999, 
        precio_noche=Decimal("50000.00"), 
        conexion_externa=conexion
    )

    assert resultado is None


# ---------- DELETE (baja lógica) ----------

def test_eliminar_habitacion_hace_baja_logica(habitacion_dao, habitacion_guardada, conexion):
    id_habitacion, _ = habitacion_guardada

    assert habitacion_dao.eliminar_habitacion(id_habitacion, conexion_externa=conexion) is True

    habitacion = habitacion_dao.obtener_habitacion_por_id(id_habitacion, conexion_externa=conexion)
    assert habitacion is not None  # la fila no se borra físicamente
    assert habitacion.get_activo() is False


def test_eliminar_habitacion_inexistente_devuelve_false(habitacion_dao, conexion):
    assert habitacion_dao.eliminar_habitacion(999999999, conexion_externa=conexion) is False