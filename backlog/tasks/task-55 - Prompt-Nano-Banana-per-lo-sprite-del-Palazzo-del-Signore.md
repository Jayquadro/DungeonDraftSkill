---
id: TASK-55
title: Prompt Nano Banana per lo sprite del Palazzo del Signore
status: Done
assignee:
  - '@claude'
created_date: '2026-09-18 08:19'
updated_date: '2026-09-18 08:43'
labels: []
dependencies: []
references:
  - prompt/01-ospedale.md
documentation:
  - docs/sprite-luoghi.md
ordinal: 56000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Il luogo 'palazzo' (Palazzo del Signore) e' gia' un LandmarkKind in src/ddforge/generators/landmarks.py e ha una misura reale in docs/sprite-luoghi.md sez.3 (monumento C1, 1024x1024 px), ma non e' mai stato commissionato per il pacchetto Nova Mistralis: oggi usa ancora il ripiego bb_keepsandcastles_castle_color (docs/sprite-luoghi.md sez.10, TASK-52). Jay vuole una scheda prompt pronta da incollare in Gemini Nano Banana per generare lo sprite dedicato, con lo stesso formato delle 25 schede gia' in prompt/ (TASK-49: prompt/01-ospedale.md come riferimento di struttura).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Esiste una nuova scheda in prompt/ (numerata in continuita' con le 25 esistenti, kebab-case) per nm_palazzo.png
- [x] #2 La scheda ha la stessa struttura delle altre: tabella di intestazione (nome file, categoria, canvas, scala, regola del rosso, dove finisce), sezione Come usarlo, prompt canonico autosufficiente, varianti B e C, sezione Dopo la generazione, checklist finale
- [x] #3 Canvas e categoria sono quelli gia' misurati per il palazzo in docs/sprite-luoghi.md sez.3 (monumento, 1024x1024), non una nuova proposta
- [x] #4 Il SUBJECT descrive una residenza fortificata con corte interna, distinta da un castello isolato (nota gia' in docs/sprite-luoghi.md: 'residenza fortificata con corte interna, non un castello isolato')
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Verificare in docs/sprite-luoghi.md sez.3 la misura del palazzo (monumento C1, 1024x1024, corte interna) e in assets.py il ripiego attuale (bb_keepsandcastles_castle_color).
2. Scrivere prompt/26-palazzo.md seguendo la struttura di prompt/01-ospedale.md e prompt/03-accademia.md (C1, rosso: nessun rosso saturo come gli altri monumenti gia' fatti): tabella, Come usarlo, prompt canonico, varianti B/C, Dopo la generazione, checklist.
3. SUBJECT: residenza fortificata con corte interna abitata (loggia, finestre), non un castello isolato di campagna (niente fossato/ponte levatoio), per AC4.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Creato prompt/26-palazzo.md (numerazione in continuita' dopo 25-bordello.md). Struttura identica a prompt/03-accademia.md e prompt/14-monastero.md (uniche altre schede C1 esistenti): tabella con canvas 1024x1024 e categoria C1 presi da docs/sprite-luoghi.md sez.3 senza modificarli, rosso 'nessun rosso saturo' come gli altri monumenti (il catalogo segna C1 come rosso:libero). SUBJECT descrive corte interna rettangolare con ala residenziale (finestre a bifora, loggia coperta) dentro mura merlate con torri d'angolo, esplicitamente 'not an isolated country castle: no moat, no drawbridge' per AC4. Nessun codice toccato, nessun impatto su test/golden.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Scheda prompt/26-palazzo.md creata per nm_palazzo.png, stessa struttura delle 25 schede esistenti (C1, 1024x1024 da docs/sprite-luoghi.md sez.3), SUBJECT che distingue la residenza fortificata con corte interna da un castello isolato di campagna.
<!-- SECTION:FINAL_SUMMARY:END -->
