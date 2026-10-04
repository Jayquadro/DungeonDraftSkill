---
id: TASK-67
title: 'Spike: codifica di terrain.splat e slot del terreno'
status: To Do
assignee: []
created_date: '2026-10-04 17:30'
updated_date: '2026-10-04 18:39'
labels: []
milestone: m-10
dependencies: []
references:
  - src/ddforge/cave_bitmap.py
  - src/ddforge/build.py
  - templates/rich_reference.dungeondraft_map
documentation:
  - docs/SPEC-decorate.md
  - docs/format.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
L'abbellimento (docs/SPEC-decorate.md §6.2, §7.3) vuole dipingere il terreno: terra e polvere ai bordi delle stanze, muschio, fango, erba fra gli edifici di una citta. Il livello ha `terrain` con 4 slot (`texture_1..texture_4`) e un blob `splat` di width×height×64 elementi, ma nessun codice del progetto lo scrive: e il template a fornirlo, mai modificato.

Lo spike, sul modello di TASK-31 per `cave.bitmap`, deve capire come e codificato lo splat (canali per slot, risoluzione sotto-cella, ordine), se si possono sostituire le texture degli slot con quelle del catalogo `terrain`, e verificarlo in Dungeondraft con campioni reali disegnati a mano da Jay. Se la codifica non si risolve, l'esito e una raccomandazione documentata di ripiego (pattern semitrasparenti).

Inoltre Jay ha deciso (SPEC-decorate §14 D6) che decorate cambia anche la texture del pavimento delle grotte (layer cave nativo): lo spike deve trovare in quale campo del livello sta, quali valori/texture accetta Dungeondraft e come scriverla senza toccare `cave.bitmap`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 La codifica di `terrain.splat` e documentata in docs/format.md in una nuova sezione, citando i file reali osservati
- [ ] #2 Esiste una funzione che scrive lo splat per una maschera data, coperta da test su fixture reali committate
- [ ] #3 E documentato se e come si cambiano le texture degli slot `texture_1..4`
- [ ] #4 Una mappa di prova con terreno dipinto e stata aperta in Dungeondraft da Jay e il terreno appare dove previsto
- [ ] #5 Se la codifica non e risolta, la nota di chiusura indica il ripiego da adottare in decorate
- [ ] #6 E documentato in docs/format.md in quale campo sta la texture del pavimento del layer cave e quali texture accetta, con una funzione che la imposta e una mappa di prova aperta da Jay in Dungeondraft con il pavimento della grotta cambiato
<!-- AC:END -->
