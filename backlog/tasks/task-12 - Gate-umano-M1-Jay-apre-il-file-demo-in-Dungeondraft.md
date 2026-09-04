---
id: TASK-12
title: 'Gate umano M1: Jay apre il file demo in Dungeondraft'
status: In Progress
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:28'
updated_date: '2026-09-03 14:42'
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
- [ ] #1 A Jay e chiesto esplicitamente di verificare: la stanza appare, i muri sono chiusi, la porta e sul muro e non fluttua
- [ ] #2 Il verso di portal.direction per ciascuno dei quattro orientamenti di muro e determinato e documentato
- [ ] #3 Il segno e l'unita delle rotazioni delle porte sono determinati e documentati
- [ ] #4 Le regole calibrate sono codificate in build.py o compose.py, non lasciate solo nella documentazione
- [ ] #5 Jay conferma l'esito; se il file non si apre correttamente, il difetto e riprodotto in un test prima della correzione
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-03 14:42
---
Il file demo e pronto: generated/demo_m1.dungeondraft_map (generato da scripts/demo_m1.py, non committato — rigenerabile con 'python scripts/demo_m1.py' dopo 'pip install -e .[dev]' nel venv). Contiene 1 stanza 10x10 quadretti al centro di una mappa 80x80, con pavimento in pietra, 4 muri e una porta (door_00.png) sul muro inferiore della stanza. direction=(0,1) e rotation=0.0 sono placeholder non calibrati. In attesa che Jay lo apra in Dungeondraft e confermi.
---
<!-- COMMENTS:END -->
