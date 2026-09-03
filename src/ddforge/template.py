"""Caricamento, svuotamento e salvataggio del template .dungeondraft_map.

Il generatore non costruisce mai il JSON da zero: carica un template reale,
svuota solo le liste disegnabili e ci inietta la geometria generata.
Vedi docs/SPEC.md §2, §6.3, §12 (base verificata).
"""

import copy
import json
from pathlib import Path
from typing import Sequence


class TemplateError(Exception):
    """Il documento caricato non e un template Dungeondraft valido."""


LEVEL_KEYS = (
    "label", "environment", "layers", "shapes", "tiles", "patterns",
    "walls", "portals", "cave", "terrain", "water", "materials",
    "paths", "objects", "lights", "roofs", "texts",
    # "texts_vis" (bool, visibilita del layer testi) e presente in tutte le
    # mappe build 1.2.0.1 osservate (blank_80x80, rich_reference) ma assente
    # dalle 17 chiavi verificate in SPEC.md §13, derivate da mappe 1.0.4.x:
    # e stato aggiunto in una build successiva. Vedi docs/format.md §12
    # (sezione "texts_vis — 18a chiave di livello").
    "texts_vis",
)

DRAWABLE_LISTS = (
    "patterns", "walls", "portals", "paths", "objects", "lights", "texts",
)


def load_template(path: str | Path) -> dict:
    """Carica il JSON e verifica che sia un documento Dungeondraft valido."""
    path = Path(path)
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except FileNotFoundError as exc:
        raise TemplateError(f"Template non trovato: {path}") from exc
    except json.JSONDecodeError as exc:
        raise TemplateError(f"Template non e un JSON valido: {path} ({exc})") from exc

    if not isinstance(doc, dict) or "header" not in doc:
        raise TemplateError(f"Manca la chiave 'header' nel template: {path}")
    if not isinstance(doc.get("header"), dict):
        raise TemplateError(f"'header' non e un oggetto nel template: {path}")
    if "world" not in doc or not isinstance(doc["world"], dict):
        raise TemplateError(f"Manca la chiave 'world' (oggetto) nel template: {path}")

    world = doc["world"]
    if "format" not in world or not isinstance(world["format"], int):
        raise TemplateError(
            f"'world.format' assente o non intero nel template: {path}"
        )
    if "levels" not in world or not isinstance(world["levels"], dict) or not world["levels"]:
        raise TemplateError(
            f"'world.levels' assente, non e un oggetto, o e vuoto nel template: {path}"
        )

    return doc


def blank_level(level: dict) -> dict:
    """Deep copy del livello con solo le liste disegnabili svuotate.

    Mantiene intatti i blob dimensionati sulla mappa (tiles, terrain, cave,
    water, environment, layers). `shapes` e `materials` vengono azzerati
    insieme alle liste disegnabili: nella base verificata di SPEC.md §12
    contengono metadati derivati dagli elementi disegnabili (poligoni di
    muri tracciati, override di materiale), non blob dimensionati sulla
    mappa, quindi vanno svuotati con loro.
    """
    lv = copy.deepcopy(level)
    for key in DRAWABLE_LISTS:
        lv[key] = []
    if isinstance(lv.get("roofs"), dict):
        lv["roofs"] = {**lv["roofs"], "roofs": []}
    lv["shapes"] = {"polygons": [], "walls": []}
    lv["materials"] = {}
    return lv


def prepare(doc: dict, *, levels: int = 1, labels: Sequence[str] | None = None) -> dict:
    """Documento pronto per l'injection, con `levels` piani svuotati.

    Se il template ha meno piani di quelli richiesti, duplica il primo
    (i blob hanno gia la dimensione giusta, indipendente dal piano).
    """
    prepared = copy.deepcopy(doc)
    world = prepared["world"]
    existing = world["levels"]
    ordered_keys = sorted(existing.keys(), key=int)
    ordered_levels = [existing[k] for k in ordered_keys]

    new_levels = {}
    for i in range(levels):
        source = ordered_levels[i] if i < len(ordered_levels) else ordered_levels[0]
        blanked = blank_level(source)
        if labels and i < len(labels):
            blanked["label"] = labels[i]
        new_levels[str(i)] = blanked
    world["levels"] = new_levels
    return prepared


def finalize(doc: dict, ids) -> dict:
    """Aggiorna world.next_node_id. Da chiamare sempre prima di save()."""
    doc["world"]["next_node_id"] = ids.next_free
    return doc


def save(doc: dict, path: str | Path) -> None:
    """json.dump con indent=2, ensure_ascii=False, encoding utf-8."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
