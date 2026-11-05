#Imports:

import logging
from pathlib import Path

# Paths:
RAIZ = Path(__file__).resolve().parent.parent
PATH_LOG = RAIZ / "logs" / "app.log"

#Modulo instrumental:

def configurar_logging() -> None:
    
    """
        Configura el sistema de registro (logging) global de la vista.

        Establece un manejador de archivos (`app.log`) con codificación UTF-8,
        define el nivel mínimo de registro en INFO y establece un formato
        estándar para todos los mensajes. Se recomienda llamarlo una única vez
        al inicio de la ejecución desde el archivo principal (`main.py`).

        Returns:
            None

        Examples:
            Así es como se debe invocar la función al arrancar la aplicación en `main.py`:

            >>> if __name__ == "__main__":
            ...     configurar_logging()
            ...     logger = logging.getLogger(__name__)
            ...     logger.info("Vista iniciada correctamente.")

        Note:
            Los registros se almacenarán localmente en el archivo 'app.log'
            ubicado en la raíz del proyecto.
    """

    PATH_LOG.parent.mkdir(parents=True, exist_ok=True)

    #Definicion de parlantes:
    handler_app = logging.FileHandler(PATH_LOG, encoding="utf-8")

    #Configuración del parlante:
    handler_app.setLevel(logging.INFO)
    formato = logging.Formatter("%(asctime)s: [%(levelname)s] --- %(name)s ---> [%(message)s]")
    handler_app.setFormatter(formato)

    #Configuracion de la consola:
    raiz = logging.getLogger()
    raiz.setLevel(logging.INFO)
    raiz.addHandler(handler_app)