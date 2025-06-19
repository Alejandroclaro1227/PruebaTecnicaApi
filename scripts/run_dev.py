#!/usr/bin/env python3
"""
Script para ejecutar el servidor de desarrollo con configuración optimizada
"""
import uvicorn
import socket
import sys
import signal
import asyncio
import platform
from pathlib import Path

# Agregar el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def signal_handler(signum, frame):
    """Maneja las señales de interrupción de manera limpia"""
    print(f"\n🛑 Señal {signum} recibida. Cerrando servidor de desarrollo...")
    sys.exit(0)

def setup_signal_handlers():
    """Configura los manejadores de señales según el sistema operativo"""
    if platform.system() != "Windows":
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    else:
        # En Windows, solo configuramos SIGINT
        signal.signal(signal.SIGINT, signal_handler)

def find_free_port(start_port=8001, max_attempts=10):
    """Encuentra un puerto libre comenzando desde start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def main():
    # Configurar manejadores de señales
    setup_signal_handlers()

    # Buscar puerto disponible
    port = find_free_port()
    if not port:
        print("❌ No se pudo encontrar un puerto disponible")
        return

    print("🚀 Event Processor API - Modo Desarrollo")
    print("=" * 50)
    print(f"🌐 URL Local: http://localhost:{port}")
    print(f"📖 Documentación: http://localhost:{port}/docs")
    print(f"🔧 Puerto: {port}")
    print(f"💻 Sistema: {platform.system()}")
    print("=" * 50)
    print("💡 Presiona Ctrl+C para detener el servidor")
    print()

    try:
        # Configuración específica para Windows
        if platform.system() == "Windows":
            # Usar política de eventos de Windows
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",  # Solo localhost por seguridad
            port=port,
            reload=True,
            log_level="info",
            access_log=True,
            # Configuraciones adicionales para mejor manejo de cierre
            lifespan="on",
            timeout_keep_alive=5
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido correctamente")
        sys.exit(0)
    except asyncio.CancelledError:
        print("\n🛑 Operación cancelada - Servidor cerrado correctamente")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error en el servidor de desarrollo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
