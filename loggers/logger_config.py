# Imports:

import logging
from pathlib import Path

# Paths:
RAIZ = Path(__file__).resolve().parent.parent
FOLDER_LOGS = RAIZ / "logs"
PATH_LOG_DAOS = FOLDER_LOGS / "dao_logs.log"
PATH_LOG_SERVICES = FOLDER_LOGS / "service_logs.log"
PATH_LOG_GUI = FOLDER_LOGS / "gui_logs.log"
PATH_LOG_BACKUPS = FOLDER_LOGS / "backup_logs.log"  # <--- Nuevo path para backups


# Modulo instrumental:

def configurar_logging() -> None:

    # Creamos la carpeta de logs si no existe
    FOLDER_LOGS.mkdir(parents=True, exist_ok=True)

    # Formato común para todos los logs
    formato = logging.Formatter("%(asctime)s: [%(levelname)s] --- %(name)s ---> [%(message)s]")

    # 1. Configurar Handler para Consola
    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(logging.INFO)
    handler_consola.setFormatter(formato)

    # 2. Configurar Handler y Logger específico para DAOs
    logger_dao = logging.getLogger("dao")
    logger_dao.setLevel(logging.INFO)
    logger_dao.propagate = False  # Evita que se dupliquen los mensajes en el root
    if logger_dao.handlers:
        logger_dao.handlers.clear()
    
    handler_dao = logging.FileHandler(PATH_LOG_DAOS, encoding="utf-8")
    handler_dao.setLevel(logging.INFO)
    handler_dao.setFormatter(formato)
    
    logger_dao.addHandler(handler_dao)
    logger_dao.addHandler(handler_consola)  # También imprime DAOs por consola

    # 3. Configurar Handler y Logger específico para Services
    logger_service = logging.getLogger("services")
    logger_service.setLevel(logging.INFO)
    logger_service.propagate = False
    if logger_service.handlers:
        logger_service.handlers.clear()
    
    handler_service = logging.FileHandler(PATH_LOG_SERVICES, encoding="utf-8")
    handler_service.setLevel(logging.INFO)
    handler_service.setFormatter(formato)
    
    logger_service.addHandler(handler_service)
    logger_service.addHandler(handler_consola)  # También imprime Servicios por consola

    # 4. Configurar Handler y Logger específico para GUI
    logger_gui = logging.getLogger("views") # O "gui" dependiendo de cómo nombres tu paquete de vistas
    logger_gui.setLevel(logging.INFO)
    logger_gui.propagate = False
    if logger_gui.handlers:
        logger_gui.handlers.clear()
    
    handler_gui = logging.FileHandler(PATH_LOG_GUI, encoding="utf-8")
    handler_gui.setLevel(logging.INFO)
    handler_gui.setFormatter(formato)
    
    logger_gui.addHandler(handler_gui)
    logger_gui.addHandler(handler_consola)  # También imprime GUI por consola

    # 5. Configurar Handler y Logger específico para Backups
    logger_backup = logging.getLogger("backups")
    logger_backup.setLevel(logging.INFO)
    logger_backup.propagate = False
    if logger_backup.handlers:
        logger_backup.handlers.clear()
    
    handler_backup = logging.FileHandler(PATH_LOG_BACKUPS, encoding="utf-8")
    handler_backup.setLevel(logging.INFO)
    handler_backup.setFormatter(formato)
    
    logger_backup.addHandler(handler_backup)
    logger_backup.addHandler(handler_consola)  # También imprime Backups por consola