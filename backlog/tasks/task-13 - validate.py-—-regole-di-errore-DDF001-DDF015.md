---
id: TASK-13
title: validate.py — regole di errore DDF001-DDF015
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:28'
updated_date: '2026-09-04 06:01'
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
- [x] #1 Tutte e 15 le regole di errore di SPEC.md §7 sono implementate con il codice DDFxxx corretto
- [x] #2 Ogni Issue riporta severity, code, messaggio leggibile in italiano e path puntuale dell'elemento
- [x] #3 DDF005 rileva i node_id duplicati in tutto il documento, porte annidate comprese
- [x] #4 DDF010 e DDF011 verificano len(tiles.cells) == width*height e len(terrain.splat) == width*height*64
- [x] #5 DDF014 verifica che ogni res://packs/<ID>/... abbia <ID> in header.asset_manifest
- [x] #6 validate() non solleva eccezioni su documenti malformati: restituisce Issue
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implementare Issue (dataclass) e validate(doc) -> list[Issue] in validate.py, importando LEVEL_KEYS/DRAWABLE_LISTS da template.py. Ogni check e una funzione dedicata, tutte difensive (mai un'eccezione non gestita, AC6). DDF001-004 struttura, DDF005-006 univocita/coerenza node_id (riuso concettuale della logica di ids.py ma con path per i messaggi), DDF007-009 formato stringhe Godot (regex), DDF010-011 lunghezza blob (parser locale PoolArray, stessa lezione imparata in TASK-5: contare gli elementi dopo il parsing, non len() sulla stringa), DDF012-013 coerenza porte SOLO per quelle annidate in wall.portals (non per l'eventuale schema libero scoperto in TASK-2), DDF014 pack referenziati, DDF015 rotazioni finite. Percorsi tipo 'world.levels.0.walls[3]'. Test con fixture corrotte mirate per ogni codice, piu verifica che il documento demo di TASK-11 non produca errori.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementate tutte e 15 le regole DDF001-015 con path puntuali e messaggi in italiano. Smoke test contro i file reali del progetto (prima di scrivere i test formali) ha trovato e fatto correggere un vero bug: rich_reference.dungeondraft_map ha una luce in variante 'con sprite' (colore a 8 cifre ARGB) che la regola iniziale, pensata solo per la variante puntiforme (6 cifre), segnalava erroneamente — corretto distinguendo le due varianti per presenza del campo 'texture'. DDF012/013 (coerenza porte) applicate solo alle porte annidate in wall.portals, mai allo schema libero di level.portals scoperto in TASK-2 (testato esplicitamente). DDF010/011 usano un parser locale di PoolIntArray/PoolByteArray (stessa lezione di TASK-5: contare gli elementi, non la lunghezza della stringa). validate() e avvolta in un blocco try/except di sicurezza (AC6): testato esplicitamente su 9 documenti malformati in modi diversi, incluso None/lista/stringa/intero come doc, senza mai sollevare eccezioni. 29 test nuovi in tests/test_validate.py, uno per ciascuno dei 15 codici errore piu casi limite; verificato anche che il documento reale generato da scripts/demo_m1.py produca zero errori. Suite completa: 118 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementate le 15 regole DDF001-015 in validate.py con Issue(severity, code, message, path). Uno smoke test contro i file reali ha scoperto e fatto correggere un bug (variante light con sprite trattata come puntiforme). DDF012/013 applicate solo ai portal annidati, mai allo schema libero. 29 test nuovi, suite completa 118 test verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
