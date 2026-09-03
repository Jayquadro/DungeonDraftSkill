---
id: TASK-13
title: validate.py — regole di errore DDF001-DDF015
status: To Do
assignee: []
created_date: '2026-09-03 11:28'
labels: []
milestone: m-2
dependencies:
  - TASK-8
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Il validatore e il pezzo che trasforma il progetto da speriamo a ingegneria: ogni errore deve essere un messaggio leggibile, non un'eccezione generica (SPEC.md §7). API: dataclass Issue(severity, code, message, path) e funzione validate(doc) -> list[Issue], con path tipo 'world.levels.0.walls[3]'. Le 15 regole di errore vanno dalla struttura del documento (DDF001-DDF004) all'univocita dei node_id (DDF005-DDF006), al formato delle stringhe Godot (DDF007-DDF009), alla lunghezza dei blob binari (DDF010-DDF011), alla coerenza delle porte (DDF012-DDF013), ai pack referenziati (DDF014) e alle rotazioni (DDF015).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Tutte e 15 le regole di errore di SPEC.md §7 sono implementate con il codice DDFxxx corretto
- [ ] #2 Ogni Issue riporta severity, code, messaggio leggibile in italiano e path puntuale dell'elemento
- [ ] #3 DDF005 rileva i node_id duplicati in tutto il documento, porte annidate comprese
- [ ] #4 DDF010 e DDF011 verificano len(tiles.cells) == width*height e len(terrain.splat) == width*height*64
- [ ] #5 DDF014 verifica che ogni res://packs/<ID>/... abbia <ID> in header.asset_manifest
- [ ] #6 validate() non solleva eccezioni su documenti malformati: restituisce Issue
<!-- AC:END -->
