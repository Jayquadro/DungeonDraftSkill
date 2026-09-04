---
id: TASK-28
title: 'generators/building.py — perimetro, suddivisione interna e tipologie'
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:34'
updated_date: '2026-09-04 07:28'
labels: []
milestone: m-4
dependencies:
  - TASK-27
  - TASK-20
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generatore di edifici urbani, secondo in ordine di priorità (SPEC.md §1.4, §9.2): perimetro esterno rettangolare o a L; suddivisione interna ricorsiva con muri portanti; un vano scale allineato verticalmente su tutti i piani; distribuzione delle stanze per piano secondo la tipologia. Taverna: piano terra sala comune, cucina e retro, primo piano camere. Magione: terra rappresentanza, primo privato, sottotetto servitù. Magazzino: terra volume unico con soppalco.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Il generatore produce perimetri sia rettangolari sia a L
- [x] #2 Le tre tipologie taverna, magione e magazzino producono distribuzioni di stanze distinte e coerenti con la descrizione della spec
- [x] #3 Ogni stanza è raggiungibile: nessun vano cieco senza porta
- [x] #4 Il vano scale è presente e allineato su tutti i piani
- [x] #5 Lo stesso seed produce lo stesso Blueprint
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Riusare l'infrastruttura gia testata di bsp.py (TASK-21), generica e non specifica al dungeon: _build_tree/_inscribe_room per la partizione, _connect_rooms per porte/corridoi (import diretto, nessuna duplicazione). Footprint: un rettangolo, o due rettangoli che insieme formano una L (notch fisso in basso a destra quando l_shaped=True — non serve randomizzare l'angolo, un solo caso testabile e sufficiente per l'AC). Vano scale: striscia riservata di 2 quadretti sul lato sinistro del footprint originale, esclusa dal footprint di generazione stanze su OGNI piano (mai sovrapposta per costruzione, niente da verificare a posteriori). _BUILDING_TYPES mappa tipologia -> lista (piano, [kind per stanza]) secondo SPEC.md §9.2 (taverna: terra sala_comune+cucina+retro, primo camere; magione: terra rappresentanza, primo privato, sottotetto servitu; magazzino: terra volume unico, primo soppalco su meta pianta). Budget di stanze per parte del footprint proporzionale all'area. Connessione per piano con un albero minimo (nearest-neighbor, non serve la ricorsione BSP ne gli anelli: un edificio si legge bene anche come albero puro), garantendo che ogni stanza sia raggiungibile. graph del Blueprint finale = unione dei grafi per piano con indici offsettati (i piani non sono collegati fra loro nel grafo delle stanze: le scale li collegano fisicamente, non serve un arco). Test: perimetro rettangolare e a L (verificato controllando che un angolo del bounding box resti privo di stanze), le 3 tipologie producono kind distinti e coerenti, ogni stanza ha almeno una porta, stairs_rect identico e mai sovrapposto alle stanze su ogni piano, stesso seed -> stesso Blueprint.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Riusata l'infrastruttura di bsp.py (TASK-21), generica: _build_tree/_inscribe_room per la partizione, _connect_rooms/_non_colliding_t per porte/corridoi, import diretto senza duplicazione. Footprint rettangolare o a L (notch fisso in basso a destra quando l_shaped=True). Vano scale: striscia di 2 quadretti riservata sul lato sinistro del footprint originale, esclusa dal footprint di generazione stanze su OGNI piano — mai sovrapposta per costruzione. Connessione per piano con albero minimo per vicinanza (nearest-neighbor/Prim), non la ricorsione BSP: un edificio si legge bene anche come albero puro, non servono anelli. Bug reale trovato con lo smoke test manuale prima dei test formali: nessun edificio aveva una porta d'ingresso verso l'esterno, e il magazzino (1 sola stanza per piano) restava completamente senza porte su entrambi i piani. Corretto con _ensure_entry: piano terra sempre con una porta d'ingresso (anche se le stanze hanno gia porte interne fra loro, che non danno accesso dall'esterno); altri piani solo se nessuna stanza ha gia una porta (il caso del soppalco). Verificato su 15 seed x 3 tipologie: zero stanze senza porte. 16 test in tests/test_building.py: footprint rettangolare/a L (notch verificato vuoto), le 3 tipologie con kind distinti e coerenti con SPEC.md §9.2, ogni stanza con porta su 15 seed, raggiungibilita interna per piano, vano scale mai sovrapposto, riproducibilita, e un test end-to-end che renderizza davvero con draw_building e verifica zero errori di validazione per tutte e 3 le tipologie. Suite completa: 279 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementato generators/building.py riusando l'infrastruttura di bsp.py (partizione, connessione). Footprint rettangolare o a L, vano scale mai sovrapposto per costruzione, 3 tipologie con kind distinti (SPEC.md §9.2). Trovato e corretto un bug reale con lo smoke test manuale: nessun edificio aveva una porta d'ingresso, il magazzino restava senza porte su entrambi i piani. 16 test nuovi inclusa un'integrazione end-to-end con draw_building+validate. Suite completa: 279 test verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
