from abc import ABC
from unittest.mock import Mock

import pytest

from models import persona
from models.huesped import Huesped
from models.persona import Persona

# Lista de validadores que le interesan a Huesped
NOMBRES_VALIDADORES = [
    "es_id_persona_valido",
    "es_nombre_valido",
    "es_apellido_valido",
    "es_dni_valido",
    "es_telefono_valido",
]

DATOS = {
    "id_huesped": 1,
    "nombre": "Lucía",
    "apellido": "Pérez",
    "dni": "40111222",
    "telefono": "3874001122",
}


@pytest.fixture
def validadores(monkeypatch):
    """Reemplaza los validadores de persona por mocks que devuelven True."""
    mocks = {}
    for nombre in NOMBRES_VALIDADORES:
        mock = Mock(return_value=True)
        monkeypatch.setattr(persona, nombre, mock)
        mocks[nombre] = mock

    # Mockea el correo para que devuelva True por defecto y no rompa super().__init__
    mock_correo = Mock(return_value=True)
    monkeypatch.setattr(persona, "es_correo_valido", mock_correo)
    mocks["es_correo_valido"] = mock_correo

    return mocks


# ---------- Construcción y getters ----------

def test_construccion_valida_no_lanza_error(validadores):
    huesped = Huesped(**DATOS)
    assert isinstance(huesped, Huesped)


@pytest.mark.parametrize(
    "campo, getter",
    [
        ("id_huesped", "get_id_persona"),
        ("nombre", "get_nombre"),
        ("apellido", "get_apellido"),
        ("dni", "get_dni"),
        ("telefono", "get_telefono"),
    ],
)
def test_getters_devuelven_lo_recibido(validadores, campo, getter):
    huesped = Huesped(**DATOS)
    assert getattr(huesped, getter)() == DATOS[campo]


def test_id_huesped_puede_ser_none(validadores):
    datos = {**DATOS, "id_huesped": None}
    huesped = Huesped(**datos)
    assert huesped.get_id_persona() is None
    validadores["es_id_persona_valido"].assert_called_once_with(None)


# ---------- Uso de los validadores ----------

@pytest.mark.parametrize(
    "validador, campo",
    [
        ("es_id_persona_valido", "id_huesped"),
        ("es_nombre_valido", "nombre"),
        ("es_apellido_valido", "apellido"),
        ("es_dni_valido", "dni"),
        ("es_telefono_valido", "telefono"),
    ],
)
def test_cada_validador_recibe_su_valor(validadores, validador, campo):
    Huesped(**DATOS)
    validadores[validador].assert_called_once_with(DATOS[campo])


# ---------- Datos inválidos ----------

@pytest.mark.parametrize(
    "validador, mensaje",
    [
        ("es_id_persona_valido", "Identificador unico invalido"),
        ("es_nombre_valido", "Nombre invalido"),
        ("es_apellido_valido", "Apellido invalido"),
        ("es_dni_valido", "DNI invalido"),
        ("es_telefono_valido", "Telefono invalido"),
    ],
)
def test_validador_falso_lanza_value_error(validadores, validador, mensaje):
    validadores[validador].return_value = False
    with pytest.raises(ValueError, match=mensaje):
        Huesped(**DATOS)


def test_se_corta_en_el_primer_dato_invalido(validadores):
    validadores["es_nombre_valido"].return_value = False
    with pytest.raises(ValueError, match="Nombre invalido"):
        Huesped(**DATOS)
    validadores["es_apellido_valido"].assert_not_called()
    validadores["es_dni_valido"].assert_not_called()
    validadores["es_telefono_valido"].assert_not_called()


def test_con_varios_datos_invalidos_falla_primero_el_id(validadores):
    validadores["es_id_persona_valido"].return_value = False
    validadores["es_nombre_valido"].return_value = False
    with pytest.raises(ValueError, match="Identificador unico invalido"):
        Huesped(**DATOS)


# ---------- Encapsulamiento y herencia ----------

def test_atributos_privados_no_son_accesibles_desde_afuera(validadores):
    huesped = Huesped(**DATOS)
    with pytest.raises(AttributeError):
        _ = huesped.__nombre


def test_atributos_privados_se_guardan_con_name_mangling(validadores):
    huesped = Huesped(**DATOS)
    assert huesped._Persona__nombre == DATOS["nombre"]


def test_huesped_hereda_de_persona():
    assert issubclass(Huesped, Persona)