# Imports:

import itertools
import pytest
from decimal import Decimal

from services.habitacion_service import HabitacionService
from dao.habitacion_dao import HabitacionDAO
from dao.db_connection import obtener_conexion
from loggers.logger_config import configurar_logging
from utils.datatypes.EstadoHabitacion import EstadoHabitacion

_contador = itertools.count(500)  # Empezamos desde un número alto para evitar colisiones


def _numero_unico() -> int:
    return next(_contador)


@pytest.fixture
def habitacion_dao() -> HabitacionDAO:
    return HabitacionDAO()


@pytest.fixture
def habitacion_service(habitacion_dao) -> HabitacionService:
    # Inyectamos el DAO en el servicio
    return HabitacionService(habitacion_dao=habitacion_dao)


@pytest.fixture
def conexion():
    """Abre la conexión para la transacción de prueba y asegura commit/rollback."""
    con = obtener_conexion()
    configurar_logging()
    yield con
    con.commit()
    con.close()


@pytest.fixture
def habitacion_guardada(habitacion_service, conexion):
    """Crea una habitación válida usando el servicio para usarla en los tests."""
    num = _numero_unico()
    id_generado = habitacion_service.crear_habitacion(
        numero=num,
        capacidad=2,
        precio_noche=Decimal("45000.00"),
        estado=EstadoHabitacion.DISPONIBLE
    )
    assert id_generado is not None
    return id_generado, num


# ---------- TESTS DE REGLAS DE NEGOCIO Y SERVICIOS ----------

def test_crear_habitacion_exitosa_devuelve_id(habitacion_service, conexion):
    num = _numero_unico()
    
    id_generado = habitacion_service.crear_habitacion(
        numero=num,
        capacidad=3,
        precio_noche=Decimal("60000.00"),
        estado=EstadoHabitacion.DISPONIBLE
    )

    assert id_generado is not None
    assert id_generado > 0


def test_crear_habitacion_con_numero_duplicado_activa_excepcion(habitacion_service, habitacion_guardada, conexion):
    _, num_existente = habitacion_guardada

    # Intentar registrar otra habitación activa con el mismo número físico debe fallar
    with pytest.raises(ValueError, match="Ya existe una habitación activa con el número"):
        habitacion_service.crear_habitacion(
            numero=num_existente,
            capacidad=1,
            precio_noche=Decimal("30000.00")
        )


def test_crear_habitacion_con_capacidad_invalida_activa_excepcion(habitacion_service, conexion):
    num = _numero_unico()
    
    # La capacidad permitida por los validadores es [1, 2, 3, 4]
    with pytest.raises(ValueError, match="La capacidad.*no es válida"):
        habitacion_service.crear_habitacion(
            numero=num,
            capacidad=5,  # Inválida
            precio_noche=Decimal("50000.00")
        )


def test_crear_habitacion_con_precio_negativo_activa_excepcion(habitacion_service, conexion):
    num = _numero_unico()
    
    with pytest.raises(ValueError, match="El precio por noche no es válido"):
        habitacion_service.crear_habitacion(
            numero=num,
            capacidad=2,
            precio_noche=Decimal("-1000.00")  # Negativo
        )


def test_obtener_habitacion_por_id_devuelve_objeto_correcto(habitacion_service, habitacion_guardada, conexion):
    id_habitacion, num = habitacion_guardada

    habitacion = habitacion_service.obtener_habitacion_por_id(id_habitacion)

    assert habitacion is not None
    assert habitacion.get_id_habitacion() == id_habitacion
    assert habitacion.get_numero() == num
    assert habitacion.get_capacidad() == 2
    assert habitacion.get_precio_noche() == Decimal("45000.00")


def test_obtener_habitaciones_incluye_a_la_creada(habitacion_service, habitacion_guardada, conexion):
    id_habitacion, _ = habitacion_guardada

    habitaciones = habitacion_service.obtener_habitaciones()
    ids = [h.get_id_habitacion() for h in habitaciones if h]

    assert id_habitacion in ids


def test_modificar_habitacion_actualiza_correctamente(habitacion_service, habitacion_guardada, conexion):
    id_habitacion, _ = habitacion_guardada

    habitacion_modificada = habitacion_service.modificar_habitacion(
        id_habitacion=id_habitacion,
        capacidad=4,
        precio_noche=Decimal("80000.00")
    )

    assert habitacion_modificada is not None
    assert habitacion_modificada.get_capacidad() == 4
    assert habitacion_modificada.get_precio_noche() == Decimal("80000.00")


def test_eliminar_habitacion_realiza_baja_logica(habitacion_service, habitacion_guardada, conexion):
    id_habitacion, _ = habitacion_guardada

    resultado = habitacion_service.eliminar_habitacion(id_habitacion)
    assert resultado is True

    # Verificamos que el estado activo pasó a False
    habitacion = habitacion_service.obtener_habitacion_por_id(id_habitacion)
    assert habitacion is not None
    assert habitacion.get_activo() is False