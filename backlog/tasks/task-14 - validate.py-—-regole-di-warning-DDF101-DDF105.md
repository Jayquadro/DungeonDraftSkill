---
id: TASK-14
title: validate.py — regole di warning DDF101-DDF105
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:28'
updated_date: '2026-09-04 06:27'
labels: []
milestone: m-2
dependencies:
  - TASK-13
documentation:
  - docs/SPEC.md
priority: medium
type: feature
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Warning che non bloccano la generazione ma segnalano mappe probabilmente sbagliate al tavolo (SPEC.md §7): elementi fuori canvas, stanze irraggiungibili, muri e pattern degeneri, porte troppo vicine sullo stesso muro. Servono soprattutto ai generatori delle milestone successive come rete di sicurezza.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 DDF101 segnala elementi con coordinate fuori dal canvas width x height
- [x] #2 DDF102 segnala stanze non raggiungibili dal grafo, cioe senza alcuna porta
- [x] #3 DDF103 segnala muri con meno di 2 punti e DDF104 pattern con meno di 3 punti
- [x] #4 DDF105 segnala due porte sullo stesso muro a distanza minore di 0.05
- [x] #5 I warning sono distinguibili dagli errori tramite il campo severity
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
DDF101 (fuori canvas): per ogni tipo di elemento, controllare le coordinate assolute pertinenti (walls/patterns/roofs: points assoluti; objects/lights/texts/portals: position; paths: position + edit_points sommati) contro [0, width*GRID] x [0, height*GRID]. DDF102 (stanza irraggiungibile): euristica a componenti connesse sui muri di un livello, unendo due muri che condividono un punto estremo (union-find), poi segnalare le componenti senza nessuna porta annidata in nessun muro del gruppo — dichiarata esplicitamente come euristica, non geometria esatta. DDF103/104: conteggio punti di wall/pattern. DDF105: confronto a coppie di wall_distance fra le porte dello stesso muro. Fixture dedicate per ognuno dei 5 codici in tests/test_validate.py, piu verifica che i warning non alzino severity error e non blocchino un documento altrimenti valido.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementate le 5 regole di warning. DDF101 (fuori canvas) controlla le coordinate assolute pertinenti per tipo: points per walls/patterns/roofs, position per objects/lights/texts, position+edit_points sommati per paths. DDF102 (stanza irraggiungibile) e un'euristica esplicita, non geometria esatta: componenti connesse sui muri via union-find su endpoint condivisi, warning se nessun muro del gruppo ha una porta annidata — documentato nel codice che un muro isolato senza porta puo essere decorativo, non necessariamente un errore, da cui la severity warning. Verificato con smoke test sui file reali (blank_80x80, rich_reference, demo_m1): zero warning spuri; costruito anche un caso deliberatamente rotto (stanza a 4 muri senza porta) per confermare che DDF102 scatta quando deve. 15 test nuovi in tests/test_validate.py. Suite completa: 128 test verdi.

Correzione post-chiusura (scoperta durante TASK-19): un canale-corridoio aperto (compose.connect) e fatto di muri paralleli isolati che non condividono estremi ne fra loro ne con le stanze che collegano. Un singolo muro non loopato, isolato (gruppo di 1 nell'union-find), non forma mai un perimetro chiuso: due segmenti rettilinei scollegati non delimitano un'area, quindi non puo essere 'la stanza a cui manca la porta'. Aggiunta un'eccezione esplicita in _check_ddf102_unreachable_rooms: i gruppi di un solo muro senza loop=True vengono saltati (un muro loopato resta invece un perimetro chiuso a se stante e continua a essere segnalato). Senza questa correzione, ogni corridoio generato da connect() avrebbe prodotto falsi positivi DDF102 sistematici. Due nuovi test di regressione in tests/test_validate.py.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementate le 5 regole di warning DDF101-105. DDF102 e un'euristica dichiarata a componenti connesse sui muri (union-find su endpoint condivisi), verificata sia sui file reali (zero falsi positivi) sia su un caso deliberatamente rotto costruito per l'occasione. 15 test nuovi, suite completa 128 test verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
