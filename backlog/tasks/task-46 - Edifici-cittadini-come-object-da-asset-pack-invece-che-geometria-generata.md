---
id: TASK-46
title: Edifici cittadini come object da asset pack invece che geometria generata
status: To Do
assignee: []
created_date: '2026-09-08 08:57'
updated_date: '2026-09-08 13:12'
labels: []
milestone: m-8
dependencies:
  - TASK-35
ordinal: 46000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Gate umano M5 (TASK-36): Jay valuta che il disegno della città (generators/city.py, TASK-35) debba concentrarsi su strade e piazze, mentre gli edifici sui lotti vadano rappresentati con object (sprite) pescati da un asset pack dedicato invece che con la geometria completa (muri/tetto/stanze) oggi generata riusando building.py a un solo piano. Jay deve ancora trovare/scegliere l'asset pack di edifici da usare: questo task va ripreso solo quando l'asset pack e' disponibile, non prima.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 L'asset pack di edifici scelto da Jay e' catalogato in data/assets.json (ddforge catalog) con i suoi object/texture disponibili
- [ ] #2 generators/city.py piazza un object edificio per lotto (dal nuovo asset pack) invece di disegnare un building.py completo, mantenendo fronte strada e arretramento gia' garantiti da TASK-35
- [ ] #3 Il documento generato passa validate() senza errori
- [ ] #4 Jay apre una città generata in Dungeondraft e conferma che il risultato e' utilizzabile al tavolo
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-08 09:54
---
Pack scelto per gli edifici cittadini: 6VxwaRdj "BB 51 Assets Houses1" (BluBerrey). Gia' catalogato in via preliminare in TASK-45 (2 object: BB_Houses1_House11.png, BB_Houses1_House12.png, disegnati in templates/rich_reference.dungeondraft_map). Riprendere questo task quando TASK-45 e' chiuso e data/assets.json committato con questo pack.
---

author: @claude
created: 2026-09-08 13:12
---
Decisioni/domande aperte spostate qui da TASK-36 (Jay: 'voglio modificare tutta la gestione della città nel task 46, chiudi TASK-36 con solo le cose relative alle grotte').

Dal gate umano round 1 di TASK-36 (file generated/city_task35.dungeondraft_map / city_m5.dungeondraft_map, mai confermato da Jay — sostituito qui dal redesign):

1. Nota già in TASK-35 (implementation notes): l'ingresso di ogni edificio è sempre sul lato sud LOCALE del lotto (comportamento di building.py, mai corretto), indipendentemente da quale lato del lotto è il fronte-strada. Per i lotti con fronte diverso da 'sud', l'ingresso non guarda la strada. Con la nuova gestione a object da asset pack (questo task) il problema potrebbe sparire da solo (un object piazzato non ha un 'ingresso' nello stesso senso) — da verificare quando si progetta il piazzamento.

2. Domanda mai risposta da Jay: isolati/strade/piazze (la parte che TASK-46 vuole mantenere procedurale) si leggono bene così come generate da TASK-35? Se il redesign tocca anche la rete stradale, vale la pena chiedere di nuovo con un file aggiornato una volta scelto l'asset pack.
---
<!-- COMMENTS:END -->
