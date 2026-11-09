
# Imports:

import logging
import pandas as pd

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QMessageBox,
    QScrollArea,
    QSizePolicy
)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from services.dashboard_service import DashboardService


# Constants:

COLOR_PRIMARIO = "#3978C5"
COLOR_ACTIVAS = "#36966B"
COLOR_CANCELADAS = "#D65B5B"
COLOR_DURACION = "#D69A38"
COLOR_TEXTO = "#263445"
COLOR_SECUNDARIO = "#718096"
COLOR_FONDO = "#F4F6FA"
COLOR_BORDE = "#E1E6EF"


# Global Variables:

logger = logging.getLogger(__name__)


# Class:

class PageDashboard(QWidget):

    # Constructor:

    def __init__(
            self,
            servicio_dashboard: DashboardService | None = None
    ):
        super().__init__()

        # Inyectamos la dependencia del servicio del dashboard
        self.servicio_dashboard = servicio_dashboard or DashboardService()

        # Inicializamos la interfaz
        self.init_ui()

        # Inicializamos las conexiones de señales y slots
        self.init_ui_connections()

        # Cargamos las estadísticas
        self.cargar_estadisticas()

    # Métodos de inicialización:

    def init_ui(self):

        # Configuración general de la página
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

        # Layout principal
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)

        # Área desplazable para el dashboard
        self.area_desplazable = QScrollArea()
        self.area_desplazable.setWidgetResizable(True)
        self.area_desplazable.setFrameShape(QFrame.NoFrame)

        self.contenido = QWidget()

        self.layout_contenido = QVBoxLayout(self.contenido)
        self.layout_contenido.setContentsMargins(20, 18, 20, 20)
        self.layout_contenido.setSpacing(16)

        # Encabezado del dashboard
        self.layout_encabezado = QHBoxLayout()

        self.titulo = QLabel("Panel de control")
        self.titulo.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            color: #263445;
        """)

        self.subtitulo = QLabel("Resumen general de reservas")
        self.subtitulo.setStyleSheet("""
            font-size: 12px;
            color: #718096;
        """)

        self.layout_titulos = QVBoxLayout()
        self.layout_titulos.addWidget(self.titulo)
        self.layout_titulos.addWidget(self.subtitulo)

        self.BotonActualizar = QPushButton("Actualizar")

        self.layout_encabezado.addLayout(self.layout_titulos)
        self.layout_encabezado.addStretch()
        self.layout_encabezado.addWidget(self.BotonActualizar)

        self.layout_contenido.addLayout(self.layout_encabezado)

        # Tarjetas de estadísticas
        self.layout_tarjetas = QGridLayout()
        self.layout_tarjetas.setSpacing(12)

        self.tarjeta_total, self.valor_total = self.crear_tarjeta(
            "Total de reservas",
            COLOR_PRIMARIO
        )

        self.tarjeta_activas, self.valor_activas = self.crear_tarjeta(
            "Reservas activas",
            COLOR_ACTIVAS
        )

        self.tarjeta_canceladas, self.valor_canceladas = self.crear_tarjeta(
            "Reservas canceladas",
            COLOR_CANCELADAS
        )

        self.tarjeta_duracion, self.valor_duracion = self.crear_tarjeta(
            "Duración promedio",
            COLOR_DURACION
        )

        self.layout_tarjetas.addWidget(self.tarjeta_total, 0, 0)
        self.layout_tarjetas.addWidget(self.tarjeta_activas, 0, 1)
        self.layout_tarjetas.addWidget(self.tarjeta_canceladas, 1, 0)
        self.layout_tarjetas.addWidget(self.tarjeta_duracion, 1, 1)

        self.layout_contenido.addLayout(self.layout_tarjetas)

        # Sección de gráficos
        self.titulo_graficos = QLabel("Actividad de reservas")

        self.titulo_graficos.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #263445;
        """)

        self.layout_contenido.addWidget(self.titulo_graficos)

        # Contenedores de gráficos
        self.layout_graficos = QVBoxLayout()
        self.layout_graficos.setSpacing(14)

        (
            self.contenedor_mes,
            self.eje_mes,
            self.canvas_mes
        ) = self.crear_grafico("Reservas por mes")

        (
            self.contenedor_semana,
            self.eje_semana,
            self.canvas_semana
        ) = self.crear_grafico("Reservas por semana")

        (
            self.contenedor_dia,
            self.eje_dia,
            self.canvas_dia
        ) = self.crear_grafico("Reservas por día")

        self.layout_graficos.addWidget(self.contenedor_mes)
        self.layout_graficos.addWidget(self.contenedor_semana)
        self.layout_graficos.addWidget(self.contenedor_dia)

        self.layout_contenido.addLayout(self.layout_graficos)

        # Espacio final
        self.layout_contenido.addStretch()

        # Incorporamos el contenido al área desplazable
        self.area_desplazable.setWidget(self.contenido)
        self.layout_principal.addWidget(self.area_desplazable)

    # Métodos de creación de componentes:

    def crear_tarjeta(
            self,
            titulo: str,
            color: str
    ) -> tuple[QFrame, QLabel]:
        """
        Crea una tarjeta visual para mostrar una estadística.
        """

        tarjeta = QFrame()
        tarjeta.setMinimumHeight(105)

        tarjeta.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        tarjeta.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {COLOR_BORDE};
                border-left: 4px solid {color};
                border-radius: 9px;
            }}
        """)

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(13, 12, 10, 12)
        layout.setSpacing(8)

        etiqueta_titulo = QLabel(titulo)
        etiqueta_titulo.setWordWrap(True)

        etiqueta_titulo.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #718096;
            border: none;
            background: transparent;
        """)

        etiqueta_valor = QLabel("0")

        etiqueta_valor.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            color: #263445;
            border: none;
            background: transparent;
        """)

        layout.addWidget(etiqueta_titulo)
        layout.addWidget(etiqueta_valor)

        return tarjeta, etiqueta_valor

    def crear_grafico(
            self,
            titulo: str
    ) -> tuple[QFrame, object, FigureCanvas]:
        """
        Crea un contenedor con un gráfico de Matplotlib.
        """

        contenedor = QFrame()
        contenedor.setMinimumHeight(300)

        contenedor.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        contenedor.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {COLOR_BORDE};
                border-radius: 9px;
            }}
        """)

        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(5)

        etiqueta_titulo = QLabel(titulo)

        etiqueta_titulo.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #263445;
            border: none;
            background: transparent;
        """)

        figura = Figure(
            figsize=(8, 3),
            dpi=100,
            facecolor="white"
        )

        eje = figura.add_subplot(111)

        canvas = FigureCanvas(figura)
        canvas.setMinimumHeight(245)

        canvas.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        layout.addWidget(etiqueta_titulo)
        layout.addWidget(canvas)

        return contenedor, eje, canvas

    # Métodos conectores:

    def init_ui_connections(self):

        self.BotonActualizar.clicked.connect(
            self.cargar_estadisticas
        )

    # Métodos estratégicos:

    def cargar_estadisticas(self):
        """
        Obtiene las estadísticas desde DashboardService
        y actualiza los indicadores y gráficos.
        """

        try:

            estadisticas = self.servicio_dashboard.obtener_estadisticas()

            # Actualizamos las tarjetas
            self.valor_total.setText(
                str(estadisticas["total"])
            )

            self.valor_activas.setText(
                str(estadisticas["activas"])
            )

            self.valor_canceladas.setText(
                str(estadisticas["canceladas"])
            )

            self.valor_duracion.setText(
                f'{estadisticas["duracion_promedio"]:.1f} días'
            )

            # Actualizamos los gráficos
            self.actualizar_grafico(
                self.eje_mes,
                estadisticas["por_mes"],
                COLOR_PRIMARIO,
                "mes"
            )

            self.actualizar_grafico(
                self.eje_semana,
                estadisticas["por_semana"],
                COLOR_ACTIVAS,
                "semana"
            )

            self.actualizar_grafico(
                self.eje_dia,
                estadisticas["por_dia"],
                COLOR_DURACION,
                "dia"
            )

        except Exception as e:

            logger.exception(
                "Error al cargar las estadísticas del dashboard."
            )

            QMessageBox.warning(
                self,
                "Error",
                f"No se pudieron cargar las estadísticas: {e}"
            )

    def actualizar_grafico(
            self,
            eje,
            datos,
            color: str,
            tipo: str
    ):
        """
        Actualiza un gráfico de puntos con los datos recibidos
        desde Pandas, completando los períodos sin reservas con cero.
        """

        eje.clear()

        if datos is None or datos.empty:

            eje.text(
                0.5,
                0.5,
                "No hay datos disponibles",
                ha="center",
                va="center",
                transform=eje.transAxes,
                color=COLOR_SECUNDARIO,
                fontsize=11
            )

            eje.set_xticks([])
            eje.set_yticks([])

        else:

            # Fecha actual
            hoy = pd.Timestamp.today().normalize()

            # Completamos los períodos según el tipo de gráfico
            if tipo == "mes":

                datos.index = pd.PeriodIndex(
                    datos.index,
                    freq="M"
                )

                periodos = pd.period_range(
                    end=hoy.to_period("M"),
                    periods=12,
                    freq="M"
                )

                datos = datos.reindex(
                    periodos,
                    fill_value=0
                )

            elif tipo == "semana":

                datos.index = pd.PeriodIndex(
                    datos.index,
                    freq="W"
                )

                periodos = pd.period_range(
                    end=hoy.to_period("W"),
                    periods=12,
                    freq="W"
                )

                datos = datos.reindex(
                    periodos,
                    fill_value=0
                )

            elif tipo == "dia":

                datos.index = pd.to_datetime(
                    datos.index
                ).normalize()

                periodos = pd.date_range(
                    end=hoy,
                    periods=14,
                    freq="D"
                )

                datos = datos.reindex(
                    periodos,
                    fill_value=0
                )

            # Generamos etiquetas legibles
            etiquetas = [
                self.formatear_etiqueta(fecha, tipo)
                for fecha in datos.index
            ]

            valores = datos.to_numpy(dtype=float)

            posiciones = list(range(len(etiquetas)))

            # Dibujamos la línea que conecta los puntos
            eje.plot(
                posiciones,
                valores,
                color=color,
                linewidth=1.8,
                alpha=0.65,
                zorder=2
            )

            # Dibujamos los puntos
            eje.scatter(
                posiciones,
                valores,
                color=color,
                s=65,
                edgecolors="white",
                linewidths=1.5,
                zorder=3
            )

            # Mostramos los valores encima de los puntos
            for x, y in zip(posiciones, valores):

                if y > 0:

                    eje.annotate(
                        str(int(y)),
                        (x, y),
                        textcoords="offset points",
                        xytext=(0, 9),
                        ha="center",
                        fontsize=9,
                        color=COLOR_TEXTO
                    )

            # Configuración de los ejes
            eje.set_xticks(posiciones)

            eje.set_xticklabels(
                etiquetas,
                fontsize=8
            )

            eje.set_ylabel(
                "Reservas",
                fontsize=9,
                color=COLOR_SECUNDARIO,
                labelpad=8
            )

            # Límites del eje vertical
            maximo = max(valores)

            eje.set_ylim(
                0,
                max(maximo * 1.25, 1)
            )

            # Márgenes horizontales
            eje.margins(x=0.05)

            # Configuración de etiquetas
            eje.tick_params(
                axis="y",
                labelsize=9,
                colors=COLOR_SECUNDARIO
            )

            eje.tick_params(
                axis="x",
                labelsize=8,
                colors=COLOR_SECUNDARIO,
                pad=7
            )

            # Rotamos las fechas del gráfico diario
            if tipo == "dia":

                eje.tick_params(
                    axis="x",
                    labelrotation=35
                )

            # Mejoramos la cuadrícula
            eje.grid(
                axis="y",
                linestyle="--",
                alpha=0.25
            )

            eje.set_axisbelow(True)

            # Quitamos los bordes superiores y derechos
            eje.spines["top"].set_visible(False)
            eje.spines["right"].set_visible(False)

            eje.spines["left"].set_color(
                COLOR_BORDE
            )

            eje.spines["bottom"].set_color(
                COLOR_BORDE
            )

        # Ajustamos los márgenes para evitar recortes
        eje.figure.tight_layout(pad=2.0)

        # Actualizamos la representación visual
        eje.figure.canvas.draw_idle()

    # Métodos auxiliares:

    def formatear_etiqueta(
            self,
            fecha,
            tipo: str
    ) -> str:
        """
        Convierte las fechas en etiquetas legibles para los gráficos.
        """

        meses = [
            "Ene", "Feb", "Mar", "Abr",
            "May", "Jun", "Jul", "Ago",
            "Sep", "Oct", "Nov", "Dic"
        ]

        if tipo == "mes":

            return (
                f"{meses[fecha.month - 1]} "
                f"{fecha.year}"
            )

        elif tipo == "semana":

            fecha_inicio = fecha.start_time
            numero_semana = fecha_inicio.isocalendar().week

            return (
                f"Sem. {numero_semana}\n"
                f"{fecha_inicio.year}"
            )

        elif tipo == "dia":

            return fecha.strftime("%d/%m")

        return str(fecha)
