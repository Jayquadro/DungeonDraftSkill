"""Protocollo comune ai generatori e Blueprint di output.

Vedi docs/SPEC.md §9. Implementato in TASK-20.
"""

from typing import Protocol

from ddforge.model import Blueprint


class Generator(Protocol):
    def generate(self, *, width: int, height: int, seed: int, **params) -> Blueprint: ...
