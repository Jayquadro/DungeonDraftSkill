---
id: TASK-68
title: Censimento asset e tabelle dei sei temi di abbellimento
status: To Do
assignee: []
created_date: '2026-10-04 17:30'
updated_date: '2026-10-04 17:43'
labels: []
milestone: m-10
dependencies: []
references:
  - data/assets.json
  - src/ddforge/assets.py
  - src/ddforge/compose.py
documentation:
  - docs/SPEC-decorate.md
  - docs/format.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
I temi di `ddforge decorate` (abbandonato, abitato, lugubre, naturale, arcano, festivo — docs/SPEC-decorate.md §6.2) sono tabelle dati che per ogni tipo di mappa × ruolo di zona elencano pavimenti, muri, pennellate di terreno, pool di oggetti con peso/modo di piazzamento/classe (decal o ingombro), regole di luce e ambient_light. Possono usare SOLO chiavi gia presenti in `data/assets.json` e pack gia nel manifest del template: nessun path inventato, nessun pack aggiunto.

Prima va censito cosa c'e davvero fra i 52 pack e 573 oggetti per i bisogni dei temi (ragnatele, sangue, ossa, candele, catene, macerie, mobili rotti, tappeti, funghi, radici, alberi, carretti, bancarelle; per arcano banchi alchemici, alambicchi, cristalli, cerchi rituali, pergamene; per festivo tavolate, stendardi, fiori, strumenti musicali...), con dimensioni native da `object_sizes`. Jay si aspetta che ci sia quasi tutto: cio che manca va elencato e portato a Jay, che decide voce per voce se il tema ne fa a meno o se servono nuovi sprite (pipeline di M9). Le tabelle dei temi si chiudono solo dopo la sua decisione.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Un documento elenca, per ciascuno dei sei temi, gli asset trovati nel catalogo (alias, pack, dimensione nativa, classe decal/ingombro) e quelli mancanti
- [ ] #2 L'elenco degli asset mancanti e stato sottoposto a Jay e la sua decisione per ciascuno (farne a meno o nuovi sprite) e registrata nel documento
- [ ] #3 Le nuove chiavi semantiche necessarie sono aggiunte al catalogo con il meccanismo esistente, senza toccare il formato delle chiavi gia usate
- [ ] #4 `decorate/themes.py` definisce i sei temi per tutti e 5 i tipi di mappa, con un default per i ruoli non elencati
- [ ] #5 Un test verifica che ogni chiave citata dai temi risolva su una texture del catalogo
- [ ] #6 Un test verifica che ogni texture risolta appartenga a un pack presente nel manifest del template di produzione
- [ ] #7 I colori di luce e ambient sono ARGB a 8 cifre (test)
<!-- AC:END -->
