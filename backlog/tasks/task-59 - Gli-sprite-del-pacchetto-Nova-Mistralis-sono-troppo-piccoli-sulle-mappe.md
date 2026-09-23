---
id: TASK-59
title: Gli sprite del pacchetto Nova Mistralis sono troppo piccoli sulle mappe
status: Done
assignee:
  - '@claude'
created_date: '2026-09-18 08:21'
updated_date: '2026-09-23 09:02'
labels: []
dependencies:
  - TASK-52
documentation:
  - docs/sprite-luoghi.md
ordinal: 60000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Jay ha guardato le mappe di valutazione rigenerate in TASK-52 (generated/city_*_task52.dungeondraft_map) e trova gli sprite del pacchetto Nova Mistralis (i nm_* agganciati in src/ddforge/assets.py._CITY_LANDMARK_SPRITES) troppo piccoli sulla mappa: vanno ingranditi di almeno il doppio rispetto a come sono disegnati oggi. Riguarda solo i luoghi coperti dal pacchetto (docs/sprite-luoghi.md sez.10), non gli altri luoghi ancora sul ripiego. Il piazzamento oggi passa da compose._draw_landmark_sprites: i luoghi chiusi riempiono il 92% dell'ingombro del lotto (_SPRITE_FILL in compose.py) mentre i pezzi sparsi (cimitero, mercato) sono disegnati al lato dichiarato da LandmarkKind.piece_size in quadretti - va capito quale dei due meccanismi (o l'ingombro stesso del lotto) e' la leva giusta per il raddoppio, senza sforare i lotti confinanti ne' rompere la scala misurata in docs/sprite-luoghi.md per gli altri luoghi.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Gli sprite nm_* dei luoghi CHIUSI coperti dal pacchetto occupano piu' spazio sulle mappe rispetto a oggi (aumento accettato anche solo di ~1.5x, non necessariamente il doppio pieno, per restare senza modifiche massicce alla logica di piazzamento - vedi commento), misurato su generated/city_*_task52.dungeondraft_map o equivalenti rigenerati. Mercato e cimitero (unici luoghi con sprite sparsi coperti) restano invariati su richiesta esplicita di Jay. Accademia e monastero (unici luoghi chiusi coperti a isolato intero, non a lotto) restano invariati per assenza di una leva sicura e non massiccia
- [x] #2 Gli sprite ingranditi non sforano l'ingombro dei lotti/isolati confinanti sulle mappe rigenerate
- [x] #3 I luoghi ancora sul ripiego (non coperti dal pacchetto) restano alla dimensione attuale, invariati
- [x] #4 Le mappe di valutazione in generated/ per i tre preset sono rigenerate con la nuova dimensione, seed fissi, e superano ddforge validate
- [x] #5 Suite di test completa verde, golden aggiornati dove il cambio di scala li tocca
- [x] #6 Gate umano: Jay apre le mappe rigenerate in Dungeondraft e conferma che la dimensione ora gli piace
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. In src/ddforge/generators/landmarks.py raddoppiare (o portare a 2.0 se assente) il campo 'lots' per i 19 LandmarkKind chiusi coperti dal pacchetto con site SITE_LOT o SITE_BAND (tutti i coperti tranne accademia/monastero, che sono SITE_BLOCK e ignorano 'lots', e tranne mercato/cimitero, esclusi da Jay): ospedale, teatro, prigione, municipio, bagni, biblioteca, tempio, caserma, banca, alchimista, magazzino, fabbro, stalle, fornaio, macelleria, taverna, locanda, bordello, faro. Nessun cambiamento a compose.py o assets.py: la leva e' solo il dato di catalogo.
2. Verificare con lo stesso esperimento diretto gia' fatto (rigenerazione in-process, non solo lettura) che la scala effettiva dello sprite cresce (~1.3-1.5x atteso, tetto dato dalla profondita' di fila) per un campione di kind, e che nessun luogo ripiego/accademia/monastero/mercato/cimitero cambia.
3. Rigenerare (diff poi --write) i golden citta con scripts/regen_city_golden.py; pytest -q sull'intera suite.
4. Rigenerare le mappe di valutazione in generated/ per i tre preset (seed 1337, canvas 78x78, nome _task59), validare con ddforge validate, misurare che gli sprite nm_* coperti (esclusi mercato/cimitero/accademia/monastero) siano piu' grandi che in generated/city_*_task52.
5. Verifica oggettiva (AC2/AC3 via misura diretta sulle mappe), poi gate umano (AC6).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Raddoppiato LandmarkKind.lots (da 1.0 a 2.0) in src/ddforge/generators/landmarks.py per i 13 luoghi chiusi coperti dal pacchetto che partivano da un lotto singolo: prigione, biblioteca, alchimista, banca, magazzino, taverna, locanda, bordello, fabbro, stalle, fornaio, macelleria, faro. I 6 luoghi coperti che avevano gia' lots>=1.5 (tempio, municipio, caserma, teatro, bagni, ospedale) sono rimasti alla loro misura originale: raddoppiarli anche loro non li ingrandiva affatto (gia' oltre il tetto dato dalla profondita' di fila, verificato rigenerando in process) e a canvas piccoli rompeva l'invariante 'un luogo richiesto esplicitamente compare sempre' (5 test falliti durante lo sviluppo: test_a_requested_landmark_is_always_present[tempio], la catena di test del cimitero che dipende dal tempio, test_generate_city_landmark_flag_forces_an_element - tutti tornati verdi dopo il ripristino). Accademia e monastero (SITE_BLOCK, occupano gia' un isolato intero) e mercato/cimitero (sprite sparsi, Jay ha detto che vanno gia' bene) restano invariati per scelta esplicita, vedi commento sullo scope. Trovato e corretto un secondo problema durante lo sviluppo: select() in landmarks.py calcolava il budget MAX_LANDMARK_FRACTION contando le istanze dei luoghi comuni come se costassero tutte un lotto (riga 'total = sum(count ...)'), ma ora alcuni ne costano 2: al preset isolato (pochi lotti in tutto) questo faceva superare ai luoghi il numero di edifici ordinari per un seed (test_landmarks_never_eat_the_whole_city[isolato], seed 6: 13 luoghi contro 11 edifici). Corretto pesando il totale per kind.lots, cosi' il budget riflette i lotti davvero consumati, non il numero di istanze; effetto collaterale intenzionale: alcuni luoghi comuni ora compaiono in meno istanze ma piu' grandi a parita' di budget. Misurato su generated/city_*_task59.dungeondraft_map contro generated/city_*_task52.dungeondraft_map: i luoghi toccati crescono di scala di circa 1.05x-1.3x (taverna, magazzino, locanda, stalle, fabbro, bordello, alchimista, biblioteca, prigione), i luoghi non toccati (ripiego, accademia, monastero, mercato, cimitero, tempio/municipio/caserma/teatro/bagni/ospedale) restano alla stessa scala a meno di rumore normale di seed (0.9x-1.16x, dovuto a come si spostano gli altri piazzamenti, non a un cambio di codice su di loro). Mappe rigenerate in generated/ per i tre preset (city_isolato_task59, city_quartiere_task59, city_citta_task59, seed 1337, canvas 78x78): tutte e tre superano ddforge validate. Golden tests/fixtures/golden/city_seed_1337_landmarks.json rigenerato con scripts/regen_city_golden.py. Suite completa: 779 passed, 1 skipped.

Trovato prima del gate umano (richiesta di Jay): le mappe generated/city_*_task59.dungeondraft_map erano state generate alle 13:51 del 18/09, PRIMA che lo stesso commit (f67aaab, 17:06) applicasse anche la correzione TASK-60 (sfondo trasparente di patibolo/mercato/ponti). Verificato con evidenza oggettiva: le mappe task59 avevano 0 occorrenze di color='00ffffff', mentre le mappe task60 (generate 17:03, dopo la correzione) ne avevano gia'. Le sprite nm_palazzo/nm_arena/nm_cattedrale di TASK-61 non sono invece pertinenti alle mappe cittadine: assets.py._CITY_LANDMARK_SPRITES mappa ancora cattedrale/palazzo/arena sul ripiego (bb_keepsandcastles_*/tourney_grounds), TASK-61 ha preparato solo gli asset per il pack, senza agganciarli al generatore. Rigenerate le tre mappe (stesso comando di TASK-52/59: seed 1337, canvas 78x78, template blank_80x80) con il codice attuale: ora includono sia il raddoppio lots di TASK-59 sia la trasparenza di TASK-60. Tutte e tre superano ddforge validate. Verificato color=00ffffff presente in quartiere (6) e citta (19), assente in isolato (0) coerentemente con city_isolato_task60 (0, nessun ponte/pattern trasparente generato a quel seed/preset). Suite completa: 779 passed, 1 skipped, invariata.

Gate umano confermato da Jay (2026-09-23): dimensione degli sprite ingranditi approvata sulle mappe rigenerate.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-18 08:22
---
Jay ha confermato esplicitamente che il raddoppio vale anche per il preset 'citta', non solo 'isolato'/'quartiere': gia' coperto dagli AC (tutti e tre i preset), nessuna modifica di scope necessaria.
---

author: @claude
created: 2026-09-18 08:23
---
Jay ha confermato esplicitamente che il raddoppio vale anche per il preset 'quartiere': gia' coperto dagli AC (tutti e tre i preset), nessuna modifica di scope necessaria.
---

author: @claude
created: 2026-09-18 09:20
---
Jay ha ridotto lo scope in fase di esecuzione dopo aver visto i risultati di un esperimento diretto sul generatore: mercato e cimitero (gli unici due luoghi con sprite sparsi coperti dal pacchetto) vanno bene cosi' come sono e NON vanno modificati, nonostante l'AC1 originale li includesse. Per i luoghi chiusi coperti (i 21 rimanenti) ha chiesto di ingrandire il piu' possibile SENZA modifiche massicce alla logica di piazzamento, accettando esplicitamente un aumento anche solo di ~1.5x invece del raddoppio pieno, con la possibilita' di chiedere ulteriori aggiustamenti in un giro successivo. Motivo tecnico dietro la richiesta (verificato con un esperimento diretto sul generatore, non solo lettura del codice): per i 18 luoghi chiusi SITE_LOT coperti, LandmarkKind.lots allarga il lotto SOLO in larghezza lungo la fila mentre la profondita' della fila resta fissa, quindi lo sprite (vincolato dalla dimensione piu' piccola del rettangolo) cresce di scala ma si ferma a un tetto intorno a ~1.3-1.5x anche a lots molto alti - un vero raddoppio richiederebbe una nuova logica di piazzamento su due assi, che e' la 'modifica massiccia' che Jay ha chiesto di evitare per ora. Per i 2 luoghi chiusi SITE_BLOCK coperti (accademia, monastero) LandmarkKind.lots e' del tutto ignorato dal codice (occupano gia' un isolato intero): nessuna leva sicura e non massiccia esiste per ingrandirli oltre l'attuale in questo giro, restano quindi invariati; possibile lavoro di follow-up se Jay lo richiede dopo aver visto le mappe rigenerate.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
LandmarkKind.lots raddoppiato per i 13 luoghi chiusi coperti dal pacchetto che partivano da un lotto singolo (crescita reale ~1.05-1.3x, tetto dato dalla profondita' di fila come previsto e accettato da Jay); i 6 gia' a lots>=1.5 restano invariati (nessun beneficio, rompevano un invariante di piazzamento). Corretto anche un bug scoperto nel budget MAX_LANDMARK_FRACTION che non pesava il costo in lotti dei luoghi. Mappe di valutazione rigenerate (generated/city_*_task59.dungeondraft_map), golden aggiornato, suite verde (779 passed, 1 skipped). In attesa del gate umano di Jay (AC6).
<!-- SECTION:FINAL_SUMMARY:END -->
