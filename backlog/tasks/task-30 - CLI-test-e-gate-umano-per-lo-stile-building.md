---
id: TASK-30
title: 'CLI, test e gate umano per lo stile building'
status: Done
assignee: []
created_date: '2026-09-03 11:34'
updated_date: '2026-09-07 09:12'
labels: []
milestone: m-4
dependencies:
  - TASK-29
  - TASK-24
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Chiusura di M4 (SPEC.md §5): il comando ddforge generate building deve produrre un edificio multi-piano con tetti che Jay apre correttamente in Dungeondraft. Include test di integrazione e golden file come per il BSP.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 ddforge generate building genera un edificio multi-piano con tetto, validato prima della scrittura
- [x] #2 Il CLI espone i parametri specifici dell'edificio, inclusa la tipologia e il numero di piani
- [x] #3 Esistono test di integrazione e un golden file per un seed fisso
- [x] #4 Jay apre il file in Dungeondraft e conferma che i piani, le scale e il tetto sono corretti
- [x] #5 Ogni difetto segnalato da Jay è riprodotto in un test prima della correzione
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. cli.py: registrare building in _load_generators; aggiungere --building-type
   e --l-shaped; ramificare _cmd_generate per il caso multi-piano (draw_building
   + furnish_building + _add_building_lighting invece di render_blueprint/furnish
   a singolo livello); style di default = building_type quando --style e assente.
2. compose.py: rooms_by_level/floor_blueprint/furnish_building, riusabili sia
   da cli.py che dai test (furnish() resta a singolo livello, TASK-23 invariato).
3. Estendere _STYLE_DEFINITIONS/palette_for (assets.py) con roof/wall_load_bearing
   per tavern/manor/warehouse: senza, draw_building non disegnava mai il tetto
   ne differenziava i muri portanti dai tramezzi (nessuna delle due cose e mai
   stata popolata da TASK-17 in poi).
4. Test: integrazione+golden file per building.generate (come TASK-25 per bsp),
   test end-to-end del CLI (multi-piano, tetto, arredo/luci per piano corretti,
   riproducibilita).
5. Generare un file demo reale e chiedere a Jay di aprirlo (gate umano AC4/5).

6. Gate umano round 1 fallito: correzioni decise con Jay (arredo addossato ai muri, vano scale dentro il perimetro con porta e oggetto scala). Ogni difetto va riprodotto in test prima della correzione (AC5), in tests/test_building_gate.py.
7. Etichette dei livelli (difetti 1 e 5): cli._cmd_generate passa 'labels' a template.prepare, che gia le supporta. Nomi per piano dell'edificio (Piano terra / Primo piano / ...); il dungeon a un livello resta invariato.
8. Vano scale (difetto 4): building.generate lo colloca dentro il perimetro portante effettivo (oggi e fuori perche draw_building deriva il perimetro dal bounding box delle stanze, non dal footprint dichiarato); porta verso la stanza adiacente su ogni piano; oggetto scala visibile dal catalogo (stairs_round_04/08); stessa posizione su ogni piano.
9. Arredo (difetti 2, 3, 6): sostituire la densita per-quadretto senza tetto con ricette per kind, con disposizione (contro il muro / al centro / attorno a un tavolo) e conteggi limitati. Gli oggetti addossati vanno ruotati parallelamente al muro. Nota: l'orientamento 'verso l'interno' dello sprite non e verificabile da qui, va confermato da Jay al prossimo gate.
10. Rigenerare generated/building_m4.dungeondraft_map e rifare il gate.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
CLI: 'ddforge generate building --building-type {tavern,manor,warehouse} [--l-shaped]' funzionante end-to-end (draw_building + furnish per piano + luci per piano, verificato con AC1-2). Bug trovati e corretti durante l'integrazione (nessuno di questi era coperto da test prima, tutti riprodotti in test prima della correzione, coerente con AC5):
- generators/building.py: c'era un margine di 1 quadretto fra il vano scale e l'area stanze, mai riempito da pavimento ne muri -> striscia vuota visibile dentro il perimetro portante. Rimosso (stairs_rect e generation_footprint ora esattamente adiacenti, Rect.overlaps con margin=0 conferma nessuna sovrapposizione).
- assets.py: palette_for non popolava mai roof/wall_load_bearing per nessuno stile (campi esistenti da TASK-27 ma mai valorizzati da TASK-17): draw_building quindi non disegnava MAI il tetto ne differenziava i muri portanti. Aggiunti a _STYLE_DEFINITIONS per tavern/manor/warehouse (roof='tiles', wall_load_bearing=stone/stone_09, uniche texture disponibili nel catalogo osservato).

Limite noto e non bloccante: 'ddforge generate building' produce 3 avvisi DDF102 non bloccanti (perimetro portante e vano scale del piano superiore senza porta propria). Stesso limite gia documentato per il dungeon (TASK-26): il validatore non distingue "muro esterno raggiungibile solo dall'interno" da "stanza davvero isolata". Segnalato esplicitamente a Jay nella richiesta di gate, non nascosto.

Test: tests/test_cli_generate_building.py (7), tests/test_building_integration.py (3, incluso golden file tests/fixtures/golden/building_tavern_seed_1337.json). Aggiornato anche un test preesistente in test_cli_generate.py che assumeva 'building' non ancora implementato (ora testa 'cave' per lo stesso scopo). Suite completa: 303/303 verdi.

File demo generato: generated/building_m4.dungeondraft_map (tavern, seed 1337, furnish medium, luci attive; rigenerabile con 'ddforge generate building --template templates/blank_80x80.dungeondraft_map --out generated/building_m4.dungeondraft_map --width 40 --height 40 --seed 1337 --building-type tavern --furnish medium --lights').

Rigenerato generated/building_m4.dungeondraft_map dopo le correzioni di TASK-26 (routing corridoi/orientamento canali/riproiezione porte in bsp.py, riusate da generators/building.py via _connect_rooms e plan_corridor). Nessuna modifica di comportamento attesa per building: le stanze di un edificio si collegano quasi sempre per adiacenza diretta (_shared_wall_segment), il percorso a corridoio di bsp._connect_rooms cambiato in TASK-26 e usato solo per i pochi collegamenti non adiacenti. Verificato: stessa validazione di prima (3 avvisi DDF102 non bloccanti, invariati), suite building (test_building_integration.py, test_draw_building.py, test_cli_generate_building.py) tutta verde nella suite completa di 315 test.

Gate umano: Jay ha aperto generated/building_m4.dungeondraft_map e il risultato NON e utilizzabile. Difetti segnalati: (1) i due livelli si chiamano entrambi 'Ground'; (2) una stanza piena di botti e camini e una piena di botti; (3) non si capisce la divisione delle stanze; (4) non si capisce quale sia il vano scale; (5) il tetto e su un layer che si chiama comunque Ground; (6) non ci sono arredi se non barili e camini.

Diagnosi (misurata sul codice e sul file, prima di correggere):
- Etichette: cli._cmd_generate chiama template.prepare(doc, levels=N) senza mai passare 'labels', che prepare supporta gia. Tutti i livelli ereditano quindi la label del template ('Ground'). Spiega i difetti 1 e 5.
- Densita arredo: _DENSITY_PER_TILE['medium']=0.12 e applicata all'intera area della stanza senza tetto massimo. Conteggi reali per seed 1337: sala_comune 544 quadretti -> 65 oggetti, cucina 306 -> 37, retro 234 -> 28, camera 640 -> 77, camera 168 -> 20, camera 216 -> 26. Totale 253 oggetti su un edificio 40x40. Le stanze sono letteralmente tappezzate: spiega i difetti 2 e 3 (i muri non si vedono sotto l'arredo).
- Varieta arredo: _KIND_ACCENT_HINTS['retro'] = ('crate','barrel') ma la palette tavern non ha 'crate' -> la stanza retro riceve SOLO barili. Stesso effetto per 'cucina' ('oven','crate','barrel' -> solo oven+barrel) e 'camera' ('bed' -> solo letti, 77 in una stanza). Spiega il difetto 6.
- Vano scale: building.generate mette stairs_rect a (1,1)-(3,3), ma compose.draw_building disegna il perimetro portante sul bounding box delle STANZE, che per seed 1337 e (3,2)-(38,38). Il vano scale finisce quindi FUORI dal perimetro, adiacente solo per l'angolo, senza porte e senza collegamento a nessuna stanza. Non contiene inoltre nessun oggetto scala (il catalogo ha stairs_round_04 e stairs_round_08, mai usati). Spiega il difetto 4, ed e anche una delle 3 DDF102 gia note.

Gate umano M4 round 1 — correzioni applicate (tutte riprodotte prima in tests/test_building_gate.py, 8 test, AC5).

Difetti 1 e 5 (etichette dei piani): cli._cmd_generate passa ora 'labels' a template.prepare, prese da building.floor_labels() ('Piano terra' / 'Primo piano' / ...). Il piano col tetto e riconoscibile come l'ultimo.

Difetto 4 (vano scale): _stairwell_rect e ora una fascia a tutta altezza sul lato sinistro del footprint, non un angolo. Scelta deliberata: il resto del footprint resta UN rettangolo, che le stanze tassellano esattamente. Ritagliando un angolo restava sempre una scheggia (la sala comune veniva 2x36) oppure si spezzava in due il piano terra del magazzino, che SPEC.md 9.2 vuole a volume unico. Il vano scale ha pavimento, muri, una porta verso la stanza piu grande adiacente su ogni piano, e un oggetto scala visibile al centro (nuovo campo Palette.stairs -> stairs_round_04/08, mai usati prima).

Difetti 2, 3 e 6 (arredo): _DENSITY_PER_TILE rimossa. L'arredo va ora per ricetta: ogni accent del kind ha una quota propria (_ACCENT_QUOTA: quadretti-per-pezzo + tetto massimo) e una disposizione propria (_ACCENT_PLACEMENT: addossato al muro / al centro / attorno all'ultimo pezzo centrale). Gli oggetti addossati sono ruotati parallelamente al muro. 'density' resta un moltiplicatore (_DENSITY_SCALE). Estesi anche _KIND_ACCENT_HINTS e le palette (tavern: crate/keg/cupboard; warehouse: cupboard), che erano la causa del 'solo barili'. Conteggi per seed 1337: taverna 35+19 oggetti su 8 texture diverse invece di 253 su 2-3.

Difetto 3 (divisione delle stanze), seconda causa trovata durante la correzione e non segnalata da Jay: _generate_room_rects usava _inscribe_room (giusto per un dungeon scavato, sbagliato per un edificio), quindi le stanze galleggiavano a distanze casuali. Ora le foglie del BSP diventano le stanze senza margine e i tramezzi sono condivisi.

Difetto trovato dopo, sul file generato: due muri sovrapposti dove quello sopra e cieco tappano la porta di quello sotto. Con le stanze che tassellano il footprint, il perimetro portante e i lati esterni delle stanze erano lo stesso segmento disegnato due volte, e l'ingresso della taverna piu la porta del vano scale risultavano murati. Corretto: ogni segmento del perimetro e disegnato una volta sola dal muro portante, le stanze saltano quel lato (draw_room(skip_sides=...)) e le loro porte vengono riportate sul muro portante; il vano scale e trattato come un ambiente (compose._stairwell_room) con le porte delle stanze adiacenti rispecchiate. Muri per piano nella taverna: da 20 a 12. Regola documentata in docs/format.md 9.7.

Golden file rigenerati dopo diff verificato a mano: bsp_seed_1337.json (solo objects, 320 -> 65, geometria identica) e building_tavern_seed_1337.json (label dei piani, tassellatura esatta, 8 segmenti ridondanti in meno per piano, portale d'ingresso spostato sul muro portante). Il generatore del golden building passa ora anche le labels, come il CLI.

Suite completa: 323/323 verdi. Avvisi DDF102 scesi da 3 a 1 per la taverna (perimetro del piano superiore senza porta propria: corretto architettonicamente, falso positivo noto del validatore, gia documentato in format.md 9.5).

File per il gate round 2: generated/building_m4.dungeondraft_map (taverna), piu building_m4_manor e building_m4_warehouse per verificare le altre due tipologie.

Gate umano M4 round 2 — difetti 7-13, tutti riprodotti prima in tests/test_building_gate.py (sezione ROUND 2) come chiede l'AC5.

Difetti 7, 10 e 13 (rotazione): 'i camini sono girati', 'l'armadio a sinistra e girato', 'molti degli sprite guardano il muro'. _wall_slot dava rotazione 0 sia al lato alto sia al basso e pi/2 sia al destro sia al sinistro, quindi meta dell'arredo finiva con la faccia contro il muro. Regola nuova: rotazione = lato * pi/2 (top 0, right pi/2, bottom pi, left 3pi/2), cioe faccia sempre verso l'interno. Non e una congettura: Jay ha corretto a mano i camini della cucina dentro il file e le sue coordinate sono il campione che fissa la formula (muro basso a y=21, camino da rot=0 a rot=+-pi).

Difetto 8 (compenetrazione): 'alcuni sprite, come i camini, e necessario che siano compenetrati coi muri. Ugualmente le madie'. _WALL_OFFSET passa da 1.0 a 0.5 quadretti: uno sprite 1x1 tocca il muro esatto, uno 2x2 ci entra per meta. Stessa misura di Jay (camino a y=20.5, muro a y=21).

Difetti 7, 9 e 12 (sovrapposizione): 'due camini parzialmente sovrapposti', 'due botti sovrapposte', 'nella magione al piano terra gli sprite sono tutti sovrapposti'. _furnish_room piazzava ogni pezzo senza sapere nulla dei precedenti. Introdotti _texture_size (ingombro letto dal nome file quando c'e — Oven_..._2x2, Keg_..._1x1 — altrimenti da tabella semantica) e _is_free (due pezzi non piu vicini della semisomma degli ingombri), con una lista  condivisa fra tutte le stanze del piano e inizializzata da cio che draw_building ha gia messo (la scala). Unica esenzione: la sedia attorno al suo tavolo. Corretto anche _around_slot, che con i % 4 e un'ancora sola rimetteva la quinta sedia sulla prima: sul file del round 1 c'erano quattro coppie di sedie nella stessa identica posizione. Verificato sui tre file: 0 sovrapposizioni.

Difetto 11 (dimensioni): 'le stanze sono molto molto grandi, un quadretto dovrebbe essere 1.5m reali'. Due cause distinte. (a) _generate_room_rects chiedeva a _build_tree tante stanze quanti i kind del piano, e _build_tree si ferma appena le raggiunge: 3 foglie su 34x38 quadretti danno stanze da 51x27 METRI. Ora rooms_target e irraggiungibile di proposito e a fermare i tagli e _can_split, cioe la DIMENSIONE (max 12 m di lato, _MAX_ROOM_SIDE_M). I kind diventano un repertorio che cicla sulle stanze ottenute, ordinate per area decrescente cosi la sala comune e davvero la stanza piu grande. (b) l'ingombro stesso: 40x40 quadretti sono 60x60 m. Aggiunto _DEFAULT_SIZE per tipologia (taverna 24x18 m, magione 30x24, magazzino 30x18) e il CLI lo usa quando --width/--height non sono passate. Risultato per seed 1337: taverna 4 stanze al piano terra + 6 camere, magazzino a volume unico, nessuna stanza oltre 10.5 m di lato.

Effetti collaterali corretti nello stesso giro: _STAIRS_MIN_SIDE da 4 a 2 quadretti (un vano scale da 6 m mangiava un quarto di taverna); _connect_floor_rooms preferisce le coppie ADIACENTI a parita di distanza, altrimenti con stanze piccole Prim collegava coppie non adiacenti e _connect_rooms scavava corridoi dentro le altre stanze (ora: 0 corridoi in tutti e tre gli edifici); _ACCENT_QUOTA ritarata sulle stanze vere (le quote di prima, 90-250 quadretti per pezzo, valevano per stanze da 600 e su una stanza da 30 davano un pezzo per tipo); il moltiplicatore di kind e passato dall'area alla scala, altrimenti col tetto per pezzo la stanza del boss e lo sgabuzzino ricevevano lo stesso arredo; density heavy da 1.8 a 1.5.

Golden rigenerati dopo diff verificato: in entrambi i casi cambiano SOLO gli oggetti (e le luci del building, per lo scorrimento degli id), muri e pattern identici. Il golden building usa ora la taglia di default della tipologia, come il CLI. Regole documentate in docs/format.md 9.8. Suite: 330 verdi, 1 skip.

Correzione alla nota precedente: la lista condivisa fra le stanze del piano si chiama 'placed' (il backtick era stato mangiato dalla shell).

Gate umano M4 round 3. Jay: 'le botti piccole vanno ancora girate a destra di 90 gradi. Tutti gli altri vanno bene' — quindi la formula rotazione = lato * pi/2 del round 2 e confermata su tutti e quattro i lati per l'intero catalogo, e resta un solo sprite fuori posto.

Keg_Wood_Light_H_1x1: la 'H' sta per horizontal, la botte e coricata sul fianco lungo l'asse orizzontale e il suo asse parte gia ruotato di un quarto di giro rispetto agli altri sprite (che a rotazione 0 hanno la faccia in giu). Non e una regola geometrica deducibile dal lato ma una proprieta del singolo sprite, quindi tabellata per texture: compose._TEXTURE_ROTATION_OFFSET, applicata da _oriented() sia in _furnish_room sia in _furnish_tactical_cover. Riprodotto prima in due test (unitario su _rotation_offset e end-to-end sul file renderizzato), sezione ROUND 3 di tests/test_building_gate.py.

Diff del golden building verificato a mano: cambia UNA sola riga, la rotazione dell'unico keg del piano terra da 1.5708 a 3.1416. Il golden bsp non cambia (la palette dungeon non ha keg). Documentato in docs/format.md 9.8. Suite: 332 verdi, 1 skip.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-04 08:03
---
File pronto: generated/building_m4.dungeondraft_map (taverna a 2 piani, seed 1337, arredo medium, luci attive). Passa la validazione con 3 soli avvisi non bloccanti (DDF102 sul perimetro portante e sul vano scale del piano superiore, limite noto e documentato del validatore, non necessariamente un difetto della mappa).

Jay, quando puoi aprilo in Dungeondraft e verifica:
1. Il piano terra (sala comune, cucina, retro) e il primo piano (camere) sono entrambi presenti e navigabili tra le rispettive schede/livelli.
2. Il vano scale occupa la stessa posizione su entrambi i piani.
3. Le porte sono sul muro e orientate bene (stessa calibrazione di TASK-12).
4. C'e un tetto visibile sull'ultimo piano.
5. L'arredo (tavoli/sedie al piano terra, letti al primo piano) e plausibile e non blocca porte o passaggi.

In attesa della tua conferma prima di chiudere il task.
---

author: @claude
created: 2026-09-07 07:26
---
Gate umano M4, round 2. File pronti in generated/: building_m4.dungeondraft_map (taverna, 2 piani), building_m4_manor.dungeondraft_map (3 piani) e building_m4_warehouse.dungeondraft_map (2 piani, piano terra a volume unico + soppalco). Tutti seed 1337, arredo medium, luci attive.

Cosa e cambiato rispetto al round 1, difetto per difetto: i piani hanno nomi propri (Piano terra / Primo piano / ...) e il tetto sta solo sull'ultimo; il vano scale e una fascia a tutta altezza sul lato sinistro, con pavimento, porta su ogni piano, oggetto scala visibile al centro e una sua luce; le stanze tassellano esattamente il footprint e condividono i tramezzi, quindi la pianta si legge; l'arredo va per ricetta invece che per densita (35 oggetti su 8 texture diverse al piano terra della taverna, contro 253 su 2-3 del round 1) ed e addossato ai muri, ruotato parallelo a essi.

Corretto anche un difetto trovato dopo, sul file generato e non segnalato: ingresso e porta del vano scale erano murati da un secondo muro cieco sovrapposto (perimetro portante ridisegnato sopra i lati esterni delle stanze).

Due cose da guardare con attenzione, che da qui non posso verificare: (1) l'orientamento degli sprite addossati al muro — sono paralleli al muro, ma se lo sprite ha un 'davanti' potrebbe guardare verso il muro invece che verso la stanza; (2) se la scala si legge come una scala e se la sua posizione al centro del vano ha senso.

Resta 1 avviso DDF102 non bloccante sul perimetro del piano superiore (non ha una porta propria, ed e corretto cosi: ci si arriva dalle scale). Limite noto del validatore, gia documentato in docs/format.md 9.5.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
M4 chiuso: 'ddforge generate building' produce edifici multi-piano (taverna, magione, magazzino) che Jay ha aperto e approvato in Dungeondraft dopo tre round di gate umano.

Cosa fa: perimetro portante, tramezzi condivisi, vano scale con porta su ogni piano e scala visibile, tetto sul solo ultimo piano, piani con nome proprio, arredo per ricetta addossato ai muri, luci per stanza. Validato prima della scrittura (AC1); CLI con --building-type e --l-shaped (AC2); test di integrazione e golden file per seed fisso (AC3).

Il gate umano (AC4) e costato tre round e 14 difetti, ciascuno riprodotto in un test prima della correzione (AC5, tests/test_building_gate.py, 18 test). Round 1: piani senza nome, stanze tappezzate di un solo oggetto, pianta illeggibile, vano scale fuori dal perimetro. Round 2: sprite girati contro il muro, non compenetrati, sovrapposti, e stanze da 51x27 METRI perche la suddivisione era guidata dal numero di stanze invece che dalla loro dimensione. Round 3: la sola botte piccola ancora storta.

Le tre scoperte di formato che valgono oltre questo task, documentate in docs/format.md 9.7 e 9.8: (1) due muri sovrapposti di cui uno cieco tappano la porta dell'altro, quindi ogni segmento del perimetro va disegnato una volta sola; (2) uno sprite addossato si ruota di lato*pi/2 e sta a mezzo quadretto dal muro, calibrato sui camini che Jay ha corretto a mano nel file; (3) un quadretto vale 1.5 m reali, e da li discendono lato massimo di stanza e ingombro di default per tipologia.

Verifica: suite 332 verdi (1 skip), i tre edifici rigenerati validano con 0 errori e i soli avvisi DDF102 noti sul perimetro dei piani superiori (che una porta esterna non ce l'hanno per costruzione), 0 sovrapposizioni fra oggetti misurate sui file, nessuna stanza oltre 10.5 m di lato, 0 corridoi scavati dentro le stanze.
<!-- SECTION:FINAL_SUMMARY:END -->
