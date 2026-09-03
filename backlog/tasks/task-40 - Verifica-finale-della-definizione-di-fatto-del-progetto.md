---
id: TASK-40
title: Verifica finale della definizione di fatto del progetto
status: To Do
assignee: []
created_date: '2026-09-03 11:35'
labels: []
milestone: m-7
dependencies:
  - TASK-38
  - TASK-30
  - TASK-36
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 40000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Controllo di chiusura contro SPEC.md §15. Il progetto è completo quando: pytest è verde con copertura di tutti i codici DDFxxx; ddforge generate dungeon --seed 1 --rooms 8 produce un file che Jay apre e trova utilizzabile al tavolo senza ritocchi manuali di struttura; lo stesso vale per building, cave e city; la skill genera una mappa da una frase in italiano; il README spiega come esportare un nuovo template. Questo task verifica ciascun punto e apre task di follow-up per quelli non soddisfatti.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 pytest è verde e ogni codice DDFxxx ha un test dedicato
- [ ] #2 Tutti e quattro gli stili producono file che Jay conferma utilizzabili al tavolo senza ritocchi strutturali
- [ ] #3 La skill genera una mappa a partire da una frase in italiano
- [ ] #4 Il README documenta la procedura di riesportazione del template
- [ ] #5 Ogni punto non soddisfatto ha un task di follow-up aperto in Backlog
<!-- AC:END -->
