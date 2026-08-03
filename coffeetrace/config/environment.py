"""Typed access to environment variables.

This module contains no database access. It only reads and validates process
configuration so the application can fail fast before serving requests.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Final

from django.core.exceptions import ImproperlyConfigured

_TRUE_VALUES: Final[frozenset[str]] = frozenset({"1", "true", "yes", "on"})
_FALSE_VALUES: Final[frozenset[str]] = frozenset({"0", "false", "no", "off"})


@dataclass(frozen=True, slots=True)
class Environment:
    """Read environment values with explicit validation and conversion."""

    @staticmethod
    def get(name: str, default: str | None = None) -> str:
        value = os.getenv(name, default)
        if value is None:
            raise ImproperlyConfigured(
                f"La variable de entorno obligatoria '{name}' no está configurada."
            )
        return value.strip()

    @staticmethod
    def require(name: str) -> str:
        value = Environment.get(name)
        if not value:
            raise ImproperlyConfigured(
                f"La variable de entorno obligatoria '{name}' no puede estar vacía."
            )
        return value

    @staticmethod
    def get_bool(name: str, default: bool = False) -> bool:
        raw_value = Environment.get(name, str(default)).lower()
        if raw_value in _TRUE_VALUES:
            return True
        if raw_value in _FALSE_VALUES:
            return False
        raise ImproperlyConfigured(
            f"La variable '{name}' debe ser true/false, 1/0, yes/no u on/off."
        )

    @staticmethod
    def get_int(name: str, default: int, *, minimum: int | None = None) -> int:
        raw_value = Environment.get(name, str(default))
        try:
            value = int(raw_value)
        except ValueError as exc:
            raise ImproperlyConfigured(
                f"La variable '{name}' debe contener un número entero."
            ) from exc

        if minimum is not None and value < minimum:
            raise ImproperlyConfigured(
                f"La variable '{name}' debe ser mayor o igual a {minimum}."
            )
        return value

    @staticmethod
    def get_list(name: str, default: str = "") -> list[str]:
        raw_value = Environment.get(name, default)
        return [item.strip() for item in raw_value.split(",") if item.strip()]
