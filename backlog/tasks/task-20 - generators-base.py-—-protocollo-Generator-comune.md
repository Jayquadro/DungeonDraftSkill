---
id: TASK-20
title: generators/base.py — protocollo Generator comune
status: To Do
assignee: []
created_date: '2026-09-03 11:32'
labels: []
milestone: m-3
dependencies:
  - TASK-9
documentation:
  - docs/SPEC.md
priority: medium
type: feature
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Protocollo condiviso da tutti i generatori (SPEC.md §9): generate(width, height, seed, params) restituisce un Blueprint. Serve a garantire che i generatori delle milestone M3-M5 siano intercambiabili dal CLI e dai test, e che ogni generazione sia riproducibile a partire dal seed: lo stesso seed con gli stessi parametri produce byte identici, escluso creation_date. È un requisito di testabilità, non un vezzo (SPEC.md §8).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Il Protocol Generator è definito e i generatori successivi lo rispettano
- [ ] #2 Ogni generatore istanzia il proprio RNG dal seed passato e non usa mai il modulo random globale
- [ ] #3 Lo stesso seed con gli stessi parametri produce un Blueprint identico
- [ ] #4 Esiste un test che verifica la riproducibilità del seed
<!-- AC:END -->
