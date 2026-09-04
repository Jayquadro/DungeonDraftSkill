---
id: TASK-12
title: 'Gate umano M1: Jay apre il file demo in Dungeondraft'
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:28'
updated_date: '2026-09-04 07:46'
labels: []
milestone: m-1
dependencies:
  - TASK-11
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Passaggio manuale obbligatorio (SPEC.md §5). Nessuna documentazione cattura il verso di portal.direction, il segno delle rotazioni e l'allineamento esatto delle porte: vanno calibrati su screenshot. Quando il file demo e pronto, fermati e chiedi esplicitamente a Jay di aprirlo, indicando cosa controllare. I valori corretti vanno poi fissati come costanti o regole nel codice e annotati in docs/format.md, cosi le milestone successive non ripartono da zero.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A Jay e chiesto esplicitamente di verificare: la stanza appare, i muri sono chiusi, la porta e sul muro e non fluttua
- [x] #2 Il verso di portal.direction per ciascuno dei quattro orientamenti di muro e determinato e documentato
- [x] #3 Il segno e l'unita delle rotazioni delle porte sono determinati e documentati
- [x] #4 Le regole calibrate sono codificate in build.py o compose.py, non lasciate solo nella documentazione
- [x] #5 Jay conferma l'esito; se il file non si apre correttamente, il difetto e riprodotto in un test prima della correzione
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Aggiunto test parametrico test_draw_room_door_direction_and_rotation_for_all_four_wall_orientations (tests/test_compose.py) che copre esplicitamente i 4 lati del perimetro (top/right/bottom/left) con direction/rotation attesi dalla formula tangente. Suite completa: 282 test verdi (era 278).
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-03 14:42
---
Il file demo e pronto: generated/demo_m1.dungeondraft_map (generato da scripts/demo_m1.py, non committato — rigenerabile con 'python scripts/demo_m1.py' dopo 'pip install -e .[dev]' nel venv). Contiene 1 stanza 10x10 quadretti al centro di una mappa 80x80, con pavimento in pietra, 4 muri e una porta (door_00.png) sul muro inferiore della stanza. direction=(0,1) e rotation=0.0 sono placeholder non calibrati. In attesa che Jay lo apra in Dungeondraft e confermi.
---

author: @claude
created: 2026-09-04 06:54
---
Ricevuto screenshot (screenshots/task12.png) da Jay. Osservazione: 3 muri (alto, sinistra, destra) sono puliti e corretti — perimetro chiuso, texture pietra regolare, angoli a 90 gradi. Il MURO INFERIORE (quello con la porta, wall_index=2) e visibilmente rotto: invece di una linea unica appare spezzato in due segmenti non allineati, con un piccolo elemento rossastro verticale nel punto di discontinuita (quasi certamente lo sprite della porta, probabilmente ruotato in modo sbagliato). Ipotesi di lavoro: la formula rotation=atan2(direction.y, direction.x) (derivata da soli 3 campioni statici, docs/format.md §5) non e la convenzione giusta per Dungeondraft — possibile che rotation vada espressa relativa alla tangente del muro invece che in coordinate assolute, o che manchi un offset costante, o che il segno di direction sia invertito. In attesa di chiarimenti da Jay prima di modificare la formula.
---

author: @claude
created: 2026-09-04 07:06
---
Applicata la correzione: direction e la tangente del muro (non la normale), confermata sui 2 campioni reali di rich_reference (vedi docs/format.md §5). compose._wall_tangent sostituisce _outward_normal. Rigenerato generated/demo_m1.dungeondraft_map: la porta ora ha direction=(-1,0) rotation=3.141593, identico all'esempio verificato di SPEC.md §13. Tutti i 244 test restano verdi. In attesa che Jay riapra il file e confermi visivamente che ora il muro e la porta sono corretti.
---

author: @claude
created: 2026-09-04 07:36
---
Verificati i timestamp: task12.png (06:49 UTC), task12_zoom.png (06:59 UTC) e task12_selected.png (07:00 UTC) sono TUTTI anteriori alla rigenerazione del file con il fix del commento #3 (generated/demo_m1.dungeondraft_map, 07:05 UTC, commit 4ba4182). Il file che Jay aveva aperto per questi screenshot era quindi ancora la versione pre-fix (direction=normale uscente), coerente con il muro inferiore spezzato in due segmenti storti e la porta ruotata male che si vede nelle immagini.

Controllo diretto del file attuale su disco (post-fix): il muro inferiore e la retta (11520,11520)->(8960,11520), stesso y su entrambi gli estremi, nessuna spezzatura. Il portale ha direction=(-1,0) e rotation=3.141592653589793 (=pi), identico al campione verificato in SPEC.md §13. I dati sono geometricamente corretti.

Richiesta a Jay: chiudere il file demo_m1 in Dungeondraft (se ancora aperto) e riaprirlo da capo (File > Open), poi rifare gli screenshot. Dungeondraft non ricarica automaticamente un file modificato su disco mentre e aperto nell'editor.
---

author: @jayquadro
created: 2026-09-04 07:45
---
Jay ha riaperto il file rigenerato e conferma: muro chiuso, porta correttamente sul muro, nessuna spezzatura.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Bug: portal.direction era calcolata come normale uscente dal muro invece che come tangente, causando nello screenshot di Jay un muro visivamente spezzato e una porta ruotata di 90 gradi. Fix: compose._wall_tangent (ex _outward_normal) ora ritorna il vettore dal primo all'ultimo punto del muro, confermato sui 2 campioni reali di rich_reference.dungeondraft_map (docs/format.md §5). Verificato con: (1) test unitario che riproduce il bug (_wall_tangent su muri orizzontali/verticali/invertiti), (2) nuovo test parametrico sui 4 orientamenti del perimetro di draw_room, (3) rigenerazione di generated/demo_m1.dungeondraft_map con valori identici all'esempio verificato di SPEC.md §13, (4) conferma visiva di Jay dopo aver riaperto il file rigenerato in Dungeondraft. Le regole sono codificate in compose.py (_wall_tangent, _rotation_for_direction), non solo documentate.
<!-- SECTION:FINAL_SUMMARY:END -->
