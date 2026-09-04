---
id: TASK-41
title: Preset di scala selezionabili per le mappe cittadine (quartiere/città)
status: To Do
assignee: []
created_date: '2026-09-04 07:24'
labels: []
milestone: m-8
dependencies:
  - TASK-34
  - TASK-35
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 41000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A 256 px/quadretto un quartiere giocabile è già enorme, una città intera diventa ingestibile (SPEC.md §9.4). TASK-34 aveva lasciato la decisione sospesa a un parametro --scale con due regimi possibili; la decisione presa è: supportare entrambi i regimi come preset selezionabili invece di scegliere un solo regime fisso.

Il generatore cittadino (generators/city.py, TASK-35) deve poter produrre due tipi di mappa a seconda del preset scelto:
- preset "quartiere": scala giocabile a 5 ft/quadretto, con il livello di dettaglio attuale (edifici singoli, lotti, strade, piazze) pensato per essere usato al tavolo.
- preset "città": scala di regione a 1 quadretto = 1 edificio, pensata per rappresentare un'intera città o quartiere esteso mantenendo dimensioni di file gestibili.

Il lavoro deve chiudere anche la parte di misurazione e documentazione lasciata aperta da TASK-34 (dimensioni file e tempi di apertura nei due regimi).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Un parametro di scala (es. --scale) permette di scegliere tra il preset "quartiere" e il preset "città" al momento della generazione
- [ ] #2 Il preset "quartiere" produce una mappa a 5 ft/quadretto con il livello di dettaglio giocabile attuale (edifici, lotti, strade, piazze)
- [ ] #3 Il preset "città" produce una mappa a 1 edificio/quadretto pensata per un'intera città o quartiere esteso
- [ ] #4 Le dimensioni in byte e i tempi di apertura risultanti nei due preset su un caso reale sono misurati e documentati
- [ ] #5 La differenza tra i due preset e come sceglierli è documentata nel README e nella skill
- [ ] #6 Il documento generato in entrambi i preset passa validate() senza errori
<!-- AC:END -->
