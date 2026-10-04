---
id: TASK-66
title: '`generate` scrive il sidecar .ddforge.json con Blueprint e parametri'
status: To Do
assignee: []
created_date: '2026-10-04 17:30'
updated_date: '2026-10-04 18:39'
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
- [ ] #1 `ddforge generate` scrive `<nome>.ddforge.json` accanto alla mappa per tutti e 5 gli algoritmi
- [ ] #2 Il sidecar contiene versione, algoritmo, parametri, template, hash del catalogo, hash del file mappa e il Blueprint serializzato, come in docs/SPEC-decorate.md §4.1
- [ ] #3 Deserializzare il sidecar restituisce un Blueprint uguale a quello generato (test di round-trip per ogni algoritmo, citta con edifici e landmark compresi)
- [ ] #4 L'hash nel sidecar corrisponde al file mappa scritto
- [ ] #5 Se la validazione fallisce e la mappa non viene scritta, non viene scritto nemmeno il sidecar
- [ ] #6 Il file .dungeondraft_map generato e byte-identico a prima del task (golden test invariati)
- [ ] #7 README e skills/generator/references/examples.md menzionano il sidecar e a cosa serve
- [ ] #8 Il sidecar viene scritto sempre: non esiste un'opzione per disattivarlo (decisione di Jay, SPEC-decorate §14 D2)
<!-- AC:END -->
