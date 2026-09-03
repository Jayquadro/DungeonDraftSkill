---
id: TASK-3
title: Derivare e documentare lo schema di lights e texts dal template ricco
status: To Do
assignee: []
created_date: '2026-09-03 11:25'
labels: []
milestone: m-0
dependencies:
  - TASK-2
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Lo schema di `lights` e `texts` NON e stato verificato nell'analisi che ha prodotto SPEC.md: nessuna delle mappe pubbliche analizzate ne conteneva (SPEC.md §3, §13). Va derivato leggendo il template ricco, campo per campo, e documentato in docs/format.md insieme al resto del formato verificato. Senza questo, add_light e add_text di build.py non sono implementabili: non inventare i campi.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 docs/format.md contiene lo schema completo di un elemento di level.lights: nome, tipo e valore osservato di ogni campo
- [ ] #2 docs/format.md contiene lo schema completo di un elemento di level.texts, incluso come e codificato il contenuto testuale e il font
- [ ] #3 Per ogni campo e indicato se e stato osservato direttamente nel template ricco o solo ipotizzato
- [ ] #4 docs/format.md riporta anche lo schema verificato degli altri elementi (wall, portal, pattern, object, path, roof) come riferimento unico del progetto
- [ ] #5 Se il template ricco non contiene luci o testi, il task si ferma e chiede a Jay un nuovo export invece di ipotizzare i campi
<!-- AC:END -->
