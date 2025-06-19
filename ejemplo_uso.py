"""
Ejemplo de uso de la Event Processor API
=========================================

Este archivo demuestra cómo usar la API tanto con requests como con ejemplos de curl.
"""

import requests
import time
import json

# URL base de la API (ajustar según tu configuración)
BASE_URL = "http://localhost:8000"

# NOTA: Los endpoints han cambiado en la nueva estructura
# Nuevo endpoint: /events/process
# Endpoint legacy: /process_events (mantenido para compatibilidad)

def test_api_with_future_events():
    """
    Ejemplo con eventos futuros - debería devolver el evento más lejano
    """
    print("🧪 Test 1: Eventos futuros")

    # Crear timestamps futuros
    future_1 = int(time.time()) + 3600  # +1 hora
    future_2 = int(time.time()) + 7200  # +2 horas

    payload = {
        "events": [
            {
                "event_id": "evt_001",
                "timestamp": future_1,
                "data": "Evento en 1 hora"
            },
            {
                "event_id": "evt_002",
                "timestamp": future_2,
                "data": "Evento en 2 horas"
            }
        ]
    }

    try:
        response = requests.post(f"{BASE_URL}/process_events", json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Evento seleccionado: {result['event_id']}")
            print(f"Timestamp: {result['timestamp']}")
            print(f"Data: {result['data']}")
        print()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar a la API. ¿Está ejecutándose en localhost:8000?")
        print()

def test_api_with_past_events():
    """
    Ejemplo con eventos pasados - debería devolver 204 No Content
    """
    print("🧪 Test 2: Eventos pasados (204 No Content)")

    # Crear timestamp pasado
    past_timestamp = int(time.time()) - 3600  # -1 hora

    payload = {
        "events": [
            {
                "event_id": "evt_past",
                "timestamp": past_timestamp,
                "data": "Evento que ya pasó"
            }
        ]
    }

    try:
        response = requests.post(f"{BASE_URL}/process_events", json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 204:
            print("✅ Correcto: No hay eventos futuros")
        else:
            print("❌ Respuesta inesperada")
        print()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar a la API")
        print()

def test_api_health():
    """
    Probar los endpoints de salud
    """
    print("🏥 Test: Endpoints de salud")

    try:
        # Test endpoint raíz
        response = requests.get(f"{BASE_URL}/")
        print(f"GET /: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")

        # Test endpoint health
        response = requests.get(f"{BASE_URL}/health")
        print(f"GET /health: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Current epoch: {data.get('current_epoch')}")
        print()

    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar a la API")
        print()

def generate_curl_examples():
    """
    Generar ejemplos de curl para probar la API
    """
    print("📋 Ejemplos de curl:")
    print("=" * 50)

    # Ejemplo con eventos futuros
    future_timestamp = int(time.time()) + 3600
    payload_future = {
        "events": [
            {
                "event_id": "evt_001",
                "timestamp": future_timestamp,
                "data": "Evento futuro"
            }
        ]
    }

    print("1. Evento futuro:")
    print('curl -X POST "http://localhost:8000/process_events" \\')
    print('  -H "Content-Type: application/json" \\')
    print(f'  -d \'{json.dumps(payload_future, indent=2)}\'')
    print()

    # Ejemplo con eventos pasados
    past_timestamp = int(time.time()) - 3600
    payload_past = {
        "events": [
            {
                "event_id": "evt_past",
                "timestamp": past_timestamp,
                "data": "Evento pasado"
            }
        ]
    }

    print("2. Evento pasado (204 No Content):")
    print('curl -X POST "http://localhost:8000/process_events" \\')
    print('  -H "Content-Type: application/json" \\')
    print(f'  -d \'{json.dumps(payload_past, indent=2)}\'')
    print()

    # Endpoint de salud
    print("3. Verificar salud de la API:")
    print('curl "http://localhost:8000/health"')
    print()

    print("4. Documentación automática:")
    print("   Swagger UI: http://localhost:8000/docs")
    print("   ReDoc: http://localhost:8000/redoc")
    print()

if __name__ == "__main__":
    print("🚀 Event Processor API - Ejemplos de uso")
    print("=" * 50)
    print()

    # Ejecutar tests
    test_api_health()
    test_api_with_future_events()
    test_api_with_past_events()

    # Generar ejemplos de curl
    generate_curl_examples()

    print("💡 Instrucciones:")
    print("1. Asegúrate de que la API esté ejecutándose: python main.py")
    print("2. La API estará disponible en: http://localhost:8000")
    print("3. Documentación automática en: http://localhost:8000/docs")
    print("4. Ejecuta este script: python ejemplo_uso.py")
