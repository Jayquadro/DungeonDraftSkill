"""Protocollo comune ai generatori e Blueprint di output.

Vedi docs/SPEC.md §9. Ogni generatore reale (bsp.py, building.py, cave.py,
city.py) deve istanziare il proprio RNG da `seed` (mai il modulo `random`
globale): e l'unico modo per garantire che lo stesso seed produca sempre
lo stesso Blueprint (SPEC.md §8, requisito di testabilita).
"""

from typing import Protocol

from ddforge.model import Blueprint


class Generator(Protocol):
    def generate(self, *, width: int, height: int, seed: int, **params) -> Blueprint: ...
