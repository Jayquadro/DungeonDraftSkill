---
id: TASK-58
title: Prompt Nano Banana per lo sprite della Cattedrale
status: Done
assignee:
  - '@claude'
created_date: '2026-09-18 08:20'
updated_date: '2026-09-18 08:44'
labels: []
dependencies: []
references:
  - prompt/01-ospedale.md
documentation:
  - docs/sprite-luoghi.md
ordinal: 59000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Il luogo 'cattedrale' e' gia' un LandmarkKind in src/ddforge/generators/landmarks.py e ha una misura reale in docs/sprite-luoghi.md sez.3 (monumento C1, 1024x1024 px, navata/transetto/abside, il monumento religioso piu' grande della citta'), ma non e' mai stato commissionato per il pacchetto Nova Mistralis: oggi usa ancora il ripiego bb_keepsandcastles_cathedral_color (docs/sprite-luoghi.md sez.10, TASK-52). Jay vuole una scheda prompt pronta da incollare in Gemini Nano Banana per generare lo sprite dedicato, con lo stesso formato delle schede gia' in prompt/ (TASK-49: prompt/01-ospedale.md come riferimento di struttura).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Esiste una nuova scheda in prompt/ (numerata in continuita' con le esistenti, kebab-case) per nm_cattedrale.png
- [x] #2 La scheda ha la stessa struttura delle altre: tabella di intestazione (nome file, categoria, canvas, scala, regola del rosso, dove finisce), sezione Come usarlo, prompt canonico autosufficiente, varianti B e C, sezione Dopo la generazione, checklist finale
- [x] #3 Canvas e categoria sono quelli gia' misurati per la cattedrale in docs/sprite-luoghi.md sez.3 (monumento, 1024x1024), non una nuova proposta
- [x] #4 Il SUBJECT descrive navata, transetto e abside, e la rende riconoscibile come il monumento religioso piu' grande della citta' (deve distinguersi dal tempio per dimensione e forma, gia' nota in docs/sprite-luoghi.md)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Verificare in docs/sprite-luoghi.md sez.3 la misura della cattedrale (monumento C1, 1024x1024, navata/transetto/abside, il piu' grande monumento religioso) e in assets.py il ripiego attuale (bb_keepsandcastles_cathedral_color).
2. Scrivere prompt/28-cattedrale.md seguendo la stessa struttura delle altre schede C1: tabella, Come usarlo, prompt canonico, varianti B/C, Dopo la generazione, checklist.
3. SUBJECT: pianta cruciforme con navata, transetto e abside, chiaramente piu' grande e articolata del tempio (chiesa a navata unica, C2), per AC4.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Creato prompt/28-cattedrale.md (numerazione in continuita' dopo 27-arena.md). Struttura identica alle altre schede C1: tabella con canvas 1024x1024 e categoria C1 presi da docs/sprite-luoghi.md sez.3, rosso 'nessun rosso saturo' come gli altri monumenti. SUBJECT descrive pianta cruciforme (navata, transetto, abside, torre di crociera, due torri gemelle in facciata, contrafforti) esplicitamente 'far larger and more elaborate than a simple parish church', per distinguerla dal tempio (chiesa a navata unica, C2) per AC4. Nessun codice toccato, nessun impatto su test/golden.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Scheda prompt/28-cattedrale.md creata per nm_cattedrale.png, stessa struttura delle schede esistenti (C1, 1024x1024 da docs/sprite-luoghi.md sez.3), SUBJECT con pianta a navata/transetto/abside distinta dal tempio per dimensione e forma.
<!-- SECTION:FINAL_SUMMARY:END -->
