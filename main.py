#!/usr/bin/env python3
"""
Event Processor API - Punto de entrada principal
===============================================

Este es el punto de entrada principal para la aplicación.
Usa la nueva estructura organizada en carpetas.
"""

import sys
import signal
import asyncio
import platform
from pathlib import Path

# Agregar el directorio actual al path para importaciones
sys.path.append(str(Path(__file__).parent))

def signal_handler(signum, frame):
    """Maneja las señales de interrupción de manera limpia"""
    print(f"\n🛑 Señal {signum} recibida. Cerrando aplicación...")
    sys.exit(0)

def setup_signal_handlers():
    """Configura los manejadores de señales según el sistema operativo"""
    if platform.system() != "Windows":
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    else:
        # En Windows, solo configuramos SIGINT
        signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    import uvicorn
    import os

    print("🚀 Iniciando Event Processor API...")
    print("📁 Estructura organizada de proyecto")
    print("🌐 URL: http://localhost:8001")
    print("📖 Documentación: http://localhost:8001/docs")
    print("-" * 50)

    # Configurar entorno de desarrollo
    os.environ["ENVIRONMENT"] = "development"

    # Configurar manejadores de señales
    setup_signal_handlers()

    try:
        # Configuración específica para Windows
        if platform.system() == "Windows":
            # Usar política de eventos de Windows
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info",
            access_log=True,
            # Configuraciones adicionales para mejor manejo de cierre
            lifespan="on",
            timeout_keep_alive=5
        )
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario")
        sys.exit(0)
    except asyncio.CancelledError:
        print("\n🛑 Operación cancelada - Aplicación cerrada correctamente")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {e}")
        print("💡 Asegúrate de estar en el directorio correcto y tener las dependencias instaladas")
        sys.exit(1)
