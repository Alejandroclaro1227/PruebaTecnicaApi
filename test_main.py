import pytest
from fastapi.testclient import TestClient
import time
from main import app

client = TestClient(app)


class TestProcessEvents:
    """Tests para el endpoint /process_events"""

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

        response = client.post("/process_events", json=payload)

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

        response = client.post("/process_events", json=payload)

        assert response.status_code == 204
        assert response.content == b""

    def test_process_events_mixed_events(self):
        """Test con eventos pasados y futuros - debe devolver solo el futuro más lejano"""
        past_timestamp = int(time.time()) - 3600
        current_timestamp = int(time.time())
        future_timestamp = int(time.time()) + 3600

        payload = {
            "events": [
                {
                    "event_id": "evt_past",
                    "timestamp": past_timestamp,
                    "data": "Evento pasado"
                },
                {
                    "event_id": "evt_current",
                    "timestamp": current_timestamp,
                    "data": "Evento actual"
                },
                {
                    "event_id": "evt_future",
                    "timestamp": future_timestamp,
                    "data": "Evento futuro"
                }
            ]
        }

        response = client.post("/process_events", json=payload)

        assert response.status_code == 200
        data = response.json()
        # Debe devolver el evento futuro o el actual (dependiendo del timing exacto)
        assert data["event_id"] in ["evt_current", "evt_future"]
        assert data["timestamp"] >= current_timestamp

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

        response = client.post("/process_events", json=invalid_payload)

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

        response = client.post("/process_events", json=payload)

        assert response.status_code == 422

    def test_process_events_empty_events_list(self):
        """Test con lista vacía de eventos - debe devolver 422"""
        payload = {
            "events": []  # Lista vacía (inválida por min_items=1)
        }

        response = client.post("/process_events", json=payload)

        assert response.status_code == 422


class TestHealthEndpoints:
    """Tests para los endpoints de salud"""

    def test_root_endpoint(self):
        """Test del endpoint raíz"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "timestamp" in data
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_check_endpoint(self):
        """Test del endpoint de verificación de salud"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "current_epoch" in data
        assert "version" in data
        assert isinstance(data["current_epoch"], int)


if __name__ == "__main__":
    pytest.main([__file__])
