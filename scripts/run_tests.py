#!/usr/bin/env python3
"""
Script para ejecutar tests de la Event Processor API
==================================================

Uso: python scripts/run_tests.py [opciones]
"""

import os
import sys
import subprocess
from pathlib import Path

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

def run_command(command, description):
    """
    Ejecuta un comando y maneja el resultado.

    Args:
        command: Lista con el comando a ejecutar
        description: Descripción del comando
    """
    print(f"🧪 {description}...")
    print(f"💻 Comando: {' '.join(command)}")
    print("-" * 50)

    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"✅ {description} completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el comando {command[0]}")
        print("💡 Asegúrate de tener pytest instalado: pip install pytest")
        return False

def main():
    """
    Ejecuta diferentes tipos de tests.
    """
    print("🚀 Ejecutando tests para Event Processor API")
    print("=" * 50)

    # Configurar variables de entorno para testing
    os.environ["ENVIRONMENT"] = "test"

    success = True

    # Verificar que pytest esté disponible
    try:
        subprocess.run(["pytest", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pytest no está instalado o no está disponible")
        print("💡 Instala pytest: pip install pytest")
        return 1

    # Tests básicos
    if not run_command(["pytest", "tests/", "-v"], "Tests básicos"):
        success = False

    print("\n" + "=" * 50)

    # Tests con cobertura (si coverage está disponible)
    try:
        subprocess.run(["coverage", "--version"], check=True, capture_output=True)
        if not run_command(["coverage", "run", "-m", "pytest", "tests/"], "Tests con cobertura"):
            success = False
        if not run_command(["coverage", "report"], "Reporte de cobertura"):
            success = False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("💡 Para reporte de cobertura instala: pip install coverage")

    print("\n" + "=" * 50)

    if success:
        print("🎉 Todos los tests completados exitosamente!")
        return 0
    else:
        print("💥 Algunos tests fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(main())
