"""
Configuración de la Event Processor API
=======================================

Este archivo contiene todas las configuraciones de la aplicación.
"""

import os
from typing import List
from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    """

    # Información básica de la aplicación
    app_name: str = "Event Processor API"
    app_version: str = "1.0.0"
    app_description: str = "API para procesar eventos y encontrar el evento futuro más próximo"

    # Configuración del servidor
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Configuración de logging
    log_level: str = "INFO"
    log_file: str = "app.log"

    # Configuración de CORS
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]

    # Configuración de hosts confiables
    trusted_hosts: List[str] = ["localhost", "127.0.0.1", "*.localhost"]

    # Límites de la aplicación
    max_events_per_request: int = 1000
    max_future_years: int = 10

    # Configuración de documentación
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"

    # Configuración de contacto
    contact_name: str = "Event Processor Team"
    contact_email: str = "contact@eventprocessor.com"

    # Configuración de licencia
    license_name: str = "MIT"
    license_url: str = "https://opensource.org/licenses/MIT"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class DevelopmentSettings(Settings):
    """
    Configuración para entorno de desarrollo.
    """
    debug: bool = True
    log_level: str = "DEBUG"


class ProductionSettings(Settings):
    """
    Configuración para entorno de producción.
    """
    debug: bool = False
    log_level: str = "WARNING"
    cors_origins: List[str] = []  # Especificar dominios específicos en producción


class TestSettings(Settings):
    """
    Configuración para entorno de testing.
    """
    debug: bool = True
    log_level: str = "DEBUG"
    max_events_per_request: int = 100  # Límite menor para tests


def get_settings() -> Settings:
    """
    Obtiene la configuración según el entorno.

    Returns:
        Settings: Configuración apropiada para el entorno actual
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if environment == "production":
        return ProductionSettings()
    elif environment == "test":
        return TestSettings()
    else:
        return DevelopmentSettings()


# Instancia global de configuración
settings = get_settings()
