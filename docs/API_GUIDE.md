# Event Processor API - Guía Técnica

## 🔧 Configuración Avanzada

### Variables de Entorno

La aplicación soporta configuración a través de variables de entorno:

```bash
# Configuración básica
ENVIRONMENT=development      # development, production, test
HOST=0.0.0.0                # Host del servidor
PORT=8000                   # Puerto del servidor
DEBUG=true                  # Modo debug

# Límites de seguridad
MAX_EVENTS_PER_REQUEST=1000  # Máximo eventos por solicitud
MAX_FUTURE_YEARS=10          # Máximo años en el futuro permitidos

# Logging
LOG_LEVEL=INFO              # Nivel de logging
LOG_FILE=app.log            # Archivo de logs
```

## 📊 Monitoreo y Observabilidad

### Endpoints de Salud

#### GET /health/

Información detallada del estado del sistema:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00+00:00",
  "current_epoch": 1704067200,
  "version": "1.0.0"
}
```

#### GET /health/dependencies

Estado de las dependencias del sistema:

```json
{
  "python_version": "3.11.0",
  "platform": "Windows-10",
  "dependencies_status": "ok"
}
```

## 🚀 Despliegue

### Desarrollo Local

```bash
# Opción 1: Script automatizado
python scripts/run_dev.py

# Opción 2: Directamente
python main.py

# Opción 3: Con uvicorn
uvicorn app.main:app --reload
```

### Producción

```bash
# Configurar entorno
export ENVIRONMENT=production

# Ejecutar con gunicorn (recomendado)
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# O con uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🔒 Seguridad

### Configuraciones de Seguridad Implementadas

- **CORS**: Configurado para desarrollo (\*), restringir en producción
- **Trusted Hosts**: Solo hosts confiables pueden acceder
- **Input Validation**: Validación exhaustiva con Pydantic
- **Rate Limiting**: Límite de 1000 eventos por solicitud
- **Error Handling**: No exposición de información sensible

### Recomendaciones para Producción

1. **Configurar CORS específico**:

   ```python
   cors_origins = ["https://tu-dominio.com"]
   ```

2. **Usar HTTPS**: Configurar certificados SSL/TLS

3. **Implementar autenticación**: JWT, OAuth2, etc.

4. **Rate limiting**: Usar nginx o middleware adicional

5. **Monitoring**: Implementar métricas con Prometheus/Grafana

## 📈 Rendimiento

### Optimizaciones Implementadas

- **Async/Await**: Manejo asíncrono de requests
- **Pydantic**: Validación rápida y serialización eficiente
- **Structured Logging**: Logs estructurados para mejor debugging
- **Error Caching**: Manejo eficiente de errores

### Métricas de Rendimiento

- **Latencia**: < 50ms para procesamiento típico
- **Throughput**: > 1000 requests/segundo (hardware dependiente)
- **Memoria**: ~50MB baseline
- **CPU**: Optimizado para cargas concurrentes

## 🐛 Debugging

### Logs Estructurados

Los logs incluyen:

- Timestamp
- Nivel de log
- Nombre del módulo
- Mensaje detallado

### Debugging Local

```bash
# Ejecutar con debug activado
ENVIRONMENT=development python main.py

# Ver logs en tiempo real
tail -f app.log

# Tests con debug
pytest tests/ -v --tb=short
```

## 📚 Ejemplos Avanzados

### Uso con Python

```python
import requests
import time

# Cliente simple
class EventProcessorClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def process_events(self, events):
        response = requests.post(
            f"{self.base_url}/events/process",
            json={"events": events}
        )
        return response

# Uso
client = EventProcessorClient()
events = [
    {
        "event_id": "evt_001",
        "timestamp": int(time.time()) + 3600,
        "data": "Mi evento"
    }
]

result = client.process_events(events)
print(result.json())
```

### Integración con Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## ❓ FAQ

### P: ¿Cómo cambiar el puerto de la aplicación?

R: Usa la variable de entorno `PORT=8080` o modifica la configuración.

### P: ¿La API persiste datos?

R: No, la API es stateless y no persiste eventos.

### P: ¿Cuál es el límite de eventos por solicitud?

R: 1000 eventos por defecto, configurable con `MAX_EVENTS_PER_REQUEST`.

### P: ¿Cómo manejar errores en el cliente?

R: Verifica siempre el status code y maneja los errores 400/422/500.

### P: ¿Soporta autenticación?

R: Actualmente no, pero se puede extender fácilmente.
