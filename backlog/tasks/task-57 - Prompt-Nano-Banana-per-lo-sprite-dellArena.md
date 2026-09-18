---
id: TASK-57
title: Prompt Nano Banana per lo sprite dell'Arena
status: Done
assignee:
  - '@claude'
created_date: '2026-09-18 08:20'
updated_date: '2026-09-18 08:43'
labels: []
dependencies: []
references:
  - prompt/01-ospedale.md
documentation:
  - docs/sprite-luoghi.md
ordinal: 58000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Il luogo 'arena' e' gia' un LandmarkKind in src/ddforge/generators/landmarks.py (ammesso solo al preset citta) e ha una misura reale in docs/sprite-luoghi.md sez.3 (monumento C1, 1024x1024 px, anfiteatro ellittico con gradinate), ma non e' mai stato commissionato per il pacchetto Nova Mistralis: oggi usa ancora il ripiego tourney_grounds (docs/sprite-luoghi.md sez.10, TASK-52). Jay vuole una scheda prompt pronta da incollare in Gemini Nano Banana per generare lo sprite dedicato, con lo stesso formato delle schede gia' in prompt/ (TASK-49: prompt/01-ospedale.md come riferimento di struttura).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Esiste una nuova scheda in prompt/ (numerata in continuita' con le esistenti, kebab-case) per nm_arena.png
- [x] #2 La scheda ha la stessa struttura delle altre: tabella di intestazione (nome file, categoria, canvas, scala, regola del rosso, dove finisce), sezione Come usarlo, prompt canonico autosufficiente, varianti B e C, sezione Dopo la generazione, checklist finale
- [x] #3 Canvas e categoria sono quelli gia' misurati per l'arena in docs/sprite-luoghi.md sez.3 (monumento, 1024x1024), non una nuova proposta
- [x] #4 Il SUBJECT descrive un anfiteatro ellittico con gradinate visto dall'alto, coerente con la nota gia' in docs/sprite-luoghi.md
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Verificare in docs/sprite-luoghi.md sez.3 la misura dell'arena (monumento C1, 1024x1024, solo preset citta, anfiteatro ellittico con gradinate) e in assets.py il ripiego attuale (tourney_grounds).
2. Scrivere prompt/27-arena.md seguendo la stessa struttura delle altre schede C1 (accademia/monastero): tabella, Come usarlo, prompt canonico, varianti B/C, Dopo la generazione, checklist.
3. SUBJECT: anfiteatro ellittico con gradinate concentriche viste dall'alto, distinto dal teatro (pianta semicircolare, categoria C2) per AC4.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Creato prompt/27-arena.md (numerazione in continuita' dopo 26-palazzo.md). Struttura identica alle altre schede C1 (accademia/monastero/palazzo): tabella con canvas 1024x1024 e categoria C1 presi da docs/sprite-luoghi.md sez.3, nota esplicita che l'arena e' ammessa solo al preset citta (a differenza degli altri monumenti). SUBJECT descrive un anfiteatro ellittico con gradinate concentriche in pietra vero e proprio, non un campo da torneo temporaneo (niente tende/steccati), esplicitamente distinto dal teatro (pianta semicircolare, categoria C2) per AC4. Nessun codice toccato, nessun impatto su test/golden.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Scheda prompt/27-arena.md creata per nm_arena.png, stessa struttura delle schede esistenti (C1, 1024x1024 da docs/sprite-luoghi.md sez.3), SUBJECT con anfiteatro ellittico a gradinate distinto dal teatro.
<!-- SECTION:FINAL_SUMMARY:END -->
