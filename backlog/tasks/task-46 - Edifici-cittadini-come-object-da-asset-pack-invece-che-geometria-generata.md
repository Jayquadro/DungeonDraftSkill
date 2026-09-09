---
id: TASK-46
title: Edifici cittadini come object da asset pack invece che geometria generata
status: To Do
assignee:
  - '@claude'
created_date: '2026-09-08 08:57'
updated_date: '2026-09-08 14:22'
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

author: @claude
created: 2026-09-08 14:16
---
Ricerca fatta il 2026-09-08 prima di sospendere il task: Jay ha chiesto di implementare TASK-41 (preset di scala) PRIMA di questo.

MISURE REALI sul pack scelto (6VxwaRdj 'BB 51 Assets Houses1'), estratte dal file C:/Users/lorenzo_m/Documents/Dungeondraft/BB-51-Assets-Houses1.dungeondraft_pack (formato Godot PCK 'GDPC', letto con uno script di parsing; header IHDR dei PNG per le dimensioni):
- 51 texture object: 33 case, 10 tetti, 2 torri, 3 tende, 1 balcone, 2 bandiere.
- Le case vanno da 51x45 px a 248x205 px, cioe 0,20-0,97 quadretti a scala 1 (256 px/quadretto). Sono sprite da mappa di citta vista dall'alto, NON dalla scala giocabile 5 ft.
- Il pack e taggato 'Colorable': ogni object di questo pack piazzato da Dungeondraft porta il campo custom_color, sempre 'ff6b3834' nei 7 campioni colorabili di templates/rich_reference.dungeondraft_map (e il default del programma). Gli object non colorabili non hanno affatto il campo. Variare custom_color per edificio e il modo naturale di dare varieta ai tetti.

CONSEGUENZA SULLA SCALA: un lotto di TASK-35 e largo 8-16 quadretti; riempirlo con uno di questi sprite richiede scala ~15-20x (152 px stirati a ~2800). Mockup mostrati a Jay (render PIL, non output Dungeondraft): a scala citta ricalibrata (strade 1,5-3 q, lotti ~2,6 q, sprite 1-2x) un canvas 80x80 tiene ~230 edifici nitidi; con i lotti di TASK-35 lo sprite ingrandito e visibilmente sgranato da vicino. Per questo Jay ha chiesto TASK-41 prima: la scelta della scala va fatta come preset, non dentro questo task.

DECISIONE PRESA DA JAY su AC1 (catalogo): estendere 'ddforge catalog' a leggere direttamente i file .dungeondraft_pack, cosi entrano tutte e 51 le texture del pack piu le loro dimensioni in pixel (indispensabili per calcolare la scala di piazzamento e non ricavabili da un .dungeondraft_map, che non le contiene). Vincolo non negoziabile da mantenere: rifiutare le texture di un pack assente da header.asset_manifest del template. Oggi in data/assets.json ci sono solo 3 case (House10/House12/House28) piu Roof7, le uniche disegnate da Jay in rich_reference.
---

author: @claude
created: 2026-09-08 14:22
---
Vincolo di design da tenere presente per tutto il redesign di questo task (Jay, 2026-09-08): le mappe generate in modalita citta NON sono pensate per essere giocate/giocabili al tavolo in scala 5 ft come le mappe dungeon/grotta. Sono mappe di citta viste dall'alto (bird's-eye/top-down), uno sfondo/riferimento visivo — non serve un layout tattico con ingressi, arretramenti o dettagli utilizzabili in combattimento. Questo vincolo va tenuto presente nel piazzamento degli object edificio (AC2) e nella verifica finale con Jay (AC4): 'utilizzabile al tavolo' va inteso come 'leggibile come mappa di citta dall'alto', non come 'giocabile'.
---
<!-- COMMENTS:END -->
