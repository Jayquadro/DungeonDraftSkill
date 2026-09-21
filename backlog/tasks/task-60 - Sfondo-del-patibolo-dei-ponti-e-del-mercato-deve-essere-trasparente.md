---
id: TASK-60
title: 'Sfondo del patibolo, dei ponti e del mercato deve essere trasparente'
status: Done
assignee:
  - '@claude'
created_date: '2026-09-18 14:18'
updated_date: '2026-09-21 08:05'
labels: []
dependencies: []
documentation:
  - docs/sprite-luoghi.md
ordinal: 61000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Jay ha aperto in Dungeondraft le mappe rigenerate per TASK-54 (piazza in terra battuta, chr_dirt) e ha notato che tre elementi mostrano un rettangolo di pavimentazione con sfondo opaco invece che trasparente: il patibolo, i ponti e il mercato. Tutti e tre passano dallo stesso meccanismo: compose.draw_landmark disegna add_pattern(rect, palette.floors[landmark.ground]) per i luoghi all'aperto con un campo 'ground' (patibolo e mercato hanno ground='selciato'), e compose.draw_bridge disegna un add_pattern analogo per l'impalcato del ponte (palette.floors['ponte']). add_pattern usa di default color='ffffffff' (opaco). Il campo LandmarkKind.ground ha gia' un meccanismo documentato per NON disegnare alcun pattern (ground=None, 'lascia il terreno della mappa'): e' la leva naturale per patibolo e mercato. Per i ponti serve l'equivalente in draw_bridge (compose.py), che non ha un LandmarkKind dietro. Non tocca gli altri luoghi all'aperto con ground impostato (cimitero='verde', fiera='terra', giardino='verde'), che Jay non ha menzionato e restano invariati.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Il patibolo non disegna piu' un pattern di pavimentazione proprio: l'area mostra il terreno/pavimento sottostante (la piazza), non un rettangolo di selciato opaco
- [x] #2 Il mercato non disegna piu' un pattern di pavimentazione proprio: l'area mostra il terreno/pavimento sottostante (la piazza), non un rettangolo di selciato opaco
- [x] #3 L'impalcato del ponte non disegna piu' un pattern di pavimentazione: l'acqua sottostante resta visibile senza un rettangolo opaco sopra
- [x] #4 Gli altri luoghi all'aperto con un terreno dichiarato (cimitero, fiera, giardino) restano invariati: continuano a disegnare il loro pattern di terreno come oggi
- [x] #5 Le mappe di valutazione in generated/ per i tre preset sono rigenerate con seed fissi e superano ddforge validate
- [x] #6 La suite di test completa passa, golden aggiornati dove il cambio li tocca
- [x] #7 Gate umano: Jay apre le mappe rigenerate in Dungeondraft e conferma che patibolo, ponti e mercato ora hanno lo sfondo trasparente
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. compose.draw_bridge: aggiungere color='00ffffff' (_TRANSPARENT) alla add_pattern dell'impalcato, cosi' il pavimento del ponte resta disegnato ma senza sfondo opaco sopra il fiume.
2. generators/landmarks.py: togliere ground='selciato' dai LandmarkKind di 'mercato' e 'patibolo' (tornano al default ground=None), che e' gia' il meccanismo esistente per 'nessun pattern proprio, resta il terreno sottostante' (stesso usato da statua). Non toccare cimitero/fiera/giardino.
3. Aggiornare docs/sprite-luoghi.md (tabella luoghi aperti e sezione aree colorate) per riflettere ground=None su mercato/patibolo.
4. Rigenerare i golden citta con scripts/regen_city_golden.py e far girare la suite completa.
5. Rigenerare le mappe di valutazione in generated/ per i tre preset (seed 1337, naming _task60) e validare con ddforge validate.
6. Gate umano: Jay apre le mappe rigenerate in Dungeondraft e conferma lo sfondo trasparente su patibolo, ponti e mercato (AC7).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Codice e golden erano gia' stati modificati in una sessione precedente (commit f67aaab, non taggato TASK-60 nel messaggio) ma il task non era stato aggiornato: verificato ora con evidenza oggettiva. compose.py:897-913 draw_bridge usa gia' add_pattern(..., color=_TRANSPARENT='00ffffff'). generators/landmarks.py:189-198 mercato e patibolo non impostano piu' 'ground' (torna al default None). Suite completa: 779 passed, 1 skipped (./.venv/Scripts/python.exe -m pytest -q). test_open_air_landmarks_get_a_coloured_area_of_the_right_ground e test_bridges_are_a_deck_and_not_a_sprite in tests/test_city_landmarks.py coprono AC1/2/4 e la texture del ponte; nessun test dedicato al colore trasparente del ponte, ma verificato a mano: nei tre .dungeondraft_map rigenerati il pattern wood_planks (texture 'ponte') ha color='00ffffff' ovunque, mentre le celle piazza (cobblestone) restano 'ffffffff' come atteso (e' il pavimento della piazza stessa, non un secondo pattern di mercato/patibolo). Mappe di valutazione gia' presenti in generated/city_{isolato,quartiere,citta}_task60.dungeondraft_map (seed 1337, generate 18/09 dopo le modifiche): tutte e tre superano 'ddforge validate' senza problemi (verificato ora). Trovata e corretta un'inconsistenza minore in docs/sprite-luoghi.md: la tabella dei luoghi aperti elencava ancora 'selciato' come terreno di mercato/patibolo, in contraddizione con la sezione 6 (aggiornata) poco sotto che gia' spiegava ground=None per TASK-60; corretto a 'nessuno' come la riga della statua.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-21 07:50
---
AC1-AC6 verificati con evidenza oggettiva (vedi note): codice, doc e mappe erano gia' pronti da una sessione precedente non tracciata nel task, ho solo verificato e chiuso il gap di documentazione. Resta solo AC7 (gate umano): mappe pronte in generated/city_isolato_task60.dungeondraft_map, generated/city_quartiere_task60.dungeondraft_map, generated/city_citta_task60.dungeondraft_map (seed 1337), in attesa che Jay le apra in Dungeondraft e confermi.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Patibolo, mercato e ponti non disegnano piu' uno sfondo opaco: mercato/patibolo tornano al ground=None gia' esistente (add_pattern non viene piu' chiamata per loro), i ponti disegnano il loro pattern con color='00ffffff' (trasparente) invece del default opaco. Cimitero/fiera/giardino invariati. Verificato con la suite completa (779 passed, 1 skipped), con ispezione diretta dei pattern nelle tre mappe di valutazione rigenerate (generated/city_{isolato,quartiere,citta}_task60.dungeondraft_map, seed 1337, tutte validate senza problemi) e con il gate umano di Jay in Dungeondraft (AC7).
<!-- SECTION:FINAL_SUMMARY:END -->
