---
id: TASK-52
title: >-
  Integrare il pack nel catalogo e rigenerare le mappe di valutazione in
  generated/
status: To Do
assignee: []
created_date: '2026-09-15 07:18'
labels: []
milestone: m-9
dependencies:
  - TASK-51
documentation:
  - docs/sprite-luoghi.md
priority: high
type: feature
ordinal: 53000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Finche' il pacchetto non e' montato sulle mappe non si puo' dire se funziona. Oggi i luoghi urbani notevoli usano sprite di ripiego scelti fra i 440 object dei pack di Jay (assets._CITY_LANDMARK_SPRITES: l'ospedale, per esempio, cade su house_02), e le case ordinarie usano le icone piatte del pacchetto BB Houses1. E' proprio la convivenza di due registri grafici diversi il motivo per cui la mappa non e' ancora bella, come annotato in docs/sprite-luoghi.md sez. 8.

Quando il pack e' importabile (TASK-51) va agganciato al sistema e i file in generated/ vanno rigenerati, perche' e' li' che Jay guarda il risultato: aprendo i .dungeondraft_map in Dungeondraft deve vedere i nuovi sprite al posto dei ripieghi e poter giudicare l'insieme, non il singolo pezzo.

Da coprire: lettura del nuovo pack nel catalogo asset (data/assets.json), voci di assets._CITY_LANDMARK_SPRITES che puntano ai nuovi nm_* per i luoghi coperti dal pacchetto lasciando il ripiego a quelli ancora scoperti, e rigenerazione dei file di valutazione in generated/ sui tre preset di scala (isolato, quartiere, citta) con seed fissi, cosi' che due rigenerazioni successive siano confrontabili.

Vanno rigenerati anche i golden di tests/fixtures/golden se il cambio di sprite li tocca, e la suite deve restare verde.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Il pack nuovo e' letto dal catalogo asset e i suoi sprite compaiono in data/assets.json con le dimensioni native lette dall'header PNG
- [ ] #2 assets._CITY_LANDMARK_SPRITES punta ai nuovi nm_* per ogni luogo coperto dal pacchetto, e conserva lo sprite di ripiego per i luoghi non ancora coperti
- [ ] #3 generated/ contiene mappe di valutazione rigenerate per i tre preset isolato, quartiere e citta, con seed fissi e nomi che dicono a quale task appartengono
- [ ] #4 Le mappe rigenerate si aprono in Dungeondraft senza errori e superano ddforge validate
- [ ] #5 Un documento o una sezione di docs/ elenca quali luoghi usano ormai uno sprite del pacchetto e quali sono ancora sul ripiego, cosi' si sa cosa resta da disegnare
- [ ] #6 I golden di tests/fixtures/golden sono aggiornati dove il cambio di sprite li tocca e la suite completa passa
- [ ] #7 Gate umano: Jay apre le mappe di generated/ in Dungeondraft e giudica il risultato complessivo
<!-- AC:END -->
