---
id: TASK-15
title: Fixture corrotte e test per ogni codice DDFxxx
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:28'
updated_date: '2026-09-04 06:09'
labels: []
milestone: m-2
dependencies:
  - TASK-13
  - TASK-14
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Criterio di completamento di M2 (SPEC.md §5, §7): per OGNI codice DDFxxx serve una fixture che lo viola e un test che verifica che validate() lo segnali. Le fixture si costruiscono corrompendo in modo mirato il template 8x8, un difetto per fixture, cosi il test isola una sola regola.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Esiste una fixture corrotta per ciascuno dei 15 codici di errore e dei 5 di warning
- [x] #2 Per ogni codice esiste un test che verifica che validate() lo segnali con severity e path corretti
- [x] #3 Un test verifica che il documento generato dallo script demo di M1 non produca alcun errore
- [x] #4 Un test verifica che non ci siano falsi positivi: una fixture valida produce zero Issue di severity error
- [x] #5 pytest -q e verde
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
reference_8x8.dungeondraft_map (TASK-5) non ha ne muri ne pattern ne luci ne portali (solo 5 oggetti e 1 path): creare una fixture pytest 'valid_doc' che parte da una deepcopy del documento reale e aggiunge un esemplare di ogni tipo di elemento mancante (wall+portal annidato, pattern, light) con valori realistici presi da docs/format.md, piu texts_vis per allinearsi a LEVEL_KEYS. Verificare che questa fixture arricchita produca zero errori (AC4). Per ciascuno dei 15 codici di errore e 5 di warning, una funzione helper che parte da una deepcopy di valid_doc, applica UNA corruzione mirata, e verifica che l'Issue con quel codice esista con la severity attesa e un path non vuoto. Riusare il test gia esistente su demo_m1 per AC3 (gia coperto in TASK-13).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
reference_8x8.dungeondraft_map (TASK-5) non contiene ne muri ne portali ne pattern ne luci (solo 5 oggetti e 1 path): creata una fixture valid_doc che deriva da una deepcopy del file reale e aggiunge un esemplare di ciascun tipo mancante con valori realistici (docs/format.md), usando node_id esadecimali coerenti col resto del file (10-13) e next_node_id aggiornato. Verificato che questa fixture arricchita produce zero errori (AC4). tests/test_validate_fixtures.py: 21 test, uno per ciascuno dei 15 codici di errore + 5 di warning (piu il test del baseline valido), ognuno verifica code, severity E path non vuoto/puntuale sull'Issue specifica trovata. Il test su demo_m1 (AC3) era gia coperto in TASK-13 (test_validate_on_real_demo_m1_output_has_zero_errors). Suite completa: 149 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
tests/test_validate_fixtures.py: 21 test derivati dal template 8x8 reale (arricchito con un esemplare di wall/portal/pattern/light, assenti dall'originale). Uno per ciascuno dei 20 codici DDFxxx, verifica code+severity+path; baseline valido a zero errori. Suite completa: 149 test verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
