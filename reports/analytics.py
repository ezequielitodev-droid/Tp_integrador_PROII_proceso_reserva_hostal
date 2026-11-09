# Imports:

import pandas as pd


# Constants:


# Global Variables:


# Functions:


def convertir_reservas_dataframe(
        reservas: list
) -> pd.DataFrame:
    """
    Convierte las reservas obtenidas desde ReservaService
    en un DataFrame de Pandas.
    """

    datos = []

    for reserva, id_cliente in reservas:
        datos.append({
            "id_reserva": reserva.get_id_reserva(),
            "fecha_reserva": reserva.get_fecha_reserva(),
            "fecha_ingreso": reserva.get_fecha_ingreso(),
            "fecha_salida": reserva.get_fecha_salida(),
            "estado": reserva.get_estado().value,
            "activo": reserva.get_activo(),
            "id_cliente": id_cliente
        })

    df = pd.DataFrame(datos)

    if df.empty:
        return df

    # Convertimos las fechas para realizar cálculos.
    df["fecha_reserva"] = pd.to_datetime(df["fecha_reserva"])
    df["fecha_ingreso"] = pd.to_datetime(df["fecha_ingreso"])
    df["fecha_salida"] = pd.to_datetime(df["fecha_salida"])

    return df


def calcular_estadisticas(
        df: pd.DataFrame
) -> dict:
    """
    Calcula las estadísticas generales de las reservas.
    """

    if df.empty:
        return {
            "total": 0,
            "activas": 0,
            "canceladas": 0,
            "por_mes": pd.Series(dtype="int64"),
            "por_semana": pd.Series(dtype="int64"),
            "por_dia": pd.Series(dtype="int64"),
            "duracion_promedio": 0
        }

    # Identificamos las reservas canceladas.
    estado_cancelada = (
        df["estado"] == "cancelada"
    )

    # Identificamos las reservas canceladas o dadas de baja.
    reservas_canceladas = (
        (~df["activo"]) | estado_cancelada
    )

    reservas_activas = ~reservas_canceladas

    # Calculamos las estadísticas generales.
    total = len(df)
    activas = int(reservas_activas.sum())
    canceladas = int(reservas_canceladas.sum())

    # Agrupamos las reservas por mes.
    por_mes = df.groupby(
        df["fecha_reserva"].dt.to_period("M")
    ).size()

    # Agrupamos las reservas por semana.
    por_semana = df.groupby(
        df["fecha_reserva"].dt.to_period("W")
    ).size()

    # Agrupamos las reservas por día.
    por_dia = df.groupby(
        df["fecha_reserva"].dt.date
    ).size()

    # Calculamos la duración promedio de las reservas activas.
    duraciones = (
        df.loc[
            reservas_activas,
            "fecha_salida"
        ] - df.loc[
            reservas_activas,
            "fecha_ingreso"
        ]
    ).dt.days

    duracion_promedio = (
        float(duraciones.mean())
        if not duraciones.empty else 0
    )

    return {
        "total": total,
        "activas": activas,
        "canceladas": canceladas,
        "por_mes": por_mes,
        "por_semana": por_semana,
        "por_dia": por_dia,
        "duracion_promedio": duracion_promedio
    }
