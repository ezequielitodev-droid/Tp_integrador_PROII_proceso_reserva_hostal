#Imports:

import logging
from pathlib import Path

# Paths:
RAIZ = Path(__file__).resolve().parent.parent
PATH_LOG = RAIZ / "logs" / "app.log"

#Modulo instrumental:

def configurar_logging() -> None:
    
    PATH_LOG.parent.mkdir(parents=True, exist_ok=True)

    raiz = logging.getLogger()
    raiz.setLevel(logging.INFO)

    if raiz.handlers:
        raiz.handlers.clear()

    handler_app = logging.FileHandler(PATH_LOG, encoding="utf-8")
    handler_app.setLevel(logging.INFO)
    
    formato = logging.Formatter("%(asctime)s: [%(levelname)s] --- %(name)s ---> [%(message)s]")
    handler_app.setFormatter(formato)
    raiz.addHandler(handler_app)

    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(logging.INFO)
    handler_consola.setFormatter(formato)
    raiz.addHandler(handler_consola)