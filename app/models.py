"""
Modelos de datos para la Event Processor API
============================================

Este archivo contiene todos los modelos Pydantic utilizados en la API.
"""

from pydantic import BaseModel, Field, validator
from typing import List
from datetime import datetime


class Event(BaseModel):
    """
    Modelo para representar un evento.

    Attributes:
        event_id: Identificador único del evento
        timestamp: Timestamp en formato epoch UTC (segundos)
        data: Datos del evento
    """
    event_id: str = Field(
        ...,
        description="Identificador único del evento",
        min_length=1,
        example="evt_001"
    )
    timestamp: int = Field(
        ...,
        description="Timestamp en formato epoch UTC (segundos)",
        example=1704067200
    )
    data: str = Field(
        ...,
        description="Datos del evento",
        example="Evento de ejemplo"
    )

    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Valida que el timestamp sea un valor válido."""
        if v < 0:
            raise ValueError('El timestamp debe ser un valor positivo')
        return v

    @validator('event_id')
    def validate_event_id(cls, v):
        """Valida que el event_id no esté vacío y tenga formato válido."""
        if not v or not v.strip():
            raise ValueError('El event_id no puede estar vacío')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_001",
                "timestamp": 1704067200,
                "data": "Evento de ejemplo"
            }
        }


class EventsRequest(BaseModel):
    """
    Modelo para la solicitud de procesamiento de eventos.
    """
    events: List[Event] = Field(
        ...,
        description="Lista de eventos a procesar",
        min_items=1,
        max_items=1000  # Límite razonable para evitar sobrecarga
    )

    class Config:
        json_schema_extra = {
            "example": {
                "events": [
                    {
                        "event_id": "evt_001",
                        "timestamp": 1704067200,
                        "data": "Primer evento"
                    },
                    {
                        "event_id": "evt_002",
                        "timestamp": 1704153600,
                        "data": "Segundo evento"
                    }
                ]
            }
        }


class HealthResponse(BaseModel):
    """
    Modelo para la respuesta de salud de la API.
    """
    status: str = Field(
        description="Estado de la API",
        example="healthy"
    )
    timestamp: str = Field(
        description="Timestamp actual en formato ISO",
        example="2024-01-01T12:00:00"
    )
    current_epoch: int = Field(
        description="Timestamp actual en formato epoch UTC",
        example=1704067200
    )
    version: str = Field(
        description="Versión de la API",
        example="1.0.0"
    )


class ErrorResponse(BaseModel):
    """
    Modelo para respuestas de error.
    """
    detail: str = Field(
        description="Descripción del error",
        example="Error de validación en los datos"
    )
    error_code: str = Field(
        description="Código de error interno",
        example="VALIDATION_ERROR"
    )
