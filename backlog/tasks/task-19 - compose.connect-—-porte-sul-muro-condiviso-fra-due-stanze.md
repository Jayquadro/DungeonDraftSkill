---
id: TASK-19
title: compose.connect — porte sul muro condiviso fra due stanze
status: To Do
assignee: []
created_date: '2026-09-03 11:31'
labels: []
milestone: m-3
dependencies:
  - TASK-18
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
La funzione più delicata del progetto (SPEC.md §6.6). Il muro condiviso fra due stanze adiacenti va trovato geometricamente e convertito in una frazione t lungo quel muro; se non esiste muro condiviso, connect genera un corridoio a L. Prescrizione esplicita della spec: scrivere test unitari con rettangoli noti PRIMA di implementare qualsiasi generatore.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 I test unitari su rettangoli noti sono scritti prima dell'implementazione e coprono adiacenza orizzontale, verticale, parziale e assenza di contatto
- [ ] #2 Per due stanze adiacenti connect trova il muro condiviso e vi colloca una porta con t nell'intervallo [0, 1]
- [ ] #3 La porta risultante è centrata sulla sovrapposizione dei due muri, non sul muro intero
- [ ] #4 Per due stanze non adiacenti connect genera un corridoio a L che le collega
- [ ] #5 Nessuna porta viene generata a distanza minore di 0.05 da un'altra sullo stesso muro (DDF105)
- [ ] #6 Il documento risultante passa validate() senza errori né warning DDF102
<!-- AC:END -->
