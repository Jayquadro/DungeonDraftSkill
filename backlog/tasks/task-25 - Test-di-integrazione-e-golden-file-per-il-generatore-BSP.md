---
id: TASK-25
title: Test di integrazione e golden file per il generatore BSP
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:32'
updated_date: '2026-09-04 07:16'
labels: []
milestone: m-3
dependencies:
  - TASK-24
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Piramide di test descritta in SPEC.md §10. Integrazione: carica il template di fixture, genera, valida; verifica che non ci siano errori di validazione, che tutte le stanze siano raggiungibili nel grafo e che nessuna stanza si sovrapponga. Golden file: per un seed fisso il documento generato viene confrontato con un riferimento in tests/fixtures/golden/, normalizzando creation_date, per intercettare regressioni silenziose nel formato. I golden vanno marcati slow così che pytest -m 'not slow' resti veloce.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Un test di integrazione genera un dungeon sulla fixture 8x8 e verifica zero Issue di severity error
- [x] #2 Il test verifica che tutte le stanze siano raggiungibili nel grafo e che nessuna si sovrapponga
- [x] #3 Esiste un golden file per un seed fisso, confrontato normalizzando creation_date
- [x] #4 I test golden sono marcati slow e pytest -m 'not slow' li esclude
- [x] #5 pytest -q è verde
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Test di integrazione: usare la fixture reference_8x8_doc (TASK-5) patchata con texts_vis (stesso approccio di TASK-15, dato che quella fixture e di una build piu vecchia e altrimenti fallirebbe sempre DDF003 indipendentemente dal generatore) come template, generare un dungeon piccolo (rooms=3, adatto a una mappa 8x8), validare: zero errori, grafo connesso via BFS, nessuna sovrapposizione fra stanze. Golden file: generare con render_blueprint+furnish+lights su blank_80x80 con seed fisso, normalizzare header.creation_date (sostituendolo con un placeholder), salvare in tests/fixtures/golden/, marcare il test @pytest.mark.slow (marker gia registrato in pyproject.toml da TASK-1) cosi pytest -m 'not slow' lo esclude. Verificare pytest -q e pytest -m 'not slow' entrambi verdi.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Test di integrazione su reference_8x8_doc (TASK-5), patchato con texts_vis=True come gia fatto in TASK-15 (altrimenti DDF003 scatterebbe sempre indipendentemente dal generatore, per la nota assenza di quella chiave nella build piu vecchia della fixture). Parametri adattati alla scala 8x8 (rooms=3, min_room=2, max_room=3: con i default max_room=10 la mappa non avrebbe mai potuto dividersi). Golden file generato con pipeline realistica completa (template reale blank_80x80, render_blueprint, furnish density=light, seed=1337) e salvato in tests/fixtures/golden/bsp_seed_1337.json, con header.creation_date normalizzato a un placeholder fisso prima del confronto. Test golden marcato @pytest.mark.slow (marker gia registrato in pyproject.toml da TASK-1). Verificato sia pytest -q (256 test) sia pytest -m 'not slow' (255, il golden escluso) entrambi verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Test di integrazione sulla fixture 8x8 (patchata con texts_vis, gia fatto in TASK-15), parametri adattati alla scala della mappa: zero errori, grafo connesso, nessuna sovrapposizione. Golden file generato con pipeline completa e realistica (seed 1337), creation_date normalizzato, marcato slow. pytest -q (256) e pytest -m 'not slow' (255) entrambi verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
