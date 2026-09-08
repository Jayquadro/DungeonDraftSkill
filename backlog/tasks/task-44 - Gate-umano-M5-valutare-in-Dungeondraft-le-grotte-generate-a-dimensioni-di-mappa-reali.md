---
id: TASK-44
title: >-
  Gate umano M5: valutare in Dungeondraft le grotte generate a dimensioni di
  mappa reali
status: Done
assignee: []
created_date: '2026-09-07 13:01'
updated_date: '2026-09-08 12:19'
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
- [x] #1 Almeno una grotta e' stata generata con `ddforge generate cave` alle dimensioni di mappa che verranno usate in produzione (non la scala ridotta dello spike) e aperta in Dungeondraft da Jay
- [x] #2 Il giudizio di Jay sul risultato (accettabile cosi' com'e', oppure servono altri parametri) e' registrato nel task
- [x] #3 Se il risultato non e' accettabile, i parametri da rivedere in generators/cave.py (min_component_size, tunnel_width, fill_prob, iterations) e il criterio di scala proposto sono documentati, cosi' un eventuale task di follow-up puo' partire da li' senza rifare l'analisi
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verdetto finale di Jay (2026-09-08, dopo 5 round di gate su TASK-36): 'ok, ora il file va bene'. Il file valutato e' generated/cave_m5.dungeondraft_map (80x80, seed 1337), rigenerato piu volte durante il gate con parametri finali fill_prob=0.45, open_radius=4, min_component_size=240 sotto-celle (15 quadretti), grand_radius=3/grand_count=2 (almeno 2 camere garantite di 150+ quadretti). Storia completa dei 5 round e delle correzioni in TASK-36 (implementation notes + commenti).
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-08 08:58
---
Verdetto di Jay (dal gate umano di TASK-36, generated/cave_m5.dungeondraft_map, 80x80 seed 1337): NON accettabile cosi' com'e'. "La cave è molto sparsa. Le mappe delle caverne perché siano utili devono comunque essere delle sorte di 'stanze', anche irregolari, collegate tra di loro."

Diagnosi coerente con quanto gia' annotato in TASK-32: a fill_prob=0.45/iterations=5/B5-S4 la componente principale sopravvive come un'unica area scavata molto estesa e sfrangiata, non un insieme di camere separate. Il problema non e' solo la soglia dei tunnel (min_component_size) ma la forma stessa della componente principale: serve un algoritmo/parametrizzazione che produca camere distinte (separate da roccia) collegate da tunnel stretti, non un'unica area aperta sprawling.

Verra' ripreso in TASK-36 (dipendenza di fatto, stesso gate).
---

author: @claude
created: 2026-09-08 09:13
---
AC3 chiuso: parametri rivisti in generators/cave.py (TASK-36, round 1 del gate) — fill_prob 0.45->0.57, min_component_size 16->128 sotto-celle (1->8 quadretti), e _dig_tunnels riscritto per collegare TUTTE le camere sopra soglia con un albero di copertura minimo invece che solo verso la componente principale. Criterio di scala: soglia ASSOLUTA in quadretti (non una frazione dell'area mappa), valida perche a fill_prob=0.57 il CA si frammenta sempre in decine di camere indipendentemente dalla dimensione della griglia (verificato su 24x18 e 80x80) — non serve piu far scalare la soglia con l'area, perche non sopravvive piu una componente dominante che la renderebbe inutile.

File rigenerato in generated/cave_m5.dungeondraft_map, in attesa dello stesso verdetto di Jay richiesto su TASK-36 (stesso file, stessa domanda). Chiudo qui quando arriva la conferma.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
La grotta generata a dimensioni di mappa di produzione (80x80) e' stata valutata da Jay in Dungeondraft attraverso 5 round di gate (dettagli in TASK-36): sprawling → camere strette → camere piccole rispetto ai tunnel → poca varieta' di taglia → mancanza di caverne davvero grandi. Ogni round ha prodotto una correzione misurabile in generators/cave.py (fill_prob, apertura morfologica per isolare camere larghe, poi camere "grand" garantite) con test di regressione dedicati in tests/test_cave_gate.py.

Parametri finali approvati: fill_prob=0.45, open_radius=4, min_component_size=240 sotto-celle (15 quadretti, soglia assoluta indipendente dalla scala mappa), grand_radius=3/grand_count=2 (almeno 2 camere di 150+ quadretti garantite). Nessuna soglia scalata sull'area mappa: la combinazione fill_prob/apertura morfologica frammenta il CA in decine di camere indipendentemente dalla dimensione della griglia, risolvendo il problema originale (soglia fissa che non scalava) alla radice.

Verdetto di Jay: "ok, ora il file va bene".
<!-- SECTION:FINAL_SUMMARY:END -->
