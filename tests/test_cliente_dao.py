# Imports:

import itertools
import pytest

from dao.db_connection import obtener_conexion
from dao.cliente_dao import ClienteDAO
from models.cliente import Cliente

_contador = itertools.count(1)


def _datos_unicos() -> dict:
    n = next(_contador)
    return {
        "nombre": "Carlos",
        "apellido": f"Prueba{n}",
        "dni": str(77000000 + n),
        "telefono": f"387{7000000 + n}",
        "correo": f"prueba{n}@email.com",
    }


def _armar_cliente(datos: dict) -> Cliente:
    return Cliente(
        id_cliente=None,
        nombre=datos["nombre"],
        apellido=datos["apellido"],
        dni=datos["dni"],
        telefono=datos["telefono"],
        correo=datos["correo"],
        activo=True,
    )


@pytest.fixture
def cliente_dao() -> ClienteDAO:
    return ClienteDAO()


@pytest.fixture
def conexion():
    """Abre la conexión antes del test y la cierra automáticamente al terminar."""
    con = obtener_conexion()
    yield con
    con.commit()
    con.close()


@pytest.fixture
def cliente_guardado(cliente_dao, conexion):
    #Guarda un cliente nuevo usando la conexión y devuelve (id, datos)
    datos = _datos_unicos()
    id_generado = cliente_dao.crear_cliente(_armar_cliente(datos), conexion_externa=conexion)
    assert id_generado is not None
    return id_generado, datos


# ---------- CREATE ----------

def test_crear_cliente_devuelve_un_id_positivo(cliente_dao, conexion):
    id_generado = cliente_dao.crear_cliente(_armar_cliente(_datos_unicos()), conexion_externa=conexion)

    assert id_generado is not None
    assert id_generado > 0


def test_crear_cliente_con_dni_duplicado_devuelve_none(cliente_dao, cliente_guardado, conexion):
    _, datos = cliente_guardado

    id_repetido = cliente_dao.crear_cliente(_armar_cliente(datos), conexion_externa=conexion)

    assert id_repetido is None


# ---------- READ ----------

def test_obtener_cliente_por_id_devuelve_sus_datos(cliente_dao, cliente_guardado, conexion):
    id_cliente, datos = cliente_guardado

    cliente = cliente_dao.obtener_cliente_por_id(id_cliente, conexion_externa=conexion)

    assert cliente is not None
    assert cliente.get_id_persona() == id_cliente
    assert cliente.get_nombre() == datos["nombre"]
    assert cliente.get_apellido() == datos["apellido"]
    assert cliente.get_dni() == datos["dni"]
    assert cliente.get_telefono() == datos["telefono"]
    assert cliente.get_correo() == datos["correo"]
    assert cliente.get_activo() is True


def test_obtener_cliente_por_id_inexistente_devuelve_none(cliente_dao, conexion):
    assert cliente_dao.obtener_cliente_por_id(999999999, conexion_externa=conexion) is None


def test_obtener_clientes_incluye_los_clientes_creados(cliente_dao, cliente_guardado, conexion):
    id_cliente, _ = cliente_guardado

    ids = [c.get_id_persona() for c in cliente_dao.obtener_clientes(conexion_externa=conexion) if c]

    assert id_cliente in ids


# ---------- UPDATE ----------

def test_modificar_cliente_cambia_solo_el_campo_indicado(cliente_dao, cliente_guardado, conexion):
    id_cliente, datos = cliente_guardado

    modificado = cliente_dao.modificar_cliente(id_cliente=id_cliente, telefono="3879999999", conexion_externa=conexion)

    assert modificado is not None
    assert modificado.get_telefono() == "3879999999"
    assert modificado.get_nombre() == datos["nombre"]


def test_modificar_cliente_queda_guardado_en_la_base(cliente_dao, cliente_guardado, conexion):
    id_cliente, _ = cliente_guardado
    cliente_dao.modificar_cliente(id_cliente=id_cliente, telefono="3879999999", conexion_externa=conexion)

    recuperado = cliente_dao.obtener_cliente_por_id(id_cliente, conexion_externa=conexion)

    assert recuperado is not None
    assert recuperado.get_telefono() == "3879999999"


def test_modificar_cliente_inexistente_devuelve_none(cliente_dao, conexion):
    resultado = cliente_dao.modificar_cliente(id_cliente=999999999, telefono="3879999999", conexion_externa=conexion)

    assert resultado is None


# ---------- DELETE (baja lógica) ----------

def test_eliminar_cliente_hace_baja_logica(cliente_dao, cliente_guardado, conexion):
    id_cliente, _ = cliente_guardado

    assert cliente_dao.eliminar_cliente(id_cliente, conexion_externa=conexion) is True

    cliente = cliente_dao.obtener_cliente_por_id(id_cliente, conexion_externa=conexion)
    assert cliente is not None  # la fila no se borra
    assert cliente.get_activo() is False


def test_eliminar_cliente_inexistente_devuelve_false(cliente_dao, conexion):
    assert cliente_dao.eliminar_cliente(999999999, conexion_externa=conexion) is False