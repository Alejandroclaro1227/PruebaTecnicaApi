"""
Servicios de negocio para la Event Processor API
===============================================

Este archivo contiene la lógica de negocio para el procesamiento de eventos.
"""

import time
from typing import List, Optional
from .models import Event, EventsRequest


class EventProcessorService:
    """
    Servicio principal para el procesamiento de eventos.
    """

    @staticmethod
    def get_current_timestamp() -> int:
        """
        Obtiene el timestamp actual en formato epoch UTC.

        Returns:
            int: Timestamp actual en segundos
        """
        return int(time.time())

    @staticmethod
    def filter_future_events(events: List[Event], current_timestamp: Optional[int] = None) -> List[Event]:
        """
        Filtra eventos que tengan timestamp >= al momento actual.

        Args:
            events: Lista de eventos a filtrar
            current_timestamp: Timestamp de referencia (opcional, usa el actual si no se proporciona)

        Returns:
            List[Event]: Lista de eventos futuros válidos
        """
        if current_timestamp is None:
            current_timestamp = EventProcessorService.get_current_timestamp()

        return [
            event for event in events
            if event.timestamp >= current_timestamp
        ]

    @staticmethod
    def find_latest_event(events: List[Event]) -> Optional[Event]:
        """
        Encuentra el evento con el timestamp más alto de una lista.

        Args:
            events: Lista de eventos

        Returns:
            Optional[Event]: El evento con el timestamp más alto, o None si la lista está vacía
        """
        if not events:
            return None

        return max(events, key=lambda event: event.timestamp)

    @classmethod
    def process_events(cls, request: EventsRequest) -> Optional[Event]:
        """
        Procesa una lista de eventos y devuelve el evento futuro más próximo.

        Args:
            request: Objeto que contiene la lista de eventos a procesar

        Returns:
            Optional[Event]: El evento con el timestamp más alto que sea >= al momento actual,
                           o None si no hay eventos válidos
        """
        # Obtener timestamp actual
        current_timestamp = cls.get_current_timestamp()

        # Filtrar eventos futuros
        future_events = cls.filter_future_events(request.events, current_timestamp)

        # Si no hay eventos futuros, devolver None
        if not future_events:
            return None

        # Encontrar el evento con el timestamp más alto
        latest_event = cls.find_latest_event(future_events)

        return latest_event

    @staticmethod
    def validate_events_business_rules(events: List[Event]) -> bool:
        """
        Valida reglas de negocio adicionales para los eventos.

        Args:
            events: Lista de eventos a validar

        Returns:
            bool: True si todos los eventos cumplen las reglas de negocio

        Raises:
            ValueError: Si algún evento no cumple las reglas de negocio
        """
        # Verificar que no haya event_ids duplicados
        event_ids = [event.event_id for event in events]
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("No se permiten event_ids duplicados")

        # Verificar que los timestamps estén en un rango razonable
        # (no más de 10 años en el futuro)
        current_time = int(time.time())
        max_future_time = current_time + (10 * 365 * 24 * 60 * 60)  # 10 años

        for event in events:
            if event.timestamp > max_future_time:
                raise ValueError(f"El timestamp del evento {event.event_id} está demasiado lejos en el futuro")

        return True


class HealthService:
    """
    Servicio para verificar la salud de la aplicación.
    """

    @staticmethod
    def get_health_status() -> dict:
        """
        Obtiene el estado de salud de la aplicación.

        Returns:
            dict: Información del estado de la aplicación
        """
        from datetime import datetime, timezone

        # Obtener versión desde el módulo app
        try:
            from app import __version__
        except ImportError:
            __version__ = "1.0.0"

        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_epoch": int(time.time()),
            "version": __version__
        }

    @staticmethod
    def check_dependencies() -> dict:
        """
        Verifica el estado de las dependencias del sistema.

        Returns:
            dict: Estado de las dependencias
        """
        import sys
        import platform

        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "dependencies_status": "ok"
        }
