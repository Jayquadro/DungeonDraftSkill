"""Tabella file grezzo -> sprite atteso.

Ogni riga viene dalla tabella di intestazione della scheda corrispondente in
prompt/*.md (categoria, canvas, regola del rosso) e da
sprite-batch.zip/catalogo.yaml (canvas per categoria: C1 1024, C2 768, C3
512; C4 a scala reale, 256 px = 1,5 m).

Un file in assets/ senza voce qui (compreso assets/template.png, che non è
uno sprite grezzo ma un'icona di riferimento) viene ignorato dalla procedura,
non elaborato a caso: aggiungere la riga è la prima cosa da fare quando arriva
un nuovo file.
"""

from __future__ import annotations

from dataclasses import dataclass

from .settings import CATEGORY_CANVAS


@dataclass(frozen=True)
class SpriteJob:
    source: str  # nome del file grezzo in assets/
    stem: str  # nome sprite senza prefisso nm_
    category: str  # C1 | C2 | C3 | C4
    red_mode: str  # tetto | vietato | libero
    scale_mode: str = "canvas"  # canvas | reale (solo C4 usa 'reale')
    size_m: tuple[float, ...] | None = None

    @property
    def filename(self) -> str:
        return f"nm_{self.stem}.png"

    @property
    def canvas(self) -> int:
        return CATEGORY_CANVAS[self.category]

    @property
    def max_size_m(self) -> float | None:
        return max(self.size_m) if self.size_m else None


# fmt: off
MANIFEST: tuple[SpriteJob, ...] = (
    # -------------------------------------------------- prompt/01..07 (esistenti)
    SpriteJob("ospedale.jpg", "ospedale", "C2", "tetto"),
    SpriteJob("teatro.jpg", "teatro", "C2", "tetto"),
    SpriteJob("accademia.jpg", "accademia", "C1", "libero"),
    SpriteJob("prigione.jpg", "prigione", "C2", "vietato"),
    SpriteJob("municipio.jpg", "municipio", "C2", "tetto"),
    SpriteJob("faro.jpg", "faro", "C2", "vietato"),
    SpriteJob("bagni_termali.jpg", "bagni", "C2", "tetto"),
    # -------------------------------------------------- prompt/08 banco-mercato (C4)
    SpriteJob(
        "Gemini_Generated_Image_z6vwunz6vwunz6vw.jpg", "banco_mercato_1", "C4", "libero",
        scale_mode="reale", size_m=(2.0, 2.0),
    ),
    # -------------------------------------------------- prompt/09..25 (TASK-49)
    SpriteJob("bibilioteca.jpg", "biblioteca", "C3", "tetto"),
    SpriteJob("villa.jpg", "villa_nobiliare", "C2", "tetto"),
    # cimitero (prompt/11): pezzi sparsi a scala reale, 256 px = 1,5 m
    SpriteJob(
        "croce.jpg", "cimitero_croce", "C4", "libero",
        scale_mode="reale", size_m=(0.8, 1.5),
    ),
    SpriteJob(
        "fossa.jpg", "cimitero_fossa", "C4", "libero",
        scale_mode="reale", size_m=(2.2, 1.5),
    ),
    SpriteJob(
        "lapide.jpg", "cimitero_lapide_1", "C4", "libero",
        scale_mode="reale", size_m=(1.0, 1.5),
    ),
    SpriteJob("armeria.jpg", "armeria", "C3", "tetto"),
    SpriteJob("tempio.jpg", "tempio", "C2", "tetto"),
    SpriteJob("monastero.jpg", "monastero", "C1", "libero"),
    SpriteJob("caserma.jpg", "caserma", "C2", "tetto"),
    SpriteJob("banca.jpg", "banca", "C3", "tetto"),
    SpriteJob("alchimista.jpg", "alchimista", "C3", "tetto"),
    SpriteJob("magazzino.jpg", "magazzino", "C3", "tetto"),
    SpriteJob("fabbro.jpg", "fabbro", "C3", "tetto"),
    SpriteJob("stalle.jpg", "stalle", "C3", "tetto"),
    SpriteJob("fornaio.jpg", "fornaio", "C3", "tetto"),
    SpriteJob("macellaio.jpg", "macelleria", "C3", "tetto"),
    SpriteJob("taverna1.jpg", "taverna", "C3", "tetto"),
    SpriteJob("locanda.jpg", "locanda", "C3", "tetto"),
    SpriteJob("bordello.jpg", "bordello", "C3", "tetto"),
)
# fmt: on

BY_SOURCE: dict[str, SpriteJob] = {job.source: job for job in MANIFEST}

if len(BY_SOURCE) != len(MANIFEST):
    raise AssertionError("manifest: nomi file grezzi duplicati")
