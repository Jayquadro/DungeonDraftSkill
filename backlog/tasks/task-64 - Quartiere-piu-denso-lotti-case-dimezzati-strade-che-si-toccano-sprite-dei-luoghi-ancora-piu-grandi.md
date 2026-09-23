---
id: TASK-64
title: >-
  Quartiere piu' denso: lotti case dimezzati, strade che si toccano, sprite dei
  luoghi ancora piu' grandi
status: Done
assignee:
  - '@claude'
created_date: '2026-09-23 06:49'
updated_date: '2026-09-23 09:04'
labels: []
dependencies:
  - TASK-63
ordinal: 65000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Jay ha aperto generated/city_quartiere_task63.dungeondraft_map in Dungeondraft, ha modificato a mano la locanda (scala 2.808->3.336, +19%, oggetto nm_locanda node e0) come riferimento di quanto vuole piu' grandi gli sprite dei luoghi, e ha segnalato quattro problemi sulla mappa quartiere (le altre due modifiche a mano su tempio/magazzino non sono arrivate nel file salvato, verificato con un confronto byte a byte prima/dopo - si procede solo col dato della locanda, confermato da Jay). (1) Molti buchi/spazio vuoto fra i lotti delle case ordinarie. (2) I lotti delle case semplici vanno dimezzati di dimensione, per riempire molto di piu' la mappa (piu' case, piu' piccole). (3) Le strade (i path disegnati da compose.add_path) non si toccano ne' si intersecano ai T/incroci: causa individuata, ScalePreset.street_path_fraction (quartiere=0.7) lascia un margine non pavimentato fra il bordo dell'isolato/lotto (dove finisce la strada di un ramo figlio della partizione ricorsiva) e il selciato vero e proprio della strada padre, che e' piu' stretto della fascia riservata (gap_width) e centrato al suo interno. (4) Le statue (LandmarkKind 'statua', piece_size=1.5 su tutti i preset) sono sproporzionate rispetto alle case ora piu' piccole, vanno ridotte. Ambito: SOLO preset 'quartiere', coerentemente con le richieste precedenti di Jay di non toccare 'citta' (TASK-63).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Le strade a preset quartiere si toccano/si intersecano ai punti di giunzione, verificato misurando che il selciato di un ramo figlio raggiunge il selciato del ramo padre senza margine vuoto in mezzo
- [x] #2 I lotti delle case ordinarie (non luoghi) a preset quartiere sono circa la meta' delle dimensioni attuali (larghezza e/o profondita'), misurato sulle mappe rigenerate
- [x] #3 La mappa quartiere e' visibilmente piu' densa: meno spazio vuoto fra i lotti, piu' edifici per isolato a parita' di canvas, misurato contando gli edifici su piu' seed
- [x] #4 Gli sprite dei luoghi chiusi coperti dal pacchetto a preset quartiere crescono di un ulteriore ~19%, coerente con la modifica di riferimento di Jay sulla locanda (nm_locanda, scala 2.808->3.336)
- [x] #5 Le statue a preset quartiere sono piu' piccole di oggi, senza cambiare la dimensione delle statue agli altri preset
- [x] #6 Il preset citta' non cambia rispetto a generated/city_citta_task63.dungeondraft_map, verificato byte a byte a parita' di seed
- [x] #7 Il preset isolato non cambia rispetto al comportamento di TASK-63 (non e' nello scope di questa richiesta)
- [x] #8 Le mappe di valutazione in generated/ per i tre preset sono rigenerate con seed fissi, nome che indica il task, e superano ddforge validate
- [x] #9 Suite di test completa verde, golden aggiornati dove il cambio li tocca
- [x] #10 Gate umano: Jay apre le mappe rigenerate in Dungeondraft e conferma il risultato
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. city.py: introdurre una variante quartiere-specifica dei parametri di ScalePreset (nuovo preset derivato o override mirato) invece di toccare SCALE_PRESETS['quartiere'] al volo: dimezzare (circa) target_lot_len, min_lot_len, building_depth_range, e ridurre in proporzione side_margin/setback_range cosi' i margini fissi non mangino la quota di lotto piu' piccolo; alzare street_path_fraction (0.7 -> vicino a 1.0, verificare l'effetto sulla serpeggiatura prima di fissare il valore finale) per far si' che il selciato riempia tutta la fascia riservata e tocchi/intersechi ai T invece di lasciare un margine vuoto centrato. Non toccare min_block/max_block se non necessario: verificare prima l'effetto sulla densita' con i soli parametri di lotto/edificio.
2. landmarks.py: dato che i luoghi a quartiere derivano la loro larghezza da kind.lots moltiplicato per lo stesso target_lot_len delle case, e il punto 1 lo dimezza, servira' quasi certamente alzare ulteriormente lots (o un fattore equivalente) per i 19 luoghi SITE_LOT/SITE_BAND coperti SOLO a quartiere, cosi' la loro dimensione assoluta non si dimezzi insieme alle case - verificare in process quanto serve per arrivare a +19% rispetto allo stato attuale di TASK-63 (misurato su locanda/nm_locanda) mantenendo isolato/citta' invariati (serve quindi un valore di lots preset-specifico, non piu' un unico numero su LandmarkKind: capire se aggiungere un meccanismo simile a compose._SPRITE_FILL_QUARTIERE ma sul lato geometria, o un moltiplicatore applicato solo quando scale=='quartiere' in city.py).
3. landmarks.py/compose.py: ridurre piece_size della statua SOLO a preset quartiere (nuovo meccanismo preset-aware analogo a _SPRITE_FILL_QUARTIERE, dato che oggi piece_size e' un unico valore su tutti gli _ALL_SCALES).
4. Verifica diretta in process: contare edifici/isolato prima-dopo su piu' seed (densita', AC3); misurare lo scarto fra selciato di un ramo figlio e quello del padre ai T (AC1); misurare la scala risultante dei 19 luoghi coperti vs TASK-63 (AC4, target ~1.19x); misurare la statua (AC5). Confermare citta' byte-identica (AC6) e isolato invariato (AC7).
5. Rigenerare golden e mappe di valutazione nei tre preset (seed 1337, canvas 78x78, naming _task64); ddforge validate; pytest -q sull'intera suite.
6. Verifica oggettiva (AC1-9), poi gate umano (AC10).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Strade che si toccano (AC1): SCALE_PRESETS['quartiere'].street_path_fraction portato da 0.7 a 1.0 in city.py. Causa isolata: il selciato (path_width = gap_width * street_path_fraction) era centrato dentro la fascia riservata (gap_width) e piu' stretto di lei, quindi la via di un ramo figlio della partizione ricorsiva (che finisce esattamente al bordo della fascia, tiling esatto senza spazio perso) non raggiungeva il selciato vero del ramo padre. A 1.0 il selciato riempie l'intera fascia: tocca sempre, si interseca dove due fasce si incrociano. Costo esplicito: niente piu' serpeggiamento a quartiere (room = (corridor.w - path_width)/2 = 0) - isolato e citta' invariati, mantengono la via serpeggiante. Aggiornato tests/test_generators_city.py::test_street_centerline_stays_inside_its_reserved_corridor per riflettere l'eccezione voluta invece di romperla silenziosamente: verificato su 6 seed che street.width == larghezza piena della fascia riservata a quartiere e swaying==0, mentre isolato/citta continuano a richiedere swaying>0.

Case dimezzate e mappa piu' densa (AC2/AC3): target_lot_len 3.0->1.5, min_lot_len 2.2->1.1 (esattamente meta'), side_margin 0.25->0.12 e setback_range (0.15,0.6)->(0.08,0.3) ridotti in proporzione (altrimenti un margine fisso pensato per lotti doppi avrebbe mangiato una fetta molto piu' grande dei lotti nuovi, vanificando la densita' in piu'). building_depth_range NON toccato di proposito: la profondita' e quindi il tetto di scala dei luoghi restano quelli di TASK-59/62/63, la crescita dei luoghi qui passa solo dal boost sotto, non dalla geometria. min_block/max_block invariati: piu' lotti piu' piccoli nello stesso isolato, non isolati piu' piccoli. Misurato in process su 10 seed (stesso seed, canvas 78x78, preset con e senza le modifiche via dataclasses.replace): edifici ordinari medi 146.0 -> 325.9 (+123%, quasi il doppio) - aggiornato anche tests/test_generators_city.py::test_citta_preset_has_many_more_buildings_than_quartiere (ex 'has_an_order_of_magnitude_more'), il cui margine 5x-20x assumeva la vecchia densita' di quartiere: il rapporto citta'/quartiere e' sceso da ~9.6x-10.8x a ~4.7x-5.1x (citta' invariata, e' quartiere che e' diventato molto piu' denso) - nuovo margine 3.5x-8.0x, rinominato per non promettere piu' 'un ordine di grandezza'.

Sprite dei luoghi ancora piu' grandi (AC4): invece di spingere ulteriormente LandmarkKind.lots (che avrebbe sbattuto di nuovo contro il tetto di profondita' del lotto, peggiorato dal dimezzamento dei lotti ordinari), replicato esattamente cio' che Jay ha fatto a mano sulla locanda: compose._SPRITE_SCALE_BOOST_QUARTIERE = 3.33594/2.80804 = 1.18800 (+18.8%), moltiplicatore diretto sulla scala finale dell'oggetto, applicato solo al luogo chiuso (non ai pezzi sparsi) e solo a preset quartiere. Puo' sconfinare leggermente nel margine attorno al lotto, come probabilmente fa gia' la locanda di Jay: accettato di proposito, e' il riferimento che ha scelto lui stesso.

Statua piu' piccola (AC5): compose._STATUA_PIECE_FACTOR_QUARTIERE = 0.6 applicato a landmark.piece_size solo per kind=='statua' e solo a quartiere (LandmarkKind.piece_size resta 1.5 su tutti i preset, invariato per isolato/citta').

Non-regressione (AC6/AC7): generated/city_isolato_task64.dungeondraft_map e city_citta_task64.dungeondraft_map verificati byte-per-byte identici a generated/city_{isolato,citta}_task63.dungeondraft_map (cmp) a parita' di seed: nessuna modifica involontaria fuori scope.

Mappe e suite (AC8/AC9): generated/city_{isolato,quartiere,citta}_task64.dungeondraft_map rigenerate (seed 1337, canvas 78x78). Tutte e tre superano ddforge validate. Golden invariati (city_seed_1337*.json testano solo il preset di default 'isolato', mai toccato qui - nessuna rigenerazione necessaria). Suite completa: 779 passed, 1 skipped, 1 fallimento transitorio non collegato (test_preview.py::test_cli_preview_without_pillow_prints_clear_message_not_traceback, PermissionError WinError 5 su CreateProcess sotto il carico della suite pesante) - riverificato passare da solo, non e' una regressione.

APERTO: AC10 (gate umano) - Jay deve aprire i tre file in Dungeondraft e confermare il risultato.

Gate umano confermato da Jay (2026-09-23): risultato sulla mappa quartiere (strade, densita', sprite, statue) approvato.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Quattro correzioni sulla mappa quartiere, isolato/citta' invariati (verificato byte-per-byte): (1) le strade ora si toccano e si intersecano sempre ai T/incroci (street_path_fraction 0.7->1.0, il selciato riempie l'intera fascia riservata invece di restarne staccato; costo: niente piu' serpeggiamento a quartiere); (2) i lotti delle case ordinarie dimezzati in larghezza (target_lot_len/min_lot_len) con margini ridotti in proporzione, mappa piu' densa (+123% edifici medi su 10 seed, 146->326); (3) gli sprite dei luoghi crescono di un ulteriore +18.8%, calcato esattamente sulla modifica che Jay ha fatto a mano sulla locanda nel file di TASK-63, applicato come moltiplicatore diretto sulla scala invece di spingere la geometria del lotto oltre il suo tetto di profondita'; (4) la statua e' piu' piccola a quartiere (fattore 0.6) per restare proporzionata alle case ora piu' piccole. Due test aggiornati per riflettere le scelte intenzionali (niente piu' serpeggiamento a quartiere; il rapporto citta'/quartiere non e' piu' 'un ordine di grandezza' ma resta 'molti di piu''). Verificato con: suite completa (779 passed, 1 skipped, 1 fallimento ambientale non collegato riverificato passare da solo), le tre mappe generated/city_*_task64 validate senza errori, cmp byte-a-byte per isolato/citta' contro TASK-63. In attesa del gate umano di Jay (AC10).
<!-- SECTION:FINAL_SUMMARY:END -->
