# Imports:

import logging
from pathlib import Path
import pandas as pd

from PyQt5.QtWidgets import (
    QWidget,
    QMessageBox,
    QSizePolicy
)
from PyQt5 import uic

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from services.dashboard_service import DashboardService


# Constants:

COLOR_PRIMARIO = "#3978C5"
COLOR_ACTIVAS = "#36966B"
COLOR_CANCELADAS = "#D65B5B"
COLOR_DURACION = "#D69A38"
COLOR_TEXTO = "#263445"
COLOR_SECUNDARIO = "#718096"
COLOR_FONDO = "#323232"

# Ruta del archivo UI
UI_PATH = Path(__file__).resolve().parent / "page_dashboard.ui"


# Global Variables:

# Apuntamos al parlante específico de la capa de GUI / Vistas
logger = logging.getLogger("views.GUI.page_dashboard")


# Class:

class PageDashboard(QWidget):

    def __init__(
            self,
            servicio_dashboard: DashboardService | None = None
    ):
        super().__init__()

        # Inyectamos la dependencia del servicio del dashboard
        self.servicio_dashboard = servicio_dashboard or DashboardService()

        # Cargamos la interfaz desde el archivo .ui
        uic.loadUi(UI_PATH, self)
        logger.info("Interfaz de PageDashboard cargada correctamente desde el archivo UI.")

        # Aplicamos estilos generales de la ventana
        self.init_styles()

        # Inicializamos los gráficos de Matplotlib incrustándolos en los QFrame del UI
        self.init_graficos()

        # Inicializamos las conexiones de señales y slots
        self.init_ui_connections()

        # Cargamos las estadísticas iniciales
        self.cargar_estadisticas()

    def init_styles(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLOR_FONDO};
                color: {COLOR_TEXTO};
                font-family: Segoe UI;
            }}
            QPushButton {{
                background-color: {COLOR_PRIMARIO};
                color: white;
                border: none;
                border-radius: 7px;
                padding: 9px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2863A9;
            }}
            QPushButton:pressed {{
                background-color: #204F87;
            }}
        """)

    def init_graficos(self):
        """Crea los canvas de Matplotlib y los añade a los layouts de los QFrame del UI."""
        
        # 1. Gráfico Mes
        self.eje_mes, self.canvas_mes = crear_canvas_en_contenedor(self.layout_g_mes)
        
        # 2. Gráfico Semana
        self.eje_semana, self.canvas_semana = crear_canvas_en_contenedor(self.layout_g_semana)
        
        # 3. Gráfico Día
        self.eje_dia, self.canvas_dia = crear_canvas_en_contenedor(self.layout_g_dia)
        
        logger.info("Canvas de gráficos para mes, semana y día inicializados con éxito.")

    def init_ui_connections(self):
        self.BotonActualizar.clicked.connect(self.cargar_estadisticas)
        logger.info("Conexiones de botones en PageDashboard inicializadas.")

    def cargar_estadisticas(self):
        try:
            logger.info("Iniciando carga y actualización de estadísticas en el dashboard...")
            estadisticas = self.servicio_dashboard.obtener_estadisticas()

            # Actualizamos las tarjetas del UI
            self.valor_total.setText(str(estadisticas["total"]))
            self.valor_activas.setText(str(estadisticas["activas"]))
            self.valor_canceladas.setText(str(estadisticas["canceladas"]))
            self.valor_duracion.setText(f'{estadisticas["duracion_promedio"]:.1f} días')

            # Actualizamos los gráficos
            self.actualizar_grafico(self.eje_mes, estadisticas["por_mes"], COLOR_PRIMARIO, "mes")
            self.actualizar_grafico(self.eje_semana, estadisticas["por_semana"], COLOR_ACTIVAS, "semana")
            self.actualizar_grafico(self.eje_dia, estadisticas["por_dia"], COLOR_DURACION, "dia")

            logger.info("Estadísticas y gráficos del dashboard actualizados correctamente en la interfaz.")

        except Exception as e:
            logger.exception("Error crítico al cargar las estadísticas del dashboard en la GUI.")
            QMessageBox.warning(self, "Error", f"No se pudieron cargar las estadísticas: {e}")

    def actualizar_grafico(self, eje, datos, color: str, tipo: str):
        eje.clear()

        if datos is None or datos.empty:
            eje.text(0.5, 0.5, "No hay datos disponibles", ha="center", va="center", transform=eje.transAxes, color=COLOR_SECUNDARIO, fontsize=11)
            eje.set_xticks([])
            eje.set_yticks([])
            logger.debug(f"Gráfico tipo '{tipo}' renderizado sin datos (vacío).")
        else:
            hoy = pd.Timestamp.today().normalize()

            if tipo == "mes":
                datos.index = pd.PeriodIndex(datos.index, freq="M")
                periodos = pd.period_range(end=hoy.to_period("M"), periods=12, freq="M")
                datos = datos.reindex(periodos, fill_value=0)
            elif tipo == "semana":
                datos.index = pd.PeriodIndex(datos.index, freq="W")
                periodos = pd.period_range(end=hoy.to_period("W"), periods=12, freq="W")
                datos = datos.reindex(periodos, fill_value=0)
            elif tipo == "dia":
                datos.index = pd.to_datetime(datos.index).normalize()
                periodos = pd.date_range(end=hoy, periods=14, freq="D")
                datos = datos.reindex(periodos, fill_value=0)

            etiquetas = [self.formatear_etiqueta(fecha, tipo) for fecha in datos.index]
            valores = datos.to_numpy(dtype=float)
            posiciones = list(range(len(etiquetas)))

            eje.plot(posiciones, valores, color=color, linewidth=1.8, alpha=0.65, zorder=2)
            eje.scatter(posiciones, valores, color=color, s=65, edgecolors="white", linewidths=1.5, zorder=3)

            for x, y in zip(posiciones, valores):
                if y > 0:
                    eje.annotate(str(int(y)), (x, y), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9, color=COLOR_TEXTO)

            eje.set_xticks(posiciones)
            eje.set_xticklabels(etiquetas, fontsize=8)
            eje.set_ylabel("Reservas", fontsize=9, color=COLOR_SECUNDARIO, labelpad=8)

            maximo = max(valores) if len(valores) > 0 else 1
            eje.set_ylim(0, max(maximo * 1.25, 1))
            eje.margins(x=0.05)
            eje.tick_params(axis="y", labelsize=9, colors=COLOR_SECUNDARIO)
            eje.tick_params(axis="x", labelsize=8, colors=COLOR_SECUNDARIO, pad=7)

            if tipo == "dia":
                eje.tick_params(axis="x", labelrotation=35)

            eje.grid(axis="y", linestyle="--", alpha=0.25)
            eje.set_axisbelow(True)
            eje.spines["top"].set_visible(False)
            eje.spines["right"].set_visible(False)
            eje.spines["left"].set_color("#232323")
            eje.spines["bottom"].set_color("#232323")
            
            logger.debug(f"Gráfico tipo '{tipo}' actualizado con éxito.")

        eje.figure.tight_layout(pad=2.0)
        eje.figure.canvas.draw_idle()

    def formatear_etiqueta(self, fecha, tipo: str) -> str:
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        if tipo == "mes":
            return f"{meses[fecha.month - 1]} {fecha.year}"
        elif tipo == "semana":
            fecha_inicio = fecha.start_time
            numero_semana = fecha_inicio.isocalendar().week
            return f"Sem. {numero_semana}\n{fecha_inicio.year}"
        elif tipo == "dia":
            return fecha.strftime("%d/%m")
        return str(fecha)


def crear_canvas_en_contenedor(layout_contenedor):
    """Función auxiliar para instanciar el gráfico y añadirlo al layout del QFrame."""
    figura = Figure(figsize=(8, 3), dpi=100, facecolor="white")
    eje = figura.add_subplot(111)
    canvas = FigureCanvas(figura)
    canvas.setMinimumHeight(245)
    canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    layout_contenedor.addWidget(canvas)
    return eje, canvas