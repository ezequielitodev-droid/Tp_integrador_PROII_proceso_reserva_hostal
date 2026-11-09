# Imports:

import logging
import pandas as pd
from services.reserva_service import ReservaService
from reports.analytics import (
    convertir_reservas_dataframe,
    calcular_estadisticas
)


# Constants:


# Global Variables:

logger = logging.getLogger(__name__)


# Class:

class DashboardService:

    # Constructor:

    def __init__(
            self,
            reserva_service: ReservaService | None = None
    ):
        # Inyectamos la dependencia del servicio de reservas
        self.reserva_service = reserva_service or ReservaService()

    # Métodos estratégicos:

    def obtener_dataframe_reservas(self) -> pd.DataFrame:
        """
        Obtiene las reservas y las convierte en un DataFrame.
        """

        reservas = self.reserva_service.obtener_reservas()

        return convertir_reservas_dataframe(reservas)

    def obtener_estadisticas(self) -> dict:
        """
        Obtiene las reservas y calcula las estadísticas
        necesarias para el dashboard.
        """

        df = self.obtener_dataframe_reservas()

        return calcular_estadisticas(df)
