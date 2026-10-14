
import logging
from pathlib import Path

# Obtenemos la carpeta principal del proyecto.
BASE_DIR = Path(__file__).resolve().parent

# Creamos la carpeta logs si todavía no existe.
CARPETA_LOGS = BASE_DIR / "logs"
CARPETA_LOGS.mkdir(exist_ok=True)

# Definimos dónde se guardarán los eventos de la aplicación.
ARCHIVO_LOG = CARPETA_LOGS / "app.log"

# Configuramos el sistema de registros.
logging.basicConfig(
    level=logging.INFO,  # Registramos INFO, WARNING, ERROR y niveles superiores.
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        # Guardamos los eventos en un archivo.
        logging.FileHandler(ARCHIVO_LOG, encoding="utf-8"),

        # También mostramos los eventos en la terminal.
        logging.StreamHandler(),
    ],
)

# Creamos un registrador reutilizable para la aplicación.
logger = logging.getLogger("billetera")
