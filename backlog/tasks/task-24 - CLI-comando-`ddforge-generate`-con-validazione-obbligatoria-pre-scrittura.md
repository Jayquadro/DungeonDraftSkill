---
id: TASK-24
title: 'CLI: comando `ddforge generate` con validazione obbligatoria pre-scrittura'
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:32'
updated_date: '2026-09-04 07:13'
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
- [x] #1 ddforge generate dungeon --template ... --out ... --rooms 8 --seed 1337 produce un file valido
- [x] #2 In presenza di errori di validazione il file di output NON viene scritto e il comando esce con codice 1 stampando gli Issue
- [x] #3 I warning sono stampati ma non bloccano la scrittura
- [x] #4 --seed rende la generazione riproducibile: due esecuzioni con gli stessi parametri producono file identici a meno di creation_date
- [x] #5 --furnish accetta none, light, medium, heavy e --lights attiva le luci
- [x] #6 Il comando è coperto da test end-to-end sulla fixture 8x8
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Aggiungere render_blueprint(level, ids, blueprint, palette) in compose.py: disegna ogni Room via draw_room (le porte sono gia decise dal generatore in Room.doors) e ogni corridoio come canale aperto (_draw_corridor_channel, orientamento da rect.w>=rect.h come documentato in bsp.py). Implementare _cmd_generate in cli.py: carica il template (TemplateError -> messaggio pulito), verifica lo stile richiesto contro un registro {'dungeon': bsp} (altri stili -> errore esplicito 'non ancora implementato', non un crash), genera il Blueprint, prepara il documento, carica il catalogo e la palette (fallback allo stile 'dungeon' se --style non passato), disegna con render_blueprint, arreda con furnish se --furnish != none (rng da random.Random(seed)), aggiunge luci se --lights (al centro di ogni stanza e al centro dei corridoi lunghi, blueprint.long_corridor_indices), finalize, poi valida SEMPRE prima di scrivere: se ci sono errori stampa gli Issue ed esce 1 senza scrivere il file; altrimenti scrive e stampa gli eventuali warning senza bloccare. Test end-to-end via subprocess sulla fixture 8x8: file valido, determinismo dello stesso seed, blocco su validazione fallita (fixture apposita), avvisi non bloccanti, stili non implementati gestiti con messaggio pulito.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Aggiunta render_blueprint(level, ids, blueprint, palette) in compose.py: disegna ogni Room via draw_room (le porte sono gia decise dal generatore) e ogni corridoio come canale aperto. Implementato _cmd_generate in cli.py con un registro {'dungeon': bsp} per gli stili (altri stili -> errore esplicito 'non ancora implementato', mai un crash). --lights aggiunge una luce al centro di ogni stanza e al centro di ogni corridoio lungo (blueprint.long_corridor_indices, coerente con SPEC.md §9.1). validate() gira SEMPRE prima di save(): errori bloccano la scrittura, warning no. Testato manualmente prima dei test formali con la fixture 8x8 (blocca correttamente: la fixture non ha texts_vis, DDF003 atteso) e col template reale blank_80x80 (scrive con successo, 2 warning DDF102 non bloccanti). Investigati i 2 warning: sono due segmenti di canale-corridoio che si toccano in una piega a L senza mai avere una porta (il canale non ne ha bisogno per essere attraversabile) — limite noto e gia atteso dell'euristica DDF102, non un bug del generatore; documentato nel docstring di _check_ddf102_unreachable_rooms. 9 test end-to-end via subprocess in tests/test_cli_generate.py: file valido, blocco su errore (fixture 8x8, exit 1, file non scritto), warning non bloccanti, determinismo del seed, seed diverso -> output diverso, furnish aumenta gli oggetti, lights aggiunge luci, stile non implementato e template mancante gestiti con messaggio pulito. Suite completa: 253 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementato ddforge generate dungeon: carica template, genera Blueprint via bsp, disegna con render_blueprint, arreda con furnish, aggiunge luci con --lights, valida sempre prima di scrivere (errori bloccano, warning no). 9 test end-to-end via subprocess, incluso un warning DDF102 investigato e spiegato (limite noto su corridoi a L, non un bug). Suite completa: 253 test verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
