from typing import Literal

from agno.models.base import Model
from pydantic_settings import BaseSettings, SettingsConfigDict
from agno.models.ollama import Ollama
from agno.models.openai import OpenAIChat


class Settings(BaseSettings):
    """Settings loaded from a .env file in the working directory.

    Environment variables take precedence over the .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    model_provider: Literal["openai", "ollama"] = "openai"
    model_name: str = "gpt-4o-mini"
    openai_api_key: str = ""

    ollama_host: str = "http://localhost:11434"


def create_model(settings: Settings) -> Model:
    """Build the chat model selected by `settings.model_provider`."""

    if settings.model_provider == "ollama":

        return Ollama(
            id=settings.model_name,
            host=settings.ollama_host,
            options={"num_ctx": 16384},
            keep_alive="30m",
        )

    return OpenAIChat(
        id=settings.model_name,
        api_key=settings.openai_api_key,
    )