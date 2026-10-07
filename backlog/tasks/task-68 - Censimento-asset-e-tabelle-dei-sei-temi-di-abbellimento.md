---
id: TASK-68
title: Censimento asset e tabelle dei sei temi di abbellimento
status: Done
assignee: []
created_date: '2026-10-04 17:30'
updated_date: '2026-10-07 06:09'
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
- [x] #1 Un documento elenca, per ciascuno dei sei temi, gli asset trovati nel catalogo (alias, pack, dimensione nativa, classe decal/ingombro) e quelli mancanti
- [x] #2 L'elenco degli asset mancanti e stato sottoposto a Jay e la sua decisione per ciascuno (farne a meno o nuovi sprite) e registrata nel documento
- [x] #3 Le nuove chiavi semantiche necessarie sono aggiunte al catalogo con il meccanismo esistente, senza toccare il formato delle chiavi gia usate
- [x] #4 `decorate/themes.py` definisce i sei temi per tutti e 5 i tipi di mappa, con un default per i ruoli non elencati
- [x] #5 Un test verifica che ogni chiave citata dai temi risolva su una texture del catalogo
- [x] #6 Un test verifica che ogni texture risolta appartenga a un pack presente nel manifest del template di produzione
- [x] #7 I colori di luce e ambient sono ARGB a 8 cifre (test)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Leggere i 52 .dungeondraft_pack reali (non solo il catalogo attuale, che contiene solo gli oggetti piazzati nei template) per un censimento vero. 2. Confermare con Jay se rigenerare il catalogo con l'intera libreria o solo i pack specializzati (deciso: tutto). 3. Rigenerare data/assets.json con ddforge catalog --pack sui 52 pack unici, verificando che la suite di test resti verde. 4. Scrivere decorate/themes.py: sei temi x cinque tipi di mappa, con ruolo _default per ognuno. 5. Scrivere tests/test_decorate_themes.py per AC5/6/7. 6. Documentare il censimento in un documento Backlog con le categorie trovate/mancanti e sottoporlo a Jay (AC1/AC2).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Censimento fatto leggendo i 52 .dungeondraft_pack reali via assets.read_dungeondraft_pack (21.086 texture totali), non solo il catalogo preesistente. Nessuna categoria richiesta dai sei temi risulta scoperta: ragnatele, sangue, ossa, candele, catene, macerie, mobili rotti, funghi, radici, carretti, bancarelle, banchi alchemici, alambicchi, cristalli, cerchi rituali, pergamene, stendardi, fiori, strumenti musicali hanno tutte almeno una famiglia di asset dedicata (soprattutto in WFW 5th Anniversary Free Megapack e [DQ] 2Y Anniversary Pack, gia nel manifest). Catalogo rigenerato (data/assets.json: 92KB/573 oggetti -> 2.7MB/12.741 oggetti) con ddforge catalog --from (entrambi i template) --from-catalog data/assets.json --pack (52 pack unici) --out data/assets.json; decisione di Jay (chat) di importare tutto, non solo i pack specializzati. Suite completa verificata verde dopo la rigenerazione (798 passed, 1 skipped). Scritto src/ddforge/decorate/themes.py (sei temi x cinque tipi di mappa, ruolo _default per ognuno) e tests/test_decorate_themes.py (8 test: default sempre presente, ogni chiave risolve sul catalogo, ogni texture appartiene a un pack nel manifest, colori ARGB a 8 cifre, fallback su ruolo sconosciuto, classi decal/ingombro valide, LightRule mai con parametri a zero). Documento backlog/docs/doc-1 scritto con il censimento completo per tema e la conclusione 'nessun asset mancante'. AC2 resta aperto: serve la conferma di Jay sul documento, non essendoci voci da decidere caso per caso non c'e' altro da aspettare se non il suo ok esplicito.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Censimento completato leggendo i 52 .dungeondraft_pack reali (21.086 texture), non solo il catalogo preesistente: nessuna categoria dei sei temi risulta scoperta. Catalogo data/assets.json rigenerato (92KB/573 oggetti -> 2,7MB/12.741 oggetti) con ddforge catalog --pack sui 52 pack unici, decisione di Jay di importare tutto. decorate/themes.py scritto (sei temi x cinque tipi di mappa, ruolo _default per ognuno), verificato da tests/test_decorate_themes.py (8 test: ogni chiave risolve sul catalogo, ogni texture appartiene a un pack nel manifest, colori ARGB a 8 cifre). Documento backlog/docs/doc-1 con il censimento per tema, confermato sufficiente da Jay in chat il 2026-10-07 (AC2). Suite completa verificata verde dopo la rigenerazione del catalogo.
<!-- SECTION:FINAL_SUMMARY:END -->
