"""
Tests para los servicios de la Event Processor API
=================================================
"""

import pytest
import time
from unittest.mock import patch

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.models import Event, EventsRequest
from app.services import EventProcessorService, HealthService


class TestEventProcessorService:
    """Tests para el EventProcessorService"""

    def test_get_current_timestamp(self):
        """Test para obtener timestamp actual"""
        timestamp = EventProcessorService.get_current_timestamp()
        assert isinstance(timestamp, int)
        assert timestamp > 0

        # Verificar que esté cerca del tiempo actual
        current_time = int(time.time())
        assert abs(timestamp - current_time) <= 1  # Diferencia máxima de 1 segundo

    def test_filter_future_events(self):
        """Test para filtrar eventos futuros"""
        current_timestamp = int(time.time())

        events = [
            Event(event_id="past", timestamp=current_timestamp - 3600, data="Pasado"),
            Event(event_id="current", timestamp=current_timestamp, data="Actual"),
            Event(event_id="future", timestamp=current_timestamp + 3600, data="Futuro"),
        ]

        future_events = EventProcessorService.filter_future_events(events, current_timestamp)

        assert len(future_events) == 2
        assert future_events[0].event_id == "current"
        assert future_events[1].event_id == "future"

    def test_filter_future_events_empty_list(self):
        """Test para filtrar eventos con lista vacía"""
        events = []
        future_events = EventProcessorService.filter_future_events(events)
        assert len(future_events) == 0

    def test_find_latest_event(self):
        """Test para encontrar el evento más tardío"""
        events = [
            Event(event_id="evt1", timestamp=1000, data="Primero"),
            Event(event_id="evt2", timestamp=3000, data="Último"),
            Event(event_id="evt3", timestamp=2000, data="Medio"),
        ]

        latest = EventProcessorService.find_latest_event(events)

        assert latest is not None
        assert latest.event_id == "evt2"
        assert latest.timestamp == 3000

    def test_find_latest_event_empty_list(self):
        """Test para encontrar evento en lista vacía"""
        events = []
        latest = EventProcessorService.find_latest_event(events)
        assert latest is None

    def test_process_events_with_future_events(self):
        """Test para procesar eventos con eventos futuros"""
        future_timestamp = int(time.time()) + 3600

        request = EventsRequest(events=[
            Event(event_id="evt1", timestamp=future_timestamp, data="Futuro 1"),
            Event(event_id="evt2", timestamp=future_timestamp + 1800, data="Futuro 2"),
        ])

        result = EventProcessorService.process_events(request)

        assert result is not None
        assert result.event_id == "evt2"
        assert result.timestamp == future_timestamp + 1800

    def test_process_events_no_future_events(self):
        """Test para procesar eventos sin eventos futuros"""
        past_timestamp = int(time.time()) - 3600

        request = EventsRequest(events=[
            Event(event_id="evt1", timestamp=past_timestamp, data="Pasado"),
        ])

        result = EventProcessorService.process_events(request)

        assert result is None

    def test_validate_events_business_rules_valid(self):
        """Test para validar reglas de negocio con eventos válidos"""
        events = [
            Event(event_id="evt1", timestamp=int(time.time()) + 3600, data="Evento 1"),
            Event(event_id="evt2", timestamp=int(time.time()) + 7200, data="Evento 2"),
        ]

        # No debe lanzar excepción
        assert EventProcessorService.validate_events_business_rules(events) is True

    def test_validate_events_business_rules_duplicate_ids(self):
        """Test para validar reglas de negocio con IDs duplicados"""
        events = [
            Event(event_id="evt1", timestamp=int(time.time()) + 3600, data="Evento 1"),
            Event(event_id="evt1", timestamp=int(time.time()) + 7200, data="Evento 2"),
        ]

        with pytest.raises(ValueError, match="No se permiten event_ids duplicados"):
            EventProcessorService.validate_events_business_rules(events)

    def test_validate_events_business_rules_far_future(self):
        """Test para validar reglas de negocio con timestamps muy futuros"""
        # Timestamp más de 10 años en el futuro
        far_future = int(time.time()) + (11 * 365 * 24 * 60 * 60)

        events = [
            Event(event_id="evt1", timestamp=far_future, data="Muy futuro"),
        ]

        with pytest.raises(ValueError, match="demasiado lejos en el futuro"):
            EventProcessorService.validate_events_business_rules(events)


class TestHealthService:
    """Tests para el HealthService"""

    def test_get_health_status(self):
        """Test para obtener estado de salud"""
        health_data = HealthService.get_health_status()

        assert isinstance(health_data, dict)
        assert health_data["status"] == "healthy"
        assert "timestamp" in health_data
        assert "current_epoch" in health_data
        assert "version" in health_data
        assert isinstance(health_data["current_epoch"], int)

    def test_check_dependencies(self):
        """Test para verificar dependencias"""
        deps_info = HealthService.check_dependencies()

        assert isinstance(deps_info, dict)
        assert "python_version" in deps_info
        assert "platform" in deps_info
        assert "dependencies_status" in deps_info
        assert deps_info["dependencies_status"] == "ok"
