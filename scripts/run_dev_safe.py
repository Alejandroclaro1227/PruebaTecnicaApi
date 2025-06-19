#!/usr/bin/env python3
"""
Script de desarrollo ULTRA SEGURO para Windows
===============================================

Este script está específicamente diseñado para evitar los errores
de KeyboardInterrupt y asyncio.CancelledError en Windows.
"""

import sys
import os
import subprocess
import signal
import platform
import socket
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def find_free_port(start_port=8001, max_attempts=10):
    """Encuentra un puerto libre"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def run_with_subprocess():
    """Ejecuta uvicorn como subproceso para mejor control"""
    port = find_free_port()
    if not port:
        print("❌ No se pudo encontrar un puerto disponible")
        return

    print("🚀 Event Processor API - Modo SEGURO para Windows")
    print("=" * 60)
    print(f"🌐 URL Local: http://localhost:{port}")
    print(f"📖 Documentación: http://localhost:{port}/docs")
    print(f"🔧 Puerto: {port}")
    print(f"💻 Sistema: {platform.system()}")
    print("⚡ Modo: Subproceso (sin errores asyncio)")
    print("=" * 60)
    print("💡 Presiona Ctrl+C para detener el servidor")
    print()

    # Comando uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "127.0.0.1",
        "--port", str(port),
        "--reload",
        "--log-level", "info"
    ]

    try:
        # Ejecutar como subproceso
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Mostrar output en tiempo real
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line.rstrip())

        process.wait()

    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidor...")
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("👋 Servidor detenido correctamente")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_direct():
    """Ejecuta directamente con uvicorn (modo tradicional mejorado)"""
    import uvicorn
    import asyncio

    port = find_free_port()
    if not port:
        print("❌ No se pudo encontrar un puerto disponible")
        return

    print("🚀 Event Processor API - Modo Directo Mejorado")
    print("=" * 60)
    print(f"🌐 URL Local: http://localhost:{port}")
    print(f"📖 Documentación: http://localhost:{port}/docs")
    print(f"🔧 Puerto: {port}")
    print(f"💻 Sistema: {platform.system()}")
    print("⚡ Modo: Directo con manejo mejorado")
    print("=" * 60)
    print("💡 Presiona Ctrl+C para detener el servidor")
    print()

    # Configurar asyncio para Windows
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        config = uvicorn.Config(
            "app.main:app",
            host="127.0.0.1",
            port=port,
            reload=True,
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        server.run()

    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n👋 Servidor detenido correctamente")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal con selección de modo"""
    if len(sys.argv) > 1 and sys.argv[1] == "--direct":
        run_direct()
    else:
        # Por defecto, usar subproceso (más seguro en Windows)
        run_with_subprocess()

if __name__ == "__main__":
    main()
