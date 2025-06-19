"""
Rutas de la Event Processor API
==============================

Este archivo contiene todas las rutas y endpoints de la API.
"""

from fastapi import APIRouter, HTTPException, status, Response
from typing import Optional
import logging

from .models import Event, EventsRequest, HealthResponse
from .services import EventProcessorService, HealthService

# Configurar logging
logger = logging.getLogger(__name__)

# Router principal para eventos
events_router = APIRouter(
    prefix="/events",
    tags=["Events"],
    responses={
        400: {"description": "Error de validación"},
        422: {"description": "Error de esquema"},
        500: {"description": "Error interno del servidor"}
    }
)

# Router para endpoints de salud
health_router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

# Router principal (sin prefijo)
main_router = APIRouter()


@main_router.get(
    "/",
    tags=["Health"],
    summary="Endpoint raíz",
    description="Endpoint básico para verificar que la API esté funcionando"
)
async def root():
    """
    Endpoint de salud para verificar que la API esté funcionando.
    """
    try:
        health_data = HealthService.get_health_status()
        return {
            "message": "Event Processor API está funcionando correctamente",
            "timestamp": health_data["timestamp"],
            "status": health_data["status"]
        }
    except Exception as e:
        logger.error(f"Error en endpoint raíz: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@events_router.post(
    "/process",
    response_model=Optional[Event],
    status_code=200,
    responses={
        200: {
            "description": "Evento futuro más próximo encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "event_id": "evt_002",
                        "timestamp": 1704153600,
                        "data": "Evento futuro"
                    }
                }
            }
        },
        204: {
            "description": "No se encontraron eventos válidos (futuros)"
        },
        400: {
            "description": "Error de validación en los datos de entrada"
        },
        422: {
            "description": "Error de validación de esquema"
        }
    },
    summary="Procesar lista de eventos",
    description="""
    Procesa una lista de eventos y devuelve el evento futuro más próximo.

    **Lógica:**
    1. Filtra eventos cuyo timestamp sea >= momento actual (UTC)
    2. De los eventos válidos, devuelve el que tenga el timestamp más alto
    3. Si no hay eventos válidos, devuelve 204 No Content

    **Validaciones adicionales:**
    - No se permiten event_ids duplicados
    - Los timestamps no pueden estar más de 10 años en el futuro
    - La lista no puede tener más de 1000 eventos

    **Parámetros:**
    - events: Lista de eventos con event_id, timestamp (epoch UTC) y data

    **Respuestas:**
    - 200: Evento futuro más próximo encontrado
    - 204: No hay eventos futuros válidos
    - 400/422: Errores de validación
    """
)
async def process_events(request: EventsRequest):
    """
    Procesa una lista de eventos y devuelve el evento futuro más próximo.

    Args:
        request: Objeto que contiene la lista de eventos a procesar

    Returns:
        Event: El evento con el timestamp más alto que sea >= al momento actual
        Response: 204 No Content si no hay eventos válidos

    Raises:
        HTTPException: Para errores de validación o procesamiento
    """
    try:
        # Validar reglas de negocio adicionales
        EventProcessorService.validate_events_business_rules(request.events)

        # Procesar eventos
        result = EventProcessorService.process_events(request)

        # Si no hay eventos futuros, devolver 204 No Content
        if result is None:
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        logger.info(f"Evento procesado exitosamente: {result.event_id}")
        return result

    except ValueError as e:
        logger.warning(f"Error de validación de negocio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error procesando eventos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al procesar los eventos"
        )


@health_router.get(
    "/",
    response_model=HealthResponse,
    summary="Verificación de salud",
    description="Endpoint de verificación de salud detallado con información del sistema"
)
async def health_check():
    """
    Endpoint de verificación de salud más detallado.
    """
    try:
        health_data = HealthService.get_health_status()
        return HealthResponse(**health_data)
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al verificar el estado de la aplicación"
        )


@health_router.get(
    "/dependencies",
    summary="Estado de dependencias",
    description="Verifica el estado de las dependencias del sistema"
)
async def check_dependencies():
    """
    Verifica el estado de las dependencias del sistema.
    """
    try:
        dependencies_info = HealthService.check_dependencies()
        return dependencies_info
    except Exception as e:
        logger.error(f"Error verificando dependencias: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al verificar las dependencias"
        )
