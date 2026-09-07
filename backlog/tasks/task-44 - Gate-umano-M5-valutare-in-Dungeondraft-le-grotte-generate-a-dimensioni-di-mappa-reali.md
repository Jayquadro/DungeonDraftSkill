---
id: TASK-44
title: >-
  Gate umano M5: valutare in Dungeondraft le grotte generate a dimensioni di
  mappa reali
status: To Do
assignee: []
created_date: '2026-09-07 13:01'
labels: []
milestone: m-5
dependencies:
  - TASK-32
documentation:
  - docs/SPEC.md
ordinal: 44000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TASK-32 ha implementato generators/cave.py: cellular automata a risoluzione sotto-cella, scritto nel layer cave nativo di Dungeondraft (decision-1). L'algoritmo (fill_prob=0.45, 5 iterazioni B5/S4, soglia fissa di 16 sotto-celle per decidere se scavare un tunnel verso una componente secondaria invece di scartarla) e' lo stesso gia approvato visivamente da Jay nello spike TASK-31, ma solo a una scala di mappa piccola (36x26 quadretti).

Alle dimensioni piu' grandi che verranno usate davvero (es. 80x80, il default di molti template), la soglia fissa fa si' che quasi ogni componente aperta superi la soglia e riceva un tunnel: il risultato e' una copertura scavata molto estesa (gran parte della mappa), un comportamento atteso dell'algoritmo classico a questi parametri ma mai giudicato visivamente in Dungeondraft a questa scala.

Serve un giudizio umano di Jay, che ha Dungeondraft installato e puo' aprire i file generati: la grotta generata alle dimensioni di mappa reali e' visivamente accettabile cosi' com'e', o servono parametri diversi (es. una soglia che scali con l'area della mappa, un fill_prob piu' alto, meno iterazioni di smoothing)?
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Almeno una grotta e' stata generata con `ddforge generate cave` alle dimensioni di mappa che verranno usate in produzione (non la scala ridotta dello spike) e aperta in Dungeondraft da Jay
- [ ] #2 Il giudizio di Jay sul risultato (accettabile cosi' com'e', oppure servono altri parametri) e' registrato nel task
- [ ] #3 Se il risultato non e' accettabile, i parametri da rivedere in generators/cave.py (min_component_size, tunnel_width, fill_prob, iterations) e il criterio di scala proposto sono documentati, cosi' un eventuale task di follow-up puo' partire da li' senza rifare l'analisi
<!-- AC:END -->
