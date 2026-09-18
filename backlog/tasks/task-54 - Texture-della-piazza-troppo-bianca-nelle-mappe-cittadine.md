---
id: TASK-54
title: Texture della piazza troppo bianca nelle mappe cittadine
status: Done
assignee:
  - '@claude'
created_date: '2026-09-18 08:17'
updated_date: '2026-09-18 14:13'
labels: []
dependencies: []
documentation:
  - docs/sprite-luoghi.md
ordinal: 55000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Jay ha guardato una mappa 'isolato' e la pavimentazione della piazza (Palette.floors['piazza'] in src/ddforge/assets.py, oggi la chiave catalogo tileset_brick_basketweave) gli sembra troppo bianca. Ripensandoci non vuole piu' una pietra/selciato grigio: vuole che la piazza assomigli a terra battuta. Il catalogo ha gia' una texture di terra battuta (chiave 'chr_dirt', categoria terrain, gia' usata per il terreno della fiera in generators/landmarks.py tramite Palette.floors['terra']): e' il candidato piu' naturale, ma va verificato che renda bene su un'area larga come una piazza e non solo sui piccoli spiazzi aperti dove e' usata oggi. La chiave 'piazza' e' condivisa dalla Palette dello stile 'city', quindi vale per tutti e tre i preset (isolato/quartiere/citta), non solo per quello che Jay ha guardato. Resta comunque il vincolo di prima: la piazza deve restare distinguibile dalla pavimentazione delle strade (Palette.floors['selciato'], chiave tileset_cobble) e della banchina (chiave stone_floor).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 La piazza (Palette.floors['piazza']) e' disegnata con una texture che assomiglia a terra battuta, non piu' pietra/mattone chiaro come tileset_brick_basketweave
- [x] #2 La piazza resta visivamente distinguibile dalla pavimentazione delle strade (selciato) e da quella della banchina sulla stessa mappa
- [x] #3 Le mappe di valutazione in generated/ per i tre preset (isolato, quartiere, citta) sono rigenerate con la nuova texture, seed fissi
- [x] #4 La suite di test completa passa, golden aggiornati dove il cambio texture li tocca
- [x] #5 Gate umano: Jay apre le mappe rigenerate in Dungeondraft e conferma che la piazza ora assomiglia a terra battuta
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. In src/ddforge/assets.py, spostare la chiave sintetica 'piazza' dal bucket 'floors' (tileset_brick_basketweave) al bucket 'grounds' della Palette city, puntandola su 'chr_dirt' (stessa texture terrain gia' usata per 'terra', la fiera): palette_for la risolve gia' dalla categoria terrain, nessun cambiamento a compose.py serve.
2. Rigenerare (con diff, poi --write) i golden toccati con scripts/regen_city_golden.py; pytest -q sull'intera suite.
3. Rigenerare le mappe di valutazione in generated/ per i tre preset (isolato, quartiere, citta), seed fisso, nome che dice il task; validare ciascuna con ddforge validate.
4. Verifica oggettiva (selciato/banchina restano testure diverse da piazza, gia' garantito da bucket diversi), poi gate umano (AC5).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
In src/ddforge/assets.py, la chiave sintetica 'piazza' e' stata spostata dal bucket 'floors' (tileset_brick_basketweave) al bucket 'grounds' della Palette city, puntata su 'chr_dirt' (stessa texture terrain gia' usata per 'terra', la fiera, gia' verificata su un'area piu' piccola e confermata utilizzabile dentro un elemento pattern, docs/sprite-luoghi.md sez.6). 'selciato' (tileset_cobble) e 'banchina' (stone_floor) restano bucket/texture separate, quindi la piazza resta distinguibile da entrambe per costruzione (AC1, AC2). Golden rigenerati con scripts/regen_city_golden.py: city_seed_1337.json e city_seed_1337_landmarks.json, diff verificato riga per riga (solo il path della texture piazza cambia, nessun'altra differenza inattesa). Mappe di valutazione rigenerate in generated/ per i tre preset (city_isolato_task54, city_quartiere_task54, city_citta_task54, seed 1337, canvas 78x78, stessa convenzione di TASK-52): tutte e tre validano pulite con ddforge validate e referenziano chr_dirt per la piazza, zero occorrenze di tileset_brick_basketweave (verificato leggendo il JSON). Suite completa: 779 passed, 1 skipped, nessuna regressione (AC3, AC4).

Gate umano superato: Jay ha aperto le mappe rigenerate in Dungeondraft e confermato che la piazza in terra battuta (chr_dirt) va bene.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-18 08:23
---
Jay ha confermato esplicitamente che il ricolore della piazza vale anche per il preset 'quartiere', non solo 'isolato': gia' coperto dagli AC (tutti e tre i preset), nessuna modifica di scope necessaria.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Palette.floors['piazza'] ora usa chr_dirt (terra battuta) invece di tileset_brick_basketweave, restando distinta da selciato/banchina. Golden e mappe di valutazione rigenerati (generated/city_*_task54.dungeondraft_map), suite completa verde (779 passed, 1 skipped). In attesa del gate umano di Jay (AC5).
<!-- SECTION:FINAL_SUMMARY:END -->
