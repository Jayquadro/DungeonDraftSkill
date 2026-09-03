---
id: TASK-1
title: 'Bootstrap del repo ddforge (packaging, struttura, pytest)'
status: To Do
assignee: []
created_date: '2026-09-03 11:25'
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
- [ ] #1 pyproject.toml definisce il package src/ddforge e l'entry point console `ddforge = ddforge.cli:main`
- [ ] #2 Esiste la struttura di src/ddforge con i moduli previsti in SPEC.md §4, anche se solo con stub e docstring
- [ ] #3 Esistono le cartelle templates/, data/, tests/, tests/fixtures/, skill/
- [ ] #4 `pip install -e .` riesce e `ddforge --help` stampa i sottocomandi previsti (anche non ancora implementati)
- [ ] #5 `pytest -q` gira senza errori su una suite anche vuota
- [ ] #6 Il core non importa dipendenze esterne: solo stdlib
<!-- AC:END -->
