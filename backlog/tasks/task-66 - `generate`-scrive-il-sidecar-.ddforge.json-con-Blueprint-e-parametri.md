---
id: TASK-66
title: '`generate` scrive il sidecar .ddforge.json con Blueprint e parametri'
status: Done
assignee: []
created_date: '2026-10-04 17:30'
updated_date: '2026-10-06 13:42'
labels: []
milestone: m-10
dependencies: []
references:
  - src/ddforge/model.py
  - src/ddforge/cli.py
  - docs/SPEC-decorate.md
documentation:
  - docs/SPEC-decorate.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Il futuro comando `ddforge decorate` (milestone M10) ha bisogno della semantica che oggi `generate` butta via dopo il compose: quale stanza e la stanza boss, quali corridoi sono "bui", gli snodi tattici, le porte segrete, i ruoli delle stanze di un edificio, strade/piazze/landmark di una citta. Un .dungeondraft_map non la contiene.

Questo task fa si che `ddforge generate` scriva, accanto a ogni mappa, un file `<nome>.ddforge.json` con: versione del formato sidecar, algoritmo e parametri usati, template, hash del catalogo, hash del file mappa scritto, serializzazione completa del `model.Blueprint` (ricorsiva su `buildings` e `landmarks[].building`) e una lista `decorations` vuota. Formato e motivazioni in docs/SPEC-decorate.md §4.

Il sidecar non cambia nulla del file .dungeondraft_map: i golden test esistenti devono restare verdi.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `ddforge generate` scrive `<nome>.ddforge.json` accanto alla mappa per tutti e 5 gli algoritmi
- [x] #2 Il sidecar contiene versione, algoritmo, parametri, template, hash del catalogo, hash del file mappa e il Blueprint serializzato, come in docs/SPEC-decorate.md §4.1
- [x] #3 Deserializzare il sidecar restituisce un Blueprint uguale a quello generato (test di round-trip per ogni algoritmo, citta con edifici e landmark compresi)
- [x] #4 L'hash nel sidecar corrisponde al file mappa scritto
- [x] #5 Se la validazione fallisce e la mappa non viene scritta, non viene scritto nemmeno il sidecar
- [x] #6 Il file .dungeondraft_map generato e byte-identico a prima del task (golden test invariati)
- [x] #7 README e skills/generator/references/examples.md menzionano il sidecar e a cosa serve
- [x] #8 Il sidecar viene scritto sempre: non esiste un'opzione per disattivarlo (decisione di Jay, SPEC-decorate §14 D2)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Nuovo package src/ddforge/decorate/ con sidecar.py: serializers espliciti to/from JSON per ogni dataclass di model.py (Rect, Corridor, Door, Chamber, Street, Gate, CityWalls, River, Bridge, Port, Landmark, Room, Blueprint), ricorsivi su buildings/landmarks[].building. 2. build_sidecar()/write_sidecar()/load_sidecar() con hash sha256 su bytes mappa scritta e su data/assets.json. 3. cli.py: cattura effective_args per ciascun ramo di _cmd_generate, scrive il sidecar dopo save() leggendo i byte scritti (cosi l'hash corrisponde sempre). Nessun flag per disattivarlo. 4. Test di round-trip per i 5 algoritmi (incl. city isolato con buildings/landmarks e quartiere/citta con footprints) + test end-to-end CLI su sidecar scritto, hash, blocco validazione, assenza flag disattivante. 5. Verifica che i golden test esistenti restino verdi. 6. README.md e skills/generator/references/examples.md aggiornati.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementato src/ddforge/decorate/sidecar.py (nuovo package decorate/) con serializzazione esplicita (non dataclasses.asdict, per gestire tuple/frozenset/chiavi-intero del Blueprint) e round-trip testato per bsp/building/cave/sewer/city (isolato con buildings e landmark, quartiere con footprints, citta con mura/fiume/porto) in tests/test_decorate_sidecar.py. cli.py aggiornato: effective_args catturati per ramo, sidecar scritto dopo save() hashando i byte realmente scritti. Test: .venv/Scripts/python -m pytest tests/ -q -m 'not slow' -> 798 passed, 1 skipped; golden file tests (-m slow -k golden) -> 5 passed, invariati. test_decorate_sidecar.py: 18 passed (round-trip, scrittura CLI per i 5 algoritmi, hash mappa/catalogo, blocco su validazione fallita, nessun flag di disattivazione, naming <nome>.ddforge.json). README.md e skills/generator/references/examples.md aggiornati con la sezione sidecar.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Aggiunto src/ddforge/decorate/sidecar.py: generate scrive sempre <nome>.ddforge.json accanto alla mappa (versione, algoritmo+parametri effettivi, template, hash catalogo/mappa, Blueprint serializzato ricorsivamente, decorations vuota). Nessun flag per disattivarlo. cli.py aggiornato per catturare gli effective_args per ramo e hashare i byte realmente scritti. Verificato: round-trip serialize/deserialize per i 5 algoritmi incl. city isolato (buildings+landmark) e quartiere/citta (footprints, mura/fiume/porto) e un caso sintetico di landmark con building annidato; 18 test nuovi in tests/test_decorate_sidecar.py; suite completa 798 passed/1 skipped; golden file (-m slow) 5 passed invariati, a conferma che il .dungeondraft_map resta byte-identico. README.md e skills/generator/references/examples.md aggiornati.
<!-- SECTION:FINAL_SUMMARY:END -->
