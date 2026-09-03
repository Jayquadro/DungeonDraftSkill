---
id: TASK-2
title: Ricognizione e messa in sicurezza dei template .dungeondraft_map reali
status: To Do
assignee: []
created_date: '2026-09-03 11:25'
labels: []
milestone: m-0
dependencies: []
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Jay ha gia esportato dalla sua installazione i file di riferimento, ma i nomi possono variare: cerca `*.dungeondraft_map` nelle cartelle di lavoro, catalogali e identifica i due che servono: un template vuoto di dimensione tipica (es. 40x40), scheletro di produzione, e un template ricco che contiene un esemplare di ogni tipo di elemento (muro, porta, finestra, pavimento, oggetto, luce, tetto, percorso, testo). Copiali in templates/ come blank_40x40.dungeondraft_map e rich_reference.dungeondraft_map, in sola lettura: un .dungeondraft_map malformato puo in rari casi far crashare Dungeondraft, quindi si lavora sempre su copie (SPEC.md §14). Se manca il template ricco o non contiene luci e testi, fermati e chiedi a Jay di esportarlo: non inventare gli schemi mancanti.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Tutti i file .dungeondraft_map trovati sono elencati con percorso, dimensione mappa (world.width x world.height), format, creation_build e conteggio degli elementi per tipo
- [ ] #2 templates/blank_40x40.dungeondraft_map e templates/rich_reference.dungeondraft_map esistono e sono documentati
- [ ] #3 I template in templates/ sono trattati come sola lettura e mai modificati dal codice
- [ ] #4 Le costanti derivate (world.format, header.creation_build, elenco pack ID con nome/autore/versione) sono registrate in docs/format.md
- [ ] #5 Se il template ricco manca o non contiene almeno una luce e un testo, il task si ferma con una richiesta esplicita a Jay invece di procedere con schemi inventati
<!-- AC:END -->
