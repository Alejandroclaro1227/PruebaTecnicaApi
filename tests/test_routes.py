"""
Tests para las rutas de la Event Processor API
==============================================
"""

import pytest
from fastapi.testclient import TestClient
import time

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)


class TestMainRoutes:
    """Tests para las rutas principales"""

    def test_root_endpoint(self):
        """Test del endpoint raíz"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "timestamp" in data
        assert "status" in data
        assert data["status"] == "healthy"
        assert "Event Processor API" in data["message"]


class TestEventRoutes:
    """Tests para las rutas de eventos"""

    def test_process_events_with_future_events(self):
        """Test con eventos futuros - debe devolver el evento más lejano"""
        future_timestamp_1 = int(time.time()) + 3600  # +1 hora
        future_timestamp_2 = int(time.time()) + 7200  # +2 horas

        payload = {
            "events": [
                {
                    "event_id": "evt_001",
                    "timestamp": future_timestamp_1,
                    "data": "Evento futuro 1"
                },
                {
                    "event_id": "evt_002",
                    "timestamp": future_timestamp_2,
                    "data": "Evento futuro 2"
                }
            ]
        }

        response = client.post("/events/process", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["event_id"] == "evt_002"
        assert data["timestamp"] == future_timestamp_2
        assert data["data"] == "Evento futuro 2"

    def test_process_events_no_future_events(self):
        """Test sin eventos futuros - debe devolver 204"""
        past_timestamp = int(time.time()) - 3600  # -1 hora

        payload = {
            "events": [
                {
                    "event_id": "evt_001",
                    "timestamp": past_timestamp,
                    "data": "Evento pasado"
                }
            ]
        }

        response = client.post("/events/process", json=payload)

        assert response.status_code == 204
        assert response.content == b""

    def test_process_events_duplicate_ids(self):
        """Test con IDs duplicados - debe devolver 400"""
        future_timestamp = int(time.time()) + 3600

        payload = {
            "events": [
                {
                    "event_id": "evt_001",
                    "timestamp": future_timestamp,
                    "data": "Evento 1"
                },
                {
                    "event_id": "evt_001",  # ID duplicado
                    "timestamp": future_timestamp + 1800,
                    "data": "Evento 2"
                }
            ]
        }

        response = client.post("/events/process", json=payload)

        assert response.status_code == 400
        assert "duplicados" in response.json()["detail"]

    def test_process_events_invalid_payload(self):
        """Test con payload inválido - debe devolver 422"""
        invalid_payload = {
            "events": [
                {
                    "event_id": "",  # ID vacío (inválido por min_length=1)
                    "timestamp": 1234567890,
                    "data": "Datos de prueba"
                }
            ]
        }

        response = client.post("/events/process", json=invalid_payload)

        assert response.status_code == 422

    def test_process_events_negative_timestamp(self):
        """Test con timestamp negativo - debe devolver 422"""
        payload = {
            "events": [
                {
                    "event_id": "evt_001",
                    "timestamp": -1,  # Timestamp negativo (inválido)
                    "data": "Evento con timestamp negativo"
                }
            ]
        }

        response = client.post("/events/process", json=payload)

        assert response.status_code == 422

    def test_process_events_empty_events_list(self):
        """Test con lista vacía de eventos - debe devolver 422"""
        payload = {
            "events": []  # Lista vacía (inválida por min_items=1)
        }

        response = client.post("/events/process", json=payload)

        assert response.status_code == 422

    def test_process_events_legacy_endpoint(self):
        """Test del endpoint legacy para compatibilidad"""
        future_timestamp = int(time.time()) + 3600

        payload = {
            "events": [
                {
                    "event_id": "evt_legacy",
                    "timestamp": future_timestamp,
                    "data": "Evento legacy"
                }
            ]
        }

        response = client.post("/process_events", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["event_id"] == "evt_legacy"


class TestHealthRoutes:
    """Tests para las rutas de salud"""

    def test_health_check_endpoint(self):
        """Test del endpoint de verificación de salud"""
        response = client.get("/health/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "current_epoch" in data
        assert "version" in data
        assert isinstance(data["current_epoch"], int)

    def test_health_dependencies_endpoint(self):
        """Test del endpoint de verificación de dependencias"""
        response = client.get("/health/dependencies")

        assert response.status_code == 200
        data = response.json()
        assert "python_version" in data
        assert "platform" in data
        assert "dependencies_status" in data
        assert data["dependencies_status"] == "ok"


class TestAPIDocumentation:
    """Tests para la documentación automática"""

    def test_openapi_schema(self):
        """Test del esquema OpenAPI"""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Event Processor API"

    def test_swagger_ui(self):
        """Test de Swagger UI"""
        response = client.get("/docs")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc(self):
        """Test de ReDoc"""
        response = client.get("/redoc")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
