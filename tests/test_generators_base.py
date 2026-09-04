"""Test per il protocollo Generator (TASK-20): riproducibilita del seed.

Usa un generatore fittizio (non uno dei generatori reali, che arrivano da
TASK-21 in poi) per dimostrare e verificare concretamente il pattern che
ogni generatore vero dovra seguire.
"""

import random

from ddforge.generators.base import Generator
from ddforge.model import Blueprint, Rect, Room


class _FakeGenerator:
    """Generatore fittizio: una stanza con dimensione/posizione derivate
    dal seed. Istanzia sempre il proprio random.Random(seed) locale."""

    def generate(self, *, width: int, height: int, seed: int, **params) -> Blueprint:
        rng = random.Random(seed)
        w = rng.randint(3, min(10, width - 2))
        h = rng.randint(3, min(10, height - 2))
        x1 = rng.randint(1, max(1, width - w - 1))
        y1 = rng.randint(1, max(1, height - h - 1))
        room = Room(rect=Rect(x1, y1, x1 + w, y1 + h), kind="sala")
        return Blueprint(
            width=width, height=height,
            rooms=[room], corridors=[], graph={0: []},
            seed=seed, style="fittizio",
        )


def test_fake_generator_satisfies_the_generator_protocol():
    generator: Generator = _FakeGenerator()
    result = generator.generate(width=40, height=40, seed=1)
    assert isinstance(result, Blueprint)


def test_same_seed_produces_identical_blueprint():
    gen = _FakeGenerator()
    a = gen.generate(width=40, height=40, seed=1337)
    b = gen.generate(width=40, height=40, seed=1337)

    assert a.rooms[0].rect == b.rooms[0].rect
    assert a.seed == b.seed == 1337
    assert a == b


def test_different_seed_produces_different_blueprint():
    gen = _FakeGenerator()
    a = gen.generate(width=40, height=40, seed=1)
    b = gen.generate(width=40, height=40, seed=2)
    assert a.rooms[0].rect != b.rooms[0].rect


def test_generator_does_not_depend_on_global_random_state():
    """Se il generatore usasse random.* globale invece di random.Random(seed)
    locale, il risultato dipenderebbe anche dallo stato globale esterno,
    non solo dal seed passato: qui lo stato globale viene alterato prima e
    dopo, e il risultato deve restare identico in entrambi i casi."""
    gen = _FakeGenerator()

    random.seed(111)
    random.random()  # altera lo stato globale
    a = gen.generate(width=40, height=40, seed=99)

    random.seed(222)
    random.random()
    random.random()
    random.random()  # altera lo stato globale in modo diverso
    b = gen.generate(width=40, height=40, seed=99)

    assert a == b
