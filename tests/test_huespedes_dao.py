# Imports:

import itertools
import pytest

from dao.db_connection import obtener_conexion
from dao.huesped_dao import HuespedDAO
from models.huesped import Huesped
from loggers.logger_config import configurar_logging

_contador = itertools.count(1)


def _datos_unicos() -> dict:
    n = next(_contador)
    return {
        "nombre": "Martín",
        "apellido": f"Huésped{n}",
        "dni": str(88000000 + n),
        "telefono": f"387{8000000 + n}",
    }


def _armar_huesped(datos: dict) -> Huesped:
    return Huesped(
        id_huesped=None,
        nombre=datos["nombre"],
        apellido=datos["apellido"],
        dni=datos["dni"],
        telefono=datos["telefono"],
        activo=True,
    )


@pytest.fixture
def huesped_dao() -> HuespedDAO:
    return HuespedDAO()


@pytest.fixture
def conexion():
    """Abre la conexión antes del test y la cierra automáticamente al terminar."""
    con = obtener_conexion()
    configurar_logging()
    yield con
    con.commit()
    con.close()


@pytest.fixture
def huesped_guardado(huesped_dao, conexion):
    # Guarda un huésped nuevo usando la conexión y devuelve (id, datos)
    datos = _datos_unicos()
    id_generado = huesped_dao.crear_huesped(_armar_huesped(datos), conexion_externa=conexion)
    assert id_generado is not None
    return id_generado, datos


# ---------- CREATE ----------

def test_crear_huesped_devuelve_un_id_positivo(huesped_dao, conexion):
    id_generado = huesped_dao.crear_huesped(_armar_huesped(_datos_unicos()), conexion_externa=conexion)

    assert id_generado is not None
    assert id_generado > 0


def test_crear_huesped_con_dni_duplicado_devuelve_none(huesped_dao, huesped_guardado, conexion):
    _, datos = huesped_guardado

    id_repetido = huesped_dao.crear_huesped(_armar_huesped(datos), conexion_externa=conexion)

    assert id_repetido is None


# ---------- READ ----------

def test_obtener_huesped_por_id_devuelve_sus_datos(huesped_dao, huesped_guardado, conexion):
    id_huesped, datos = huesped_guardado

    huesped = huesped_dao.obtener_huesped_por_id(id_huesped, conexion_externa=conexion)

    assert huesped is not None
    assert huesped.get_id_persona() == id_huesped
    assert huesped.get_nombre() == datos["nombre"]
    assert huesped.get_apellido() == datos["apellido"]
    assert huesped.get_dni() == datos["dni"]
    assert huesped.get_telefono() == datos["telefono"]
    assert huesped.get_activo() is True


def test_obtener_huesped_por_dni_devuelve_sus_datos(huesped_dao, huesped_guardado, conexion):
    id_huesped, datos = huesped_guardado
    dni_buscado = datos["dni"]

    huesped = huesped_dao.obtener_huesped_por_dni(dni_buscado, conexion_externa=conexion)

    assert huesped is not None
    assert huesped.get_id_persona() == id_huesped
    assert huesped.get_dni() == dni_buscado
    assert huesped.get_nombre() == datos["nombre"]


def test_obtener_huesped_por_dni_inexistente_devuelve_none(huesped_dao, conexion):
    assert huesped_dao.obtener_huesped_por_dni("00000000", conexion_externa=conexion) is None


def test_obtener_huesped_por_id_inexistente_devuelve_none(huesped_dao, conexion):
    assert huesped_dao.obtener_huesped_por_id(999999999, conexion_externa=conexion) is None


def test_obtener_huespedes_incluye_los_huespedes_creados(huesped_dao, huesped_guardado, conexion):
    id_huesped, _ = huesped_guardado

    ids = [h.get_id_persona() for h in huesped_dao.obtener_huespedes(conexion_externa=conexion) if h]

    assert id_huesped in ids


# ---------- UPDATE ----------

def test_modificar_huesped_cambia_solo_el_campo_indicado(huesped_dao, huesped_guardado, conexion):
    id_huesped, datos = huesped_guardado

    modificado = huesped_dao.modificar_huesped(id_huesped=id_huesped, telefono="3871111111", conexion_externa=conexion)

    assert modificado is not None
    assert modificado.get_telefono() == "3871111111"
    assert modificado.get_nombre() == datos["nombre"]


def test_modificar_huesped_queda_guardado_en_la_base(huesped_dao, huesped_guardado, conexion):
    id_huesped, _ = huesped_guardado
    huesped_dao.modificar_huesped(id_huesped=id_huesped, telefono="3871111111", conexion_externa=conexion)

    recuperado = huesped_dao.obtener_huesped_por_id(id_huesped, conexion_externa=conexion)

    assert recuperado is not None
    assert recuperado.get_telefono() == "3871111111"


def test_modificar_huesped_inexistente_devuelve_none(huesped_dao, conexion):
    resultado = huesped_dao.modificar_huesped(id_huesped=999999999, telefono="3871111111", conexion_externa=conexion)

    assert resultado is None


# ---------- DELETE (baja lógica) ----------

def test_eliminar_huesped_hace_baja_logica(huesped_dao, huesped_guardado, conexion):
    id_huesped, _ = huesped_guardado

    assert huesped_dao.eliminar_huesped(id_huesped, conexion_externa=conexion) is True

    huesped = huesped_dao.obtener_huesped_por_id(id_huesped, conexion_externa=conexion)
    assert huesped is not None  # la fila no se borra
    assert huesped.get_activo() is False


def test_eliminar_huesped_inexistente_devuelve_false(huesped_dao, conexion):
    assert huesped_dao.eliminar_huesped(999999999, conexion_externa=conexion) is False