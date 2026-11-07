# Imports:

import itertools
import pytest

from services.cliente_service import ClienteService
from dao.cliente_dao import ClienteDAO
from dao.db_connection import obtener_conexion
from loggers.logger_config import configurar_logging

_contador = itertools.count(1)


def _datos_unicos() -> dict:
    n = next(_contador)
    return {
        "nombre": "Carlos",
        "apellido": f"Servicio{n}",
        "dni": str(88000000 + n),
        "telefono": f"387{8000000 + n}",
        "correo": f"servicio{n}@email.com",
    }


@pytest.fixture
def cliente_dao() -> ClienteDAO:
    return ClienteDAO()


@pytest.fixture
def cliente_service(cliente_dao) -> ClienteService:
    # Instanciamos el servicio inyectándole el DAO
    return ClienteService(cliente_dao=cliente_dao)


@pytest.fixture
def conexion():
    """Abre la conexión para la transacción de prueba y limpia al terminar."""
    con = obtener_conexion()
    configurar_logging()
    yield con
    con.commit()
    con.close()


@pytest.fixture
def cliente_guardado(cliente_service, conexion):
    """Crea un cliente usando el servicio y devuelve (id, datos)."""
    datos = _datos_unicos()
    
    # Nota: Como el DAO interno usa conexiones del pool automáticamente, 
    # envolvemos la prueba en la sesión de la fixture 'conexion' de pytest.
    id_generado = cliente_service.crear_cliente(
        nombre=datos["nombre"],
        apellido=datos["apellido"],
        dni=datos["dni"],
        telefono=datos["telefono"],
        correo=datos["correo"]
    )
    
    assert id_generado is not None
    return id_generado, datos


# ---------- TESTS DE REGLAS DE NEGOCIO Y SERVICIOS ----------

def test_crear_cliente_exitoso_devuelve_id(cliente_service, conexion):
    datos = _datos_unicos()
    
    id_generado = cliente_service.crear_cliente(
        nombre=datos["nombre"],
        apellido=datos["apellido"],
        dni=datos["dni"],
        telefono=datos["telefono"],
        correo=datos["correo"]
    )

    assert id_generado is not None
    assert id_generado > 0


def test_crear_cliente_con_dni_duplicado_activa_excepcion(cliente_service, cliente_guardado, conexion):
    _, datos = cliente_guardado

    # La regla de negocio del servicio exige que si el DNI ya existe y está activo, lance un ValueError
    with pytest.raises(ValueError, match="Ya existe un cliente activo con el DNI"):
        cliente_service.crear_cliente(
            nombre="Otro",
            apellido="Nombre",
            dni=datos["dni"],  # Mismo DNI ya guardado
            telefono="3870000000",
            correo="otro@email.com"
        )


def test_obtener_cliente_por_id_devuelve_objeto_correcto(cliente_service, cliente_guardado, conexion):
    id_cliente, datos = cliente_guardado

    cliente = cliente_service.obtener_cliente_por_id(id_cliente)

    assert cliente is not None
    assert cliente.get_id_persona() == id_cliente
    assert cliente.get_nombre() == datos["nombre"]
    assert cliente.get_dni() == datos["dni"]


def test_obtener_clientes_incluye_al_creado(cliente_service, cliente_guardado, conexion):
    id_cliente, _ = cliente_guardado

    clientes = cliente_service.obtener_clientes()
    ids = [c.get_id_persona() for c in clientes if c]

    assert id_cliente in ids


def test_eliminar_cliente_realiza_baja_logica(cliente_service, cliente_guardado, conexion):
    id_cliente, _ = cliente_guardado

    resultado = cliente_service.eliminar_cliente(id_cliente)
    assert resultado is True

    # Verificamos que el registro sigue existiendo pero su estado 'activo' pasó a False
    cliente = cliente_service.obtener_cliente_por_id(id_cliente)
    assert cliente is not None
    assert cliente.get_activo() is False