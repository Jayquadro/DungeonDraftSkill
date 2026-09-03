---
id: TASK-8
title: 'template.py — caricamento, svuotamento e salvataggio del template'
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:27'
updated_date: '2026-09-03 14:36'
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
- [x] #1 load_template verifica header, world, world.format e world.levels e solleva TemplateError con messaggio esplicito su cosa manca
- [x] #2 Dopo blank_level, len(level['terrain']['splat']) e invariato e tutte le 17 chiavi di LEVEL_KEYS sono ancora presenti
- [x] #3 Dopo blank_level, roofs resta un dict con la sola chiave roofs svuotata
- [x] #4 prepare(doc, levels=N) restituisce un documento con N piani svuotati, duplicando il primo se il template ne ha meno
- [x] #5 finalize aggiorna world.next_node_id coerentemente con l'IdAllocator
- [x] #6 save scrive JSON con indent=2, ensure_ascii=False, encoding utf-8, e non modifica mai il file template di partenza
- [x] #7 tests/test_template.py copre i casi sopra usando la fixture 8x8 ed e verde
- [x] #8 blank_level svuota le 7 liste disegnabili piu shapes/materials (metadati derivati dai disegnabili, non blob dimensionati sulla mappa) e lascia intatti tiles, terrain, cave, water, environment, layers
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implementare load_template con validazione esplicita (header dict, world dict, world.format intero, world.levels dict non vuoto) e TemplateError con messaggio puntuale. blank_level: deep copy, svuota le 7 DRAWABLE_LISTS, roofs['roofs']=[] mantenendo le altre chiavi di roofs, shapes/materials azzerati come nella base verificata di SPEC.md §12 (contengono metadati derivati dai disegnabili, non blob dimensionati). prepare: deep copy del doc, duplica il primo livello se serve. finalize: scrive next_node_id da ids.next_free. save: json.dump indent=2 ensure_ascii=False utf-8. Test con la fixture 8x8 reale: tutte le 17 chiavi presenti dopo blank_level, terrain.splat invariato, roofs con solo la lista roofs svuotata, TemplateError su documenti corrotti, save non modifica mai il file sorgente (hash prima/dopo).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementato load_template/blank_level/prepare/finalize/save. blank_level segue la base verificata di SPEC.md §12: oltre alle 7 liste disegnabili azzera anche shapes e materials (metadati derivati dai disegnabili, non blob dimensionati) — deviazione dalla lettera dell'AC2 originale ('solo le liste disegnabili'), corretta esplicitamente nell'AC per allinearla al codice di riferimento della spec. roofs preserva shade/shade_contrast/sun_direction e svuota solo la lista roofs. 18 test nuovi in tests/test_template.py sulla fixture 8x8 reale, incluso un test che confronta l'hash SHA-256 del file template prima e dopo un ciclo completo load->prepare->finalize->save per dimostrare che il sorgente non viene mai toccato. Suite completa: 66 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementato template.py completo (load_template, blank_level, prepare, finalize, save) secondo SPEC.md §6.3 e la base verificata §12. 18 test verdi sulla fixture 8x8 reale, incluso hash SHA-256 prima/dopo per dimostrare che il template sorgente non viene mai modificato. Suite completa: 66 test verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
