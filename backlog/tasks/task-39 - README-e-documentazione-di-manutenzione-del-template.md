---
id: TASK-39
title: README e documentazione di manutenzione del template
status: To Do
assignee: []
created_date: '2026-09-03 11:35'
labels: []
milestone: m-7
dependencies:
  - TASK-37
documentation:
  - docs/SPEC.md
priority: medium
type: docs
ordinal: 39000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Requisito esplicito della definizione di fatto (SPEC.md §15): il README deve spiegare come esportare un nuovo template quando Dungeondraft aggiorna il formato. È la procedura che tiene in vita il progetto negli anni, perché tutta l'architettura dipende dal template (SPEC.md §2). Vanno documentati anche installazione, uso del CLI, e le trappole di §14.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Il README spiega installazione, uso dei comandi generate, validate, inspect, catalog e preview
- [ ] #2 Il README contiene la procedura passo-passo per esportare un nuovo template da Dungeondraft quando il formato cambia
- [ ] #3 Il README rimanda a docs/format.md per lo schema e riassume le trappole di SPEC.md §14
- [ ] #4 docs/format.md è aggiornato con tutto ciò che è stato calibrato nei gate umani di M1 e M3
<!-- AC:END -->
