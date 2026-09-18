---
id: TASK-56
title: Rimuovere Sede di Gilda dal catalogo dei luoghi notevoli
status: Done
assignee:
  - '@claude'
created_date: '2026-09-18 08:19'
updated_date: '2026-09-18 08:46'
labels: []
dependencies: []
documentation:
  - docs/sprite-luoghi.md
ordinal: 57000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Jay ha chiesto di togliere la Sede di Gilda dall'elenco dei luoghi che il generatore puo' piazzare nelle mappe cittadine. Oggi 'gilda' e' un LandmarkKind in src/ddforge/generators/landmarks.py (_BIG, SITE_LOT, rate=0.008, max_count=4), sul ripiego house_09 (mai commissionato per il pacchetto Nova Mistralis, docs/sprite-luoghi.md sez.10) e accettato da --landmark. E' lo stesso tipo di rimozione gia' fatta in passato per cantiere navale, mercato del pesce e quartiere povero (docs/sprite-luoghi.md sez.9: 'tolti dal catalogo perche' Jay li ha scartati guardando il campionario').
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 'gilda' non compare piu' in generators.landmarks.LANDMARK_KINDS ne' fra i valori accettati da --landmark
- [x] #2 Nessuna mappa generata (nessun preset, nessun seed) piazza piu' la Sede di Gilda
- [x] #3 assets._CITY_LANDMARK_SPRITES non ha piu' una voce per 'gilda' coerente con la rimozione
- [x] #4 I test e i golden che referenziano il luogo 'gilda' sono aggiornati e la suite completa passa
- [x] #5 docs/sprite-luoghi.md aggiornato per riflettere la rimozione, come gia' fatto per gli altri luoghi scartati in sez.9
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Rimuovere il LandmarkKind 'gilda' da LANDMARK_KINDS in src/ddforge/generators/landmarks.py (REQUESTABLE/BY_KEY derivano da li', quindi --landmark si aggiorna da solo, AC1).
2. Rimuovere la voce 'gilda' da assets._CITY_LANDMARK_SPRITES in src/ddforge/assets.py (AC3).
3. Rimuovere 'gilda' da CANDIDATES in scripts/landmark_sprite_sheet.py e aggiornare il commento sui luoghi gia' tolti (stessa convenzione usata per cantiere/mercato_pesce/quartiere povero).
4. Aggiornare docs/sprite-luoghi.md: togliere la riga 'gilda' dalla tabella botteghe (sez.3), dalla tabella 'ancora sul ripiego' (sez.10), aggiornare i conteggi di sez.9 e la frase sui luoghi gia' tolti dal catalogo (AC5).
5. Verificare che nessun golden/test referenzi 'gilda' o 'house_09' per quel luogo; rigenerare golden se il diff lo tocca; pytest -q sull'intera suite (AC2, AC4).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Rimosso il LandmarkKind 'gilda' da LANDMARK_KINDS (landmarks.py): REQUESTABLE/BY_KEY derivano da li', quindi --landmark non lo accetta piu' senza altre modifiche (AC1). Rimossa la voce 'gilda' da assets._CITY_LANDMARK_SPRITES (AC3). Rimossa 'gilda' da CANDIDATES in scripts/landmark_sprite_sheet.py e aggiornato il commento sui luoghi gia' tolti dal catalogo, stessa convenzione di cantiere/mercato_pesce/quartiere povero. Aggiornato docs/sprite-luoghi.md: riga gilda tolta dalla tabella botteghe (sez.3) e dalla tabella 'ancora sul ripiego' (sez.10, ora 13 su 36), conteggi di sez.9 aggiornati (28 luoghi chiusi, ~46 totale minimo) e la frase sui luoghi gia' tolti ora ne cita quattro invece di tre (AC5). Nessun golden referenziava 'gilda' o 'house_09' per quel luogo (verificato con grep prima della rimozione). Suite completa: 779 passed, 1 skipped in 731s, stesso risultato di TASK-52 prima di questa modifica -> nessuna regressione, nessun golden da rigenerare (AC2, AC4).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
'gilda' rimosso da LANDMARK_KINDS, _CITY_LANDMARK_SPRITES e dal campionario di scripts/landmark_sprite_sheet.py; docs/sprite-luoghi.md aggiornato (sez.3, 9, 10). Verificato con l'intera suite: 779 passed, 1 skipped, nessun golden toccato.
<!-- SECTION:FINAL_SUMMARY:END -->
