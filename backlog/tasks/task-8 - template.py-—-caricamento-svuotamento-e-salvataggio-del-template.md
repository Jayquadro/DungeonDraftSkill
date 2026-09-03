---
id: TASK-8
title: 'template.py — caricamento, svuotamento e salvataggio del template'
status: To Do
assignee: []
created_date: '2026-09-03 11:27'
labels: []
milestone: m-1
dependencies:
  - TASK-2
  - TASK-7
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Il vincolo che determina tutta l'architettura (SPEC.md §2): il generatore NON costruisce il JSON da zero, ma carica un template .dungeondraft_map esportato dall'installazione reale, svuota SOLO le liste disegnabili e ci inietta la geometria. Il template porta con se i blob binari della dimensione giusta, i pack ID reali, il creation_build corretto e il world.format atteso dall'eseguibile. Un tentativo precedente del progetto e fallito esattamente qui: produceva JSON sintatticamente valido che Dungeondraft apriva vuoto, senza errori. API: LEVEL_KEYS (17 chiavi), DRAWABLE_LISTS (7 liste), load_template, blank_level, prepare, finalize, save (SPEC.md §6.3).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 load_template verifica header, world, world.format e world.levels e solleva TemplateError con messaggio esplicito su cosa manca
- [ ] #2 blank_level svuota solo le 7 liste disegnabili e lascia intatti tiles, terrain, cave, water, environment, layers
- [ ] #3 Dopo blank_level, len(level['terrain']['splat']) e invariato e tutte le 17 chiavi di LEVEL_KEYS sono ancora presenti
- [ ] #4 Dopo blank_level, roofs resta un dict con la sola chiave roofs svuotata
- [ ] #5 prepare(doc, levels=N) restituisce un documento con N piani svuotati, duplicando il primo se il template ne ha meno
- [ ] #6 finalize aggiorna world.next_node_id coerentemente con l'IdAllocator
- [ ] #7 save scrive JSON con indent=2, ensure_ascii=False, encoding utf-8, e non modifica mai il file template di partenza
- [ ] #8 tests/test_template.py copre i casi sopra usando la fixture 8x8 ed e verde
<!-- AC:END -->
