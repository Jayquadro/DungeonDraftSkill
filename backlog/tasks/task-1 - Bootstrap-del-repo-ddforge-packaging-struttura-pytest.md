---
id: TASK-1
title: 'Bootstrap del repo ddforge (packaging, struttura, pytest)'
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:25'
updated_date: '2026-09-03 11:45'
labels: []
milestone: m-0
dependencies: []
documentation:
  - docs/SPEC.md
priority: high
type: chore
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Crea lo scheletro del progetto descritto in SPEC.md §4 in modo che ogni milestone successiva abbia dove atterrare: pyproject.toml con entry point CLI `ddforge`, package `src/ddforge` con i moduli vuoti previsti, cartelle `templates/`, `data/`, `tests/fixtures/`, README minimo. Stack: Python >= 3.11, solo stdlib per il core, pytest per i test, nessuna dipendenza runtime pesante (Pillow solo in M6). Codice e docstring in italiano, nomi di funzione in inglese.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 pyproject.toml definisce il package src/ddforge e l'entry point console `ddforge = ddforge.cli:main`
- [x] #2 Esiste la struttura di src/ddforge con i moduli previsti in SPEC.md §4, anche se solo con stub e docstring
- [x] #3 Esistono le cartelle templates/, data/, tests/, tests/fixtures/, skill/
- [x] #4 `pip install -e .` riesce e `ddforge --help` stampa i sottocomandi previsti (anche non ancora implementati)
- [x] #5 `pytest -q` gira senza errori su una suite anche vuota
- [x] #6 Il core non importa dipendenze esterne: solo stdlib
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Creare pyproject.toml (setuptools, src layout, package ddforge, Python >=3.11, zero dipendenze runtime nel core, entry point console ddforge = ddforge.cli:main, dev extra con pytest).
2. Creare src/ddforge/__init__.py e gli stub dei moduli previsti in SPEC.md §4: godot.py, ids.py, template.py, model.py, build.py, compose.py, assets.py, validate.py, cli.py, piu il package generators/ con __init__.py, base.py, bsp.py, building.py, cave.py, city.py. Ogni stub ha docstring in italiano che rimanda alla sezione di SPEC.md pertinente, nessuna logica.
3. Implementare cli.py con argparse: parser principale e sottocomandi generate, validate, inspect, catalog, preview (stub che sollevano NotImplementedError quando invocati, ma visibili in --help).
4. Creare le cartelle templates/, data/, tests/, tests/fixtures/, skill/ (con .gitkeep dove serve) e skill/references/.
5. Creare tests/conftest.py minimo e un test placeholder cosi pytest -q non fallisce su suite vuota.
6. Creare un README.md minimo che rimanda a docs/SPEC.md.
7. pip install -e . in un venv, verificare ddforge --help elenca i sottocomandi, poi pytest -q verde.
8. Verificare che nessun modulo sotto src/ddforge importi pacchetti esterni (grep import).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Creato pyproject.toml (setuptools, src layout, entry point ddforge=ddforge.cli:main, extra dev/preview, zero dipendenze runtime nel core). Creati gli stub di tutti i moduli di SPEC.md §4 (godot, ids, template, model, build, compose, assets, validate, cli, generators/{base,bsp,building,cave,city}) con docstring in italiano che rimandano ai task che li implementeranno. cli.py espone gia il parser completo con i 5 sottocomandi (generate, validate, inspect, catalog, preview) tramite argparse; le funzioni sollevano NotImplementedError quando invocate. Create le cartelle templates/, data/, tests/fixtures/, skill/references/ con .gitkeep esplicativi. Aggiunti tests/conftest.py e tests/test_bootstrap.py come placeholder. README.md minimo. Verificato in un venv pulito: pip install -e ".[dev]" riesce, ddforge --help elenca i 5 sottocomandi, pytest -q -> 2 passed, grep su src/ddforge conferma che gli unici import sono stdlib (dataclasses, argparse, sys, pathlib, typing) piu import interni ddforge.*.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Scheletro del repo ddforge creato secondo SPEC.md §4: pyproject.toml (setuptools src-layout, entry point ddforge=ddforge.cli:main, extra dev/preview), stub di tutti i moduli core e dei 4 generatori con docstring in italiano che rimandano ai task di implementazione futuri, cli.py con parser argparse completo (generate/validate/inspect/catalog/preview), cartelle templates/ data/ tests/fixtures/ skill/references/ e README minimo. Verificato in venv pulito: pip install -e ".[dev]" riuscito, ddforge --help elenca i 5 sottocomandi, pytest -q -> 2 passed exit 0, grep conferma zero dipendenze esterne nel core (solo stdlib + import interni ddforge.*).
<!-- SECTION:FINAL_SUMMARY:END -->
