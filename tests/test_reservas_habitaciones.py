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
    con = obtener_conexion()
    configurar_logging()
    yield con
    con.commit()
    con.close()

"""
@pytest.fixture
def contexto_asociacion_habitacion(reserva_dao, habitacion_dao, cliente_dao, conexion):
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
    assert len(habitaciones) == 0"""

# =========================================================================
# PRUEBAS PARA CREAR RESERVA COMPLETA (TRANSACCIONAL)
# =========================================================================

from services.reserva_service import ReservaService

@pytest.fixture
def reserva_service() -> ReservaService:
    return ReservaService(cliente_dao=ClienteDAO())


def test_crear_multiples_reservas_complejas_con_volumen(reserva_service, cliente_dao, habitacion_dao, conexion):
    """
    Test de integración avanzado:
    - Crea 3 clientes diferentes.
    - Crea 20 habitaciones con capacidades variadas (1 a 4 personas).
    - Ejecuta múltiples reservas complejas distribuyendo huéspedes y habitaciones,
      validando las relaciones N:M, capacidades y transacciones atómicas.
    """
    n = next(_contador)
    
    # 1. Creamos 3 clientes diferentes
    clientes_ids = []
    for i in range(3):
        dni = f"50{n:02d}{i:03d}"
        cliente = Cliente(
            id_cliente=None,
            nombre=f"ClienteMulti_{n}_{i}",
            apellido="Prueba",
            dni=dni,
            telefono="3871234567",
            correo=f"cliente{n}_{i}@mail.com",
            activo=True
        )
        id_cli = cliente_dao.crear_cliente(cliente, conexion_externa=conexion)
        assert id_cli is not None
        clientes_ids.append((id_cli, dni))

    # 2. Creamos 20 habitaciones con capacidades variadas (ej: 1 a 4 personas)
    habitaciones_creadas = []
    for i in range(20):
        capacidad = (i % 4) + 1  # Capacidades rotativas entre 1, 2, 3 y 4
        habitacion = Habitacion(
            id_habitacion=None,
            numero=7000 + (n * 100) + i,
            capacidad=capacidad,
            precio_noche=Decimal("25000.00") * capacidad,
            estado=EstadoHabitacion.DISPONIBLE,
            activo=True
        )
        id_hab = habitacion_dao.crear_habitacion(habitacion, conexion_externa=conexion)
        assert id_hab is not None
        habitaciones_creadas.append({"id": id_hab, "capacidad": capacidad})

    # 3. Armamos un conjunto de 10 huéspedes para distribuir en las reservas
    lista_huespedes_base = []
    for i in range(10):
        lista_huespedes_base.append({
            "nombre": f"Huesped_{n}_{i}",
            "apellido": f"Apellido_{i}",
            "dni": f"60{n:02d}{i:03d}",
            "telefono": "3871234567"
        })

    # 4. Primera Reserva Masiva: Cliente 0 reserva una habitación grande (capacidad 4) 
    # y aloja exactamente a 4 huéspedes.
    hab_grande = next(h for h in habitaciones_creadas if h["capacidad"] == 4)
    
    datos_reserva_1 = {
        "cliente": {"dni": clientes_ids[0][1]},
        "fechas": {
            "fecha_ingreso": date(2026, 12, 10),
            "fecha_salida": date(2026, 12, 15),
            "monto_total": 100000.00
        },
        "huespedes": [
            {**lista_huespedes_base[0], "id_habitacion": hab_grande["id"]},
            {**lista_huespedes_base[1], "id_habitacion": hab_grande["id"]},
            {**lista_huespedes_base[2], "id_habitacion": hab_grande["id"]},
            {**lista_huespedes_base[3], "id_habitacion": hab_grande["id"]}
        ]
    }
    
    id_res_1 = reserva_service.crear_reserva_completa(datos_reserva_1, conexion_externa=conexion)
    assert id_res_1 is not None

    # Verificamos que los 4 huéspedes y la habitación se hayan vinculado correctamente
    from dao.reservas_habitaciones_dao import ReservasHabitacionesDAO
    from dao.reservas_huespedes_dao import ReservasHuespedesDAO
    
    hab_dao = ReservasHabitacionesDAO()
    hue_dao = ReservasHuespedesDAO()

    assert len(hab_dao.obtener_habitaciones_por_reserva(id_res_1, conexion_externa=conexion)) == 1
    assert len(hue_dao.obtener_huespedes_por_reserva(id_res_1, conexion_externa=conexion)) == 4

    # 5. Segunda Reserva: Cliente 1 reserva 2 habitaciones distintas y distribuye a 4 huéspedes más
    hab_1 = habitaciones_creadas[5]["id"]
    hab_2 = habitaciones_creadas[6]["id"]

    datos_reserva_2 = {
        "cliente": {"dni": clientes_ids[1][1]},
        "fechas": {
            "fecha_ingreso": date(2027, 1, 10) if False else date(2027, 1, 10),
            "fecha_salida": date(2027, 1, 15),
            "monto_total": 150000.00
        },
        "huespedes": [
            {**lista_huespedes_base[4], "id_habitacion": hab_1},
            {**lista_huespedes_base[5], "id_habitacion": hab_1},
            {**lista_huespedes_base[6], "id_habitacion": hab_2},
            {**lista_huespedes_base[7], "id_habitacion": hab_2}
        ]
    }

    id_res_2 = reserva_service.crear_reserva_completa(datos_reserva_2, conexion_externa=conexion)
    assert id_res_2 is not None

    # Comprobamos que para esta reserva se asociaron 2 habitaciones y 4 huéspedes
    assert len(hab_dao.obtener_habitaciones_por_reserva(id_res_2, conexion_externa=conexion)) == 2
    assert len(hue_dao.obtener_huespedes_por_reserva(id_res_2, conexion_externa=conexion)) == 4

    # 6. Tercera Reserva: Cliente 2 utiliza los últimos 2 huéspedes restantes en una habitación de capacidad 2
    hab_individual = next(h for h in habitaciones_creadas if h["capacidad"] == 2 and h["id"] not in [hab_grande["id"], hab_1, hab_2])

    datos_reserva_3 = {
        "cliente": {"dni": clientes_ids[2][1]},
        "fechas": {
            "fecha_ingreso": date(2027, 2, 1),
            "fecha_salida": date(2027, 2, 5),
            "monto_total": 50000.00
        },
        "huespedes": [
            {**lista_huespedes_base[8], "id_habitacion": hab_individual["id"]},
            {**lista_huespedes_base[9], "id_habitacion": hab_individual["id"]}
        ]
    }

    id_res_3 = reserva_service.crear_reserva_completa(datos_reserva_3, conexion_externa=conexion)
    assert id_res_3 is not None
    assert len(hue_dao.obtener_huespedes_por_reserva(id_res_3, conexion_externa=conexion)) == 2