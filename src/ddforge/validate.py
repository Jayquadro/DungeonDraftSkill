"""Validatore pre-consegna: trasforma il progetto da speranza a ingegneria.

Codici DDF001-DDF015 (error) e DDF101-DDF105 (warning).
Vedi docs/SPEC.md §7. Implementato in TASK-13 e TASK-14.
"""

from dataclasses import dataclass


@dataclass
class Issue:
    severity: str  # "error" | "warning"
    code: str  # es. "DDF001"
    message: str
    path: str  # es. "world.levels.0.walls[3]"


def validate(doc: dict) -> list[Issue]:
    raise NotImplementedError
