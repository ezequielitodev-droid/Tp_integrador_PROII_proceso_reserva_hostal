# Imports:

import itertools
import pytest

from services.huesped_service import HuespedService
from dao.huesped_dao import HuespedDAO
from dao.reserva_dao import ReservaDAO
from dao.db_connection import obtener_conexion
from loggers.logger_config import configurar_logging

_contador = itertools.count(1)


def _datos_unicos() -> dict:
    n = next(_contador)
    return {
        "nombre": "Lucía",
        "apellido": f"HuespedPrueba{n}",
        "dni": str(99000000 + n),
        "telefono": f"387{9000000 + n}",
        "correo": f"huesped{n}@email.com",
    }


@pytest.fixture
def huesped_dao() -> HuespedDAO:
    return HuespedDAO()


@pytest.fixture
def reserva_dao() -> ReservaDAO:
    return ReservaDAO()


@pytest.fixture
def huesped_service(huesped_dao, reserva_dao) -> HuespedService:
    # Instanciamos el servicio inyectándole los DAOs correspondientes
    return HuespedService(huesped_dao=huesped_dao, reserva_dao=reserva_dao)


@pytest.fixture
def conexion():
    """Abre la conexión para la transacción de prueba y limpia al terminar."""
    con = obtener_conexion()
    configurar_logging()
    yield con
    con.commit()
    con.close()


@pytest.fixture
def huesped_guardado(huesped_service, conexion):
    """Crea un huésped usando el servicio y devuelve (id, datos)."""
    datos = _datos_unicos()
    
    id_generado = huesped_service.crear_huesped(
        nombre=datos["nombre"],
        apellido=datos["apellido"],
        dni=datos["dni"],
        telefono=datos["telefono"],
        correo=datos["correo"]
    )
    
    assert id_generado is not None
    return id_generado, datos


# ---------- TESTS DE REGLAS DE NEGOCIO Y SERVICIOS ----------

def test_crear_huesped_exitoso_devuelve_id(huesped_service, conexion):
    datos = _datos_unicos()
    
    id_generado = huesped_service.crear_huesped(
        nombre=datos["nombre"],
        apellido=datos["apellido"],
        dni=datos["dni"],
        telefono=datos["telefono"],
        correo=datos["correo"]
    )

    assert id_generado is not None
    assert id_generado > 0


def test_crear_huesped_con_dni_duplicado_activa_excepcion(huesped_service, huesped_guardado, conexion):
    _, datos = huesped_guardado

    # La regla de negocio exige que si el DNI ya existe y está activo, lance un ValueError
    with pytest.raises(ValueError, match="Ya existe un huésped activo con el DNI"):
        huesped_service.crear_huesped(
            nombre="Otro",
            apellido="Huesped",
            dni=datos["dni"],  # Mismo DNI ya guardado
            telefono="3870000000",
            correo="otro_huesped@email.com"
        )


def test_obtener_huesped_por_id_devuelve_objeto_correcto(huesped_service, huesped_guardado, conexion):
    id_huesped, datos = huesped_guardado

    huesped = huesped_service.obtener_huesped_por_id(id_huesped)

    assert huesped is not None
    assert huesped.get_id_persona() == id_huesped
    assert huesped.get_nombre() == datos["nombre"]
    assert huesped.get_dni() == datos["dni"]


def test_obtener_huesped_por_dni_devuelve_objeto_correcto(huesped_service, huesped_guardado, conexion):
    id_huesped, datos = huesped_guardado
    dni_buscado = datos["dni"]

    huesped = huesped_service.obtener_huesped_por_dni(dni_buscado)

    assert huesped is not None
    assert huesped.get_id_persona() == id_huesped
    assert huesped.get_dni() == dni_buscado


def test_obtener_huespedes_incluye_al_creado(huesped_service, huesped_guardado, conexion):
    id_huesped, _ = huesped_guardado

    huespedes = huesped_service.obtener_huespedes()
    ids = [h.get_id_persona() for h in huespedes if h]

    assert id_huesped in ids


def test_eliminar_huesped_realiza_baja_logica(huesped_service, huesped_guardado, conexion):
    id_huesped, _ = huesped_guardado

    resultado = huesped_service.eliminar_huesped(id_huesped)
    assert resultado is True

    # Verificamos que el registro sigue existiendo pero su estado 'activo' pasó a False
    huesped = huesped_service.obtener_huesped_por_id(id_huesped)
    assert huesped is not None
    assert huesped.get_activo() is False