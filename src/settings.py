"""Configuration module for loading and managing application settings.

This module provides:
- Settings: Configuration class for loading environment variables
- get_settings: Factory function to get application settings
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	"""Application configuration settings loaded from environment variables."""

	AUTHORISATION_URL: str = Field(description="URL for authorisation")

	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
	"""Get the application configuration settings.

	Returns:
		Settings: The app's configuration settings loaded from environment variables.
	"""
	return Settings()


app_settings = get_settings()
