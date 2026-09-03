---
id: TASK-24
title: 'CLI: comando `ddforge generate` con validazione obbligatoria pre-scrittura'
status: To Do
assignee: []
created_date: '2026-09-03 11:32'
labels: []
milestone: m-3
dependencies:
  - TASK-21
  - TASK-13
  - TASK-23
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Comando di generazione descritto in SPEC.md §8: ddforge generate <style> --template --out --width --height --rooms --seed --style --lights --furnish. Stili: dungeon, building, cave, city (i generatori arrivano nelle milestone successive; qui basta che dungeon funzioni e gli altri siano registrati). Comportamento obbligatorio: generate esegue validate sul risultato PRIMA di scrivere il file; se ci sono errori non scrive nulla ed esce con codice 1 stampando gli Issue, mentre un warning stampa ma non blocca.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ddforge generate dungeon --template ... --out ... --rooms 8 --seed 1337 produce un file valido
- [ ] #2 In presenza di errori di validazione il file di output NON viene scritto e il comando esce con codice 1 stampando gli Issue
- [ ] #3 I warning sono stampati ma non bloccano la scrittura
- [ ] #4 --seed rende la generazione riproducibile: due esecuzioni con gli stessi parametri producono file identici a meno di creation_date
- [ ] #5 --furnish accetta none, light, medium, heavy e --lights attiva le luci
- [ ] #6 Il comando è coperto da test end-to-end sulla fixture 8x8
<!-- AC:END -->
