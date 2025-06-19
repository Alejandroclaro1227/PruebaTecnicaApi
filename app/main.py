"""
Event Processor API - Aplicación Principal
==========================================

API desarrollada en FastAPI para procesar eventos y encontrar el evento futuro más próximo.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import sys
from pathlib import Path

# Agregar el directorio padre al path para importaciones
sys.path.append(str(Path(__file__).parent.parent))

from .routes import events_router, health_router, main_router
from . import __version__, __description__

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)

logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(
    title="Event Processor API",
    description=__description__,
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Event Processor Team",
        "email": "contact@eventprocessor.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Configurar CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar hosts confiables (seguridad)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# Incluir routers
app.include_router(main_router)
app.include_router(events_router)
app.include_router(health_router)

# También mantener el endpoint original para compatibilidad
@app.post(
    "/process_events",
    response_model=None,
    summary="[LEGACY] Procesar eventos - Endpoint de compatibilidad",
    description="Endpoint legacy mantenido para compatibilidad. Use /events/process en su lugar.",
    deprecated=True,
    tags=["Legacy"]
)
async def process_events_legacy(request):
    """
    Endpoint legacy para compatibilidad con la versión anterior.
    Se recomienda usar /events/process en su lugar.
    """
    from .routes import process_events
    return await process_events(request)


@app.on_event("startup")
async def startup_event():
    """
    Eventos que se ejecutan al iniciar la aplicación.
    """
    logger.info("🚀 Event Processor API iniciándose...")
    logger.info(f"📊 Versión: {__version__}")
    logger.info("✅ Aplicación iniciada correctamente")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Eventos que se ejecutan al apagar la aplicación.
    """
    logger.info("🛑 Event Processor API cerrándose...")
    logger.info("✅ Aplicación cerrada correctamente")


# Punto de entrada para desarrollo local
if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Iniciando Event Processor API en modo desarrollo...")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
