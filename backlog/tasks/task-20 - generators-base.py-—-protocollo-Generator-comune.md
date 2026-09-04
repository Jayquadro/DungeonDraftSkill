---
id: TASK-20
title: generators/base.py — protocollo Generator comune
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:32'
updated_date: '2026-09-04 06:30'
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
- [x] #1 Il Protocol Generator è definito e i generatori successivi lo rispettano
- [x] #2 Ogni generatore istanzia il proprio RNG dal seed passato e non usa mai il modulo random globale
- [x] #3 Lo stesso seed con gli stessi parametri produce un Blueprint identico
- [x] #4 Esiste un test che verifica la riproducibilità del seed
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Definire il Protocol Generator con generate(*, width, height, seed, **params) -> Blueprint. Scrivere un generatore fittizio (usato solo nel test) che istanzia random.Random(seed) e produce un Blueprint con una stanza a dimensione/posizione pseudo-casuale derivata dal seed, per dimostrare concretamente il pattern che i generatori reali (TASK-21+) dovranno seguire. Test: stesso seed -> Blueprint identico (confronto campo per campo); seed diverso -> Blueprint diverso; verificare che il generatore fittizio non tocchi mai il modulo random globale (import random; random.seed fisso esterno, poi chiamare il generatore, poi verificare che una chiamata successiva a random.random() non sia stata alterata in modo prevedibile — o piu semplicemente, ispezionare che il generatore usi solo un'istanza locale).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Il Protocol Generator era gia definito correttamente nello stub di TASK-1. Scritto un generatore fittizio (_FakeGenerator, solo nei test) che istanzia random.Random(seed) locale e produce un Blueprint con una stanza pseudo-casuale, a dimostrazione concreta del pattern richiesto ai generatori reali (TASK-21+). 4 test: conformita al protocollo, stesso seed -> Blueprint identico (confronto per uguaglianza dataclass, non solo campo per campo), seed diverso -> risultato diverso, e un test che alterando deliberatamente lo stato di random globale prima/dopo la chiamata dimostra che il risultato resta identico (prova che il generatore non dipende dal modulo random globale). Suite completa: 203 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Protocol Generator confermato/documentato. Generatore fittizio dimostra e verifica il pattern random.Random(seed) locale richiesto ai generatori reali: 4 test, incluso uno che alterando lo stato random globale conferma l'indipendenza del risultato. Suite completa: 203 test verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
