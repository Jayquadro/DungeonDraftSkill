---
id: TASK-38
title: Skill Claude dungeondraft-map-generator che invoca il CLI
status: To Do
assignee: []
created_date: '2026-09-03 11:35'
labels: []
milestone: m-7
dependencies:
  - TASK-36
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 38000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
La skill va riscritta evitando l'errore da non ripetere (SPEC.md §11): NON deve contenere lo schema del formato né riscrivere il generatore; deve essere sottile e chiamare il CLI. SKILL.md descrive un workflow di quattro passi: interpretare la richiesta in linguaggio naturale scegliendo style, dimensioni, numero di stanze e densità di arredo; invocare ddforge generate con quei parametri; se il comando esce con errore leggere gli Issue e correggere i PARAMETRI, mai modificare il JSON a mano; consegnare il file indicando dove salvarlo e come aprirlo. Con references/styles.md (stili disponibili e quando usarli) e references/examples.md (esempi di invocazione).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 skill/SKILL.md descrive il workflow in quattro passi e non contiene schema del formato né codice di generazione
- [ ] #2 skill/references/styles.md elenca gli stili disponibili e quando usarli
- [ ] #3 skill/references/examples.md contiene esempi concreti di invocazione del CLI
- [ ] #4 La skill istruisce esplicitamente a non modificare mai il JSON a mano e a correggere invece i parametri
- [ ] #5 Una richiesta in italiano tipo una cripta di otto stanze con poca luce produce una mappa valida
<!-- AC:END -->
