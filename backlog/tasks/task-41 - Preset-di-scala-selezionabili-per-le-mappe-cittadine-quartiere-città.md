---
id: TASK-41
title: Preset di scala selezionabili per le mappe cittadine (isolato/quartiere/citta)
status: Done
assignee:
  - '@claude'
created_date: '2026-09-04 07:24'
updated_date: '2026-09-09 12:00'
labels: []
milestone: m-8
dependencies:
  - TASK-34
  - TASK-35
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 41000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A 256 px/quadretto un quartiere giocabile e' gia' enorme, una citta' intera diventa ingestibile (SPEC.md 9.4). TASK-34 aveva lasciato la decisione sospesa a un parametro --scale con due regimi possibili; decision-2 ha deciso di supportare entrambi i regimi come preset selezionabili invece di scegliere un solo regime fisso.

Al round 2 del gate umano Jay ha rivisto la scala e i nomi, e ha chiesto TRE preset invece di due, rinominando i due esistenti:

- preset 'isolato' (era 'quartiere'): scala giocabile a 5 ft/quadretto, edifici con pianta completa (muri, stanze, porte, tetto) - la mappa su cui si muovono le miniature.
- preset 'quartiere' (era 'citta'): 1 quadretto = 1 edificio, un quartiere intero visto dall'alto.
- preset 'citta' (nuovo): una citta' intera, capace di contenere una decina di quartieri.

Il lavoro deve chiudere anche la parte di misurazione e documentazione lasciata aperta da TASK-34 (dimensioni file e tempi di apertura nei regimi supportati).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Un parametro di scala (es. --scale) permette di scegliere fra i tre preset isolato, quartiere e citta al momento della generazione
- [x] #2 Il preset 'isolato' produce una mappa a 5 ft/quadretto con edifici a pianta completa, lotti con fronte strada, strade e piazze
- [x] #3 Il preset 'quartiere' produce una mappa a 1 edificio/quadretto per un quartiere intero
- [x] #4 Il preset 'citta' produce una mappa che contiene una decina di quartieri, cioe un ordine di grandezza piu edifici del preset 'quartiere' sullo stesso canvas
- [x] #5 Le dimensioni in byte e i tempi di apertura risultanti nei tre preset su un caso reale sono misurati e documentati
- [x] #6 La differenza fra i tre preset e come sceglierli e documentata nel README e nella skill
- [x] #7 Il documento generato in tutti i preset passa validate() senza errori
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. generators/city.py: rinomina le chiavi di SCALE_PRESETS - 'quartiere' (5 ft/quadretto, edifici pieni) -> 'isolato'; 'citta' (1 quadretto = 1 edificio) -> 'quartiere'. DEFAULT_SCALE = 'isolato' (preserva l'output di default byte per byte, solo il nome cambia). Aggiorna i commenti/docstring di modulo che nominano i preset.
2. Nuovo preset 'citta' (whole city, ~10 quartieri): scala geometrica del nuovo preset 'quartiere' di un fattore lineare ~3.25 (street width, block/lot size, setback, building depth, min_yard, min_building_side), depth_max piu alto per permettere piu tagli. Misurato su blank_80x80 78x78: ~3260-3280 edifici contro 322 del preset 'quartiere' = ~10.1x, dentro 'un ordine di grandezza'/'una decina di quartieri' (AC4). abstract_buildings=True come l'attuale 'citta'.
3. cli.py: --scale {isolato,quartiere,citta}, default 'isolato'.
4. tests/test_generators_city.py e tests/test_cli_generate.py: aggiorna i riferimenti a scale='quartiere'/'citta' con la nuova semantica a tre; aggiungi test per il nuovo preset 'citta' (densita ~10x rispetto a quartiere, nessuna sovrapposizione, dentro al canvas, render+validate pulito) rispecchiando i test gia esistenti per isolato/quartiere.
5. Verifica golden file: il default 'isolato' deve produrre lo stesso output byte per byte dell'attuale default 'quartiere' (solo rinominato) - nessuna rigenerazione attesa.
6. Misure (AC5): genera i tre file su blank_80x80 (78x78, seed 1337), misura i byte, verifica validate() pulito sui tre. I tempi di apertura restano una misura che solo Jay puo dare (nota gia aperta nei round precedenti).
7. Documentazione (AC6): README (sezione preset aggiornata da due a tre), skill/references/styles.md, docs/SPEC.md §9.4.
8. Genero i tre file di esempio e chiedo a Jay il gate round 3 prima di chiudere il task (AC4 e i tempi di apertura restano aperti finche' non risponde).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
IMPLEMENTATO

- model.py: nuovo campo Blueprint.building_footprints (list[Rect]) per gli edifici del preset citta. I due campi edificio si escludono a vicenda (buildings per quartiere, building_footprints per citta) e compose non lo pretende: disegna quello che trova.
- generators/city.py: dataclass ScalePreset (11 campi: larghezze strade, soglie isolato, profondita, lotti, margine, arretramento, lato minimo edificio, e il flag abstract_buildings) e tabella SCALE_PRESETS con 'quartiere' e 'citta'. Le costanti sciolte di TASK-35 (_MIN_BLOCK, _MAIN_STREET_WIDTH, ...) sono sparite dentro il preset 'quartiere' con gli stessi valori. generate() prende scale='quartiere' (DEFAULT_SCALE) e in alternativa un preset=ScalePreset(...) tarato a mano. _build_blocks prende il preset invece di 6 kwargs. Nuovo _building_area() condiviso dai due percorsi (margine sui lati non-fronte + arretramento sul fronte), _place_building (quartiere, come prima) e _place_footprint (citta).
- compose.py: nuove _ridge_line() e draw_city_footprint(); render_city_blueprint disegna anche blueprint.building_footprints.
- cli.py: --scale {quartiere,citta} su 'generate' (default quartiere), passato solo al ramo city. Scritto senza accento perche' e' un valore da riga di comando su Windows; decision-2 lo chiama 'citta'.

ORDINE DELL'RNG PRESERVATO. Nel preset quartiere il seed dell'edificio va estratto PRIMA di entrare in _place_building (che consuma l'RNG per l'arretramento): era l'effetto della valutazione degli argomenti in TASK-35 (_place_building(..., seed=rng.randrange(...))), ora e' una riga esplicita con un commento. Il golden file tests/fixtures/golden/city_seed_1337.json passa senza essere rigenerato: e' la prova che il preset quartiere non e' cambiato.

CORRETTO UN DIFETTO LATENTE DI TASK-35. _split_into_lots calcolava il bordo dell'ultima striscia come block.x1 + span*n/n, che in virgola mobile non ridà block.x2 esatto: l'ultimo lotto sporgeva di 1 ULP fuori dall'isolato. Invisibile col preset quartiere (lotti grandi, bordi su valori tondi), lo ha fatto emergere il preset citta al seed 2. Ora l'ultima striscia prende il bordo dell'isolato cosi com'e. Nessun effetto sul golden file (verificato).

SCOPERTA SUL FORMATO: roof.points e' la linea di COLMO e roof.width e' la MEZZA larghezza (colmo->gronda), non la larghezza totale. Non era mai stato verificabile: i due soli campioni noti (rich_reference, Conyberry) hanno un tetto isolato senza niente sotto (Conyberry ha zero muri su tutti i livelli, verificato). Prova trovata in dungeondraft_maps/crosshead_style/tresendar_manor_full.dungeondraft_map, che tiene gli 11 tetti su un livello dedicato e i muri su un altro: colmo verticale x=2560 width=768 -> muri a x=1790,5 e x=3325,9 (attesi 1792 e 3328); colmo x=5632 width=768 -> muro a x=4864 (= 5632-768, ed e' il massimo x di quel livello). Con la lettura 'larghezza totale' le gronde cadrebbero a 2176/2944 e 5248/6016, valori che non compaiono fra i muri. Documentato in docs/format.md 5. draw_city_footprint la usa: colmo lungo il lato lungo, width = meta del lato corto, gronde esattamente sui bordi del footprint (test dedicato).

MISURE (AC4), su templates/blank_80x80.dungeondraft_map, 78x78, seed 1337:
- blank (riferimento): 1.676.423 B
- --scale quartiere: 1.883.240 B, 16 edifici, 150 muri, 88 porte, 54 pattern, 15 strade, 16 tetti. Delta dal blank 206.817 B = ~12.926 B/edificio.
- --scale citta: 1.979.924 B, 215 edifici, 0 muri, 217 pattern, 62 strade, 215 tetti. Delta 303.501 B = ~1.412 B/edificio.
- Densita: 1 edificio ogni ~380 quadretti (quartiere) contro 1 ogni ~28 (citta), cioe 13x piu edifici sullo stesso canvas.
- Estrapolazione: rappresentare gli stessi 215 edifici a scala quartiere richiederebbe ~81.700 quadretti, cioe un canvas ~286x286, che nessun template fornisce (prepare() non tocca mai world.width/height). Il costo in byte sarebbe ~24 MB (base del canvas scalata linearmente + elementi) contro 1,98 MB.
- Precisazione onesta su decision-2: la sua stima di ~2,4 MB per edificio a scala quartiere veniva dai file building_m4 (edifici singoli, multi-piano, arredati e illuminati), i soli disponibili prima che city.py esistesse. Misurato sul generatore vero, un edificio del preset quartiere di city.py costa ~12,9 KB, non 2,4 MB: sono cose diverse (casa a un piano non arredata contro taverna/villa arredata). La conclusione di decision-2 resta valida, ma il vincolo vero e' la DIMENSIONE DEL CANVAS (286x286 non esiste), non i byte.

ROBUSTEZZA: 240 combinazioni (2 preset x 4 dimensioni x 30 seed) senza una sola sovrapposizione edificio/strada/piazza, nessun edificio fuori canvas, e un render+validate per ogni dimensione con 0 errori e 0 avvisi. Canvas minuscoli (3x3, 6x6, 10x10, 12x8) degradano a citta vuota o a pochi edifici senza strade, senza crash.

TEST: +23 nel file di city (i due preset in parametrize dove la garanzia e' comune, piu una sezione dedicata: tabella dei preset, errore esplicito su uno scale sconosciuto, default = quartiere identico all'esplicito, i due campi edificio che si escludono, densita/dimensione degli edifici, nessuna sovrapposizione, dentro il canvas, render+validate pulito con un tetto e un pavimento per edificio e zero muri, gronde sui bordi del footprint) e +2 in test_cli_generate.py (--scale citta end-to-end, e default = quartiere byte per byte). Suite completa: 523 passed, 1 skipped.

DOCUMENTAZIONE (AC5): README.md nuova sezione 'Mappe cittadine: i due preset di scala' (tabella di confronto coi numeri misurati, come scegliere, due comandi di esempio); skill/references/styles.md creato (algoritmi, palette, tipologie di edificio, i due preset, arredo/luci) - la cartella skill/ aveva solo .gitkeep, il file e' previsto da SPEC.md 11 e da TASK-38 AC2, qui e' scritto per quello che serve a scegliere stile e scala e resta da completare in TASK-38; docs/SPEC.md 9.4 con la nota che la decisione di M5 e' presa e implementata; docs/format.md 5 con la semantica di roof.points/roof.width e la prova.

FOLLOW-UP DA APRIRE, non corretto qui: con roof.width = mezza larghezza, il tetto di compose.draw_building (poligono chiuso del footprint, width 512 di default) sborda 2 quadretti oltre l'edificio su ogni lato. Riguarda TASK-27/TASK-35 e un output gia approvato da Jay al gate umano M4: cambiarlo in silenzio significherebbe modificare un risultato validato senza un nuovo riscontro visivo.

NOTA DI CONTESTO: durante questo lavoro un'altra sessione stava implementando TASK-37 (ddforge preview) nello stesso working tree - src/ddforge/preview.py, tests/test_preview.py e il ramo preview di cli.py sono suoi, non di questo task.

Il follow-up sul tetto di draw_building e' stato aperto come TASK-47 (bug), con la prova sul formato e il motivo per cui non e' stato corretto qui.

SOSPESO su richiesta di Jay dopo il round 1 del gate (vedi il commento con il riscontro verbatim, le misure, la causa della texture sbagliata e il design del round 2). Albero lasciato verde: 523 passed, 1 skipped. Le uniche modifiche del round 2 gia dentro sono la rimozione del vano scale dagli edifici a un piano (building.py) e la dataclass Street (model.py, ancora inerte); il golden di city e stato rigenerato per la prima delle due, con il diff verificato a mano.

ROUND 2 DEL GATE - implementato tutto quello che Jay ha chiesto.

1. CASE GRANDI LA META (entrambi i preset). Due cause corrette, non una:
   - I lotti coincidevano con l'isolato: target_lot_len 11 contro isolati 10-16 dava n=1 quasi sempre. Ora gli isolati sono 13-22 e i lotti 9, quindi ogni isolato ne contiene davvero piu di uno.
   - L'edificio riempiva tutta la profondita del lotto. Nuovo campo building_depth_range: la profondita e misurata DAL FRONTE strada e limitata (quartiere 6-9, citta 1,8-3), il resto del lotto resta cortile. E' questo il freno vero: senza, nel preset citta ogni edificio era una striscia ~2x6 lunga quanto l'isolato (la media 4,6x4,2 lo nascondeva, perche mediava strisce orientate nei due versi).
   Misurato su 78x78 seed 1337: quartiere da 9,6x8,7 quadretti (181 m2) a 4,7x5,2 (55 m2), e da 16 a 30 edifici; citta da ~2x6 a 2,5x2,4, e da 215 a 322 edifici. Test di regressione dedicato (area media sotto 40 quadretti su 8 seed).
   Aggiunti anche i lotti su DUE file schiena contro schiena negli isolati profondi (_lot_rows), ognuna col fronte sulla via opposta e il cortile in mezzo: front_side ora puo valere tutti e quattro i lati, non solo BOTTOM/RIGHT.

2. STRADE PIU IRREGOLARI, NON SOLO VERTICALI E ORIZZONTALI. Due meccanismi, tenuti separati di proposito:
   - Ogni via da taglio e ora una polilinea che serpeggia (model.Street: points + width + corridor + main). L'ingombro riservato resta rettangolare e il selciato e piu stretto (street_path_fraction 0,65-0,7): lo scarto laterale sta in cio che avanza, quindi TUTTE le garanzie di TASK-35 (fronte strada, nessun edificio in strada) continuano a dipendere dall'ingombro e non dalla forma del tracciato. Gli estremi non si spostano, cosi gli incroci restano allineati.
   - Una via obliqua per mappa (_avenue), da un bordo a quello opposto, che non avendo ingombro riservato si fa spazio togliendo gli edifici che incontra (_clear_avenue, distanza rettangolo-polilinea per campionamento a 0,25 quadretti). Primo tentativo scartato: con passo e scarto pari a quelli delle vie da taglio veniva un zigzag a tornanti, non una diagonale; ora i vertici stanno 3 volte piu distanti e lo scarto e il 40% della via principale. Nessuna via obliqua su un canvas troppo piccolo per essere diviso nemmeno una volta.

3. TEXTURE. Causa trovata, non tentativi: estratte e guardate tutte e 44 le texture di res://textures/paths/ dal Dungeondraft.pck (i .stex contengono un PNG/WebP incorporato). res://textures/paths/cobble.png, scelta in TASK-35 sul solo nome, NON e una pavimentazione: e una texture da muretto, blocchi grigi con contorno nero, come stone/stone_09/concrete/battlements/cliff/wood e tutti i *_fence_*. Le uniche vere superfici stradali sono wagon_trail (sterrato quasi invisibile) e i quattro path_blender_0X. Provate su render della mappa vera: path_blender_01 (grigio-pietra) si perde nel terreno del template, path_blender_03 (terra battuta) stacca sia dal terreno sia dai tetti. Scelta path_blender_03; l'alternativa grigia e una riga in compose._STREET_TEXTURE.

4. TIPI DI EDIFICIO DIVERSI (preset quartiere). Nuovo _BUILDING_REPERTOIRE: house, house a pianta a L (building.generate ha gia l_shaped), tavern, warehouse, manor, con pesi e una soglia di lato minimo per tipologia. Delle multi-piano si tiene il SOLO piano terra (su una mappa cittadina i piani alti non si disegnano: portarsi dietro stanze che nessuno disegna vorrebbe dire un Blueprint che non descrive quel che si vede), il vano scale resta. Le soglie sono state TARATE sulla distribuzione reale dei lotti, non a occhio: col primo tentativo (10 alle multi-piano, 8 alla pianta a L) nessuna tipologia oltre house risultava mai ammissibile e tutti gli edifici venivano identici, cioe esattamente il difetto segnalato. Misurato: il lato minore passato a building.generate vale 6 nel 53% dei casi, 7 nel 34%, 8 nel 9%; soglie portate a 6/6/7/7/8. Su 8 seed: 195 house, 18 tavern, 15 warehouse, 4 manor.

5. FUORI RICHIESTA MA NECESSARIO: IL TETTO. Con le case dimezzate lo sbordo di 2 quadretti per lato del tetto di draw_building (TASK-47) e diventato il difetto dominante invece di un dettaglio: su una casa 5x5 il tetto risultava 9x9, in mezzo alla strada e sovrapposto a quello del vicino. Verificato renderizzando i tetti come fascia centrata sul perimetro - riempiendo il poligono lo sbordo non si vede, ed e per questo che al round 1 era sfuggito. Corretto a raggio minimo: draw_building prende roof=True/False e render_city_blueprint lo chiama con roof=False, disegnando il tetto con la nuova compose.add_ridge_roof (linea di colmo, gronde esattamente sui bordi). L'output di 'ddforge generate building' resta identico, perche cambiarlo richiede il riscontro visivo di Jay che gli AC di TASK-47 chiedono: TASK-47 aggiornato con questo restringimento di perimetro.

MISURE AGGIORNATE (AC4), 78x78 seed 1337 su blank_80x80 (1.676.423 B):
- quartiere: 1.867.121 B, 30 edifici, 16 vie (1 obliqua), 2 piazze, 150 muri, 43 pattern, 30 tetti. ~6.357 B/edificio.
- citta: 2.089.561 B, 322 edifici, 53 vie (1 obliqua), 2 piazze, 0 muri, 324 pattern, 322 tetti. ~1.283 B/edificio.
- Gli stessi 322 edifici a scala quartiere richiederebbero ~285x285 quadretti, che nessun template fornisce.

ROBUSTEZZA: 240 combinazioni (2 preset x 4 dimensioni x 30 seed) con zero sovrapposizioni edificio/ingombro-via/piazza, zero edifici fuori canvas, zero edifici sulla via obliqua; un render+validate per dimensione con 0 errori e 0 avvisi. Canvas minuscoli degradano senza crash.

TEST: 113 nel file di city (erano 73), fra cui centro-linea dentro l'ingombro con serpeggio verificato, via obliqua passante e senza edifici addosso, tetti a colmo senza sbordo, piu di una tipologia su 8 seed, area media degli edifici sotto soglia, profondita limitata in entrambi i preset. Golden rigenerato due volte con diff verificato a mano ogni volta (la seconda: solo la texture dei path, tutto il resto identico byte per byte). Suite completa: 563 passed, 1 skipped.

STRUMENTO DI LAVORO: scritto un renderer usa-e-getta nello scratchpad (non in src/) che legge un .dungeondraft_map e disegna path con la texture vera estratta dal pck, pattern, tetti (sia a colmo sia a poligono) e muri. Serviva per giudicare senza aprire Dungeondraft a ogni giro; e cio che ha fatto trovare sia il problema del tetto sia quello dello zigzag. Nel scriverlo e emerso un dettaglio del formato utile: un regex sui numeri applicato all'intera stringa 'PoolVector2Array( ... )' cattura anche il '2' del nome e sfasa tutte le coppie - ddforge.godot.parse_pv2 lo evita leggendo solo dentro le parentesi.

ROUND 3 DEL GATE - implementata la richiesta di Jay: tre preset rinominati invece di due (isolato/quartiere/citta).

1. RINOMINA. generators/city.py: SCALE_PRESETS['quartiere'] (5 ft/quadretto, edifici pieni) -> 'isolato'; SCALE_PRESETS['citta'] (1 quadretto = 1 edificio) -> 'quartiere'. Nessun valore numerico toccato in questi due: DEFAULT_SCALE = 'isolato' produce lo stesso output byte per byte del vecchio default 'quartiere' (verificato: test_default_scale_is_the_isolato_preset_unchanged e il golden file passano senza rigenerazione). cli.py: --scale {isolato,quartiere,citta}, default 'isolato'.

2. NUOVO PRESET 'citta' (AC4: contiene una decina di quartieri, un ordine di grandezza in piu di edifici del preset quartiere sullo stesso canvas). Ogni costante e quella del preset 'quartiere' scalata di un fattore lineare ~3,25 (street width, block/lot size, setback, building depth, min_yard, min_building_side; depth_max piu alto per permettere piu tagli). Misurato su blank_80x80 78x78 su 7 seed: da 9,6x a 10,8x il numero di edifici del preset 'quartiere' a parita di canvas (322 -> 3.113-3.365). abstract_buildings=True, stessa rappresentazione astratta di 'quartiere' (pavimento + tetto a colmo, senza stanze).

3. BUG TROVATO E CORRETTO (non nella scala, nel formato). Il preset 'citta' ha fatto emergere un difetto latente in ddforge.godot._fmt_number: repr() passa alla notazione scientifica sotto 1e-4 (es. '8.567903932998888e-05'), che ne' il letterale Godot ne' _PV2_RE/parse_pv2 riconoscono (fallisce con DDF007 'PoolVector2Array non valida'). Con isolato/quartiere non si era mai visto: le coordinate non si avvicinano mai cosi tanto a zero. Con isolati di 1,85-3,4 quadretti (contro 6-22 degli altri due preset) il rumore di arrotondamento nella centro-linea serpeggiante (model.Street, TASK-41 round 2) puo produrre un delta vicino a zero fra due punti quasi coincidenti. Corretto: se repr() emette 'e', _fmt_number la riespande in notazione posizionale via decimal.Decimal(repr(n)), stesse cifre, round-trip esatto. Nessun impatto sugli altri generatori (mai avvicinati a 1e-4): tutta la suite (613 test, golden file inclusi) passa identica prima e dopo la modifica. Nuovo test dedicato in tests/test_godot.py (test_pv2_never_emits_scientific_notation). Trovato con una sweep di robustezza dedicata (240 combinazioni: 3 preset x 8 dimensioni di canvas x 10 seed, render+validate ogni volta): 1 fallimento (citta, 100x60, seed 7) prima della correzione, 0 dopo.

4. TEST. tests/test_generators_city.py: tutti i parametrize scale=['quartiere','citta'] estesi a ['isolato','quartiere','citta'] (i test generici sulla rete stradale/centro-linea/vie oblique valgono per tutti e tre); i test specifici del vecchio 'citta' (nessuna sovrapposizione, dentro il canvas, render+validate pulito, gronde sui bordi) ora parametrizzati su ['quartiere','citta'] (entrambi astratti); nuovo test_citta_preset_has_an_order_of_magnitude_more_buildings_than_quartiere (margine 5x-20x per non dipendere dal seed esatto); rinominati i test specifici di 'isolato' (edifici pieni, tipologie, dimensione) da test_quartiere_* a test_isolato_*. Un test (via obliqua assente su canvas troppo piccolo) usava un canvas 8x8 fisso tarato sui preset piu radi: con min_block 1,85 del preset citta un 8x8 e abbastanza grande da dividersi, quindi il test falliva per il preset citta (non un bug del generatore, un'assunzione della fixture) - corretto derivando la soglia da preset.min_block invece di un valore fisso. tests/test_cli_generate.py aggiornato allo stesso modo, piu un test end-to-end dedicato all'ordine di grandezza citta/quartiere. Suite completa: 613 passed, 1 skipped (era 563 passed prima di questo round).

5. MISURE (AC5, bytes fatte - tempi di apertura restano da chiedere a Jay), su templates/blank_80x80.dungeondraft_map (78x78, seed 1337, riferimento blank 1.676.423 B), generati in generated/city_{isolato,quartiere,citta}_task41.dungeondraft_map:
- isolato: 1.867.121 B, 30 edifici (invariato dal round 2, solo rinominato), ~6.357 B/edificio.
- quartiere: 2.089.561 B, 322 edifici (invariato dal round 2, solo rinominato), ~1.283 B/edificio.
- citta: 5.437.005 B, 3.325 edifici, ~1.131 B/edificio. Rapporto citta/quartiere sullo stesso canvas: 10,3x (AC4).
Tutti e tre passano validate() senza errori (AC7): la CLI valida obbligatoriamente prima di scrivere (TASK-24), quindi la sola presenza dei tre file ne e prova.

6. DOCUMENTAZIONE (AC6): README.md sezione riscritta da 'i due preset' a 'i tre preset' con la tabella aggiornata (isolato/quartiere/citta, misure sopra) e i tre comandi di esempio; skill/references/styles.md stessa tabella, stesso 'come scegliere'; docs/SPEC.md 9.4 nota aggiornata con la cronologia (decision-2 -> TASK-41 due preset -> round 2 del gate -> tre preset rinominati). Corretti anche i riferimenti sparsi ai vecchi nomi nei docstring/commenti di generators/city.py, compose.py, model.py, cli.py (dove parlavano del preset 'quartiere' che oggi e' 'isolato', o del preset 'citta' che oggi copre sia 'quartiere' che 'citta').

7. FOLLOW-UP aperto su TASK-47 (bug del tetto di draw_building, non di city.py): aggiunto un commento con la mappatura dei nomi rinominati, perche' quel task cita ancora 'preset quartiere' con il significato vecchio e il nome di un test che qui e' stato rinominato. Nessun impatto sui suoi AC.

AC5 resta parzialmente aperta: le dimensioni in byte sono misurate e documentate, i tempi di apertura in Dungeondraft li puo dare solo Jay aprendo i tre file. Task lasciato In Progress in attesa del gate round 3: Jay deve confermare che tre preset/nomi/numeri sono quelli giusti prima di chiudere.

GATE ROUND 3 - Jay ha confermato i tre preset rinominati ('molto bene').

VERIFICA SU UN QUARTO CASO REALE: Jay ha aggiunto templates/blank_160x160.dungeondraft_map (nome commerciale; il mondo dentro il file e' in realta' 128x128 quadretti, letto da world.width/height - non e' un errore di ddforge, e' cosi' che Dungeondraft ha salvato il template). Generato --scale citta --width 126 --height 126 (stesso margine di 1 quadretto usato per blank_80x80): 8.927 edifici, 1.300 vie, 14,4 MB, validate() pulito (0 avvisi, 0 errori) - la densita' ~10x rispetto a quartiere sulla stessa area si conferma anche a questa scala di canvas (stimati ~840 edifici per quartiere sulla stessa area, rapporto ~10,6x). Confermato per la stessa occasione che --scale funziona a qualunque dimensione di template, nessun preset dedicato ai canvas grandi necessario (era la domanda di Jay che ha portato al template 160x160).

AC5: le dimensioni in byte sono misurate e documentate (README.md, skill/references/styles.md) su tre canvas reali (78x78 col preset originale, 126x126/128 col preset citta per la prova metropoli). I TEMPI DI APERTURA non sono mai stati numeri espliciti da parte di Jay: la verifica e' stata qualitativa, aprendo ripetutamente i file nei tre round del gate (incluso questo quarto file piu' grande) senza segnalare alcun problema. Jay ha confermato esplicitamente e chiesto di chiudere il task: AC5 spuntata su questa base, non su un cronometro.

Task chiuso su istruzione esplicita di Jay ('molto bene. Chiudi il task e committa tutto').
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-08 18:38
---
GATE ROUND 1 - riscontro di Jay sui due file generati (2026-09-08), e stato in cui il lavoro e' stato sospeso su sua richiesta ('fermati dove sei in modo che io possa riprendere domani').

RICHIESTE DI JAY, verbatim:
1. 'nel quartiere le case possono essere grandi la meta di quello che sono'
2. 'Le strade devono essere piu irregolari, non solo verticali e orizzontali'
3. 'Cambia anche la texture che usi che quella attuale e orribile'
4. 'Anche nella citta le case sono troppo grandi e le strade sono molto brutte. Dimezza anche qui le dimensioni'
5. 'Non usare un unico oggetto per gli edifici ma usane di diversi tipi'

MISURE FATTE PRIMA DI SOSPENDERE (78x78, seed 1337):
- quartiere: 16 edifici, footprint medio 9,6x8,7 quadretti = 14,4x13 m = 181 m2. Enorme per una casa di citta. Meta lineare = ~4,8x4,4.
- citta: 215 edifici, footprint medio 4,6x4,2 - ma il valore medio inganna: ogni edificio e in realta una striscia ~2x6, perche il lotto occupa TUTTA la profondita dell'isolato. Meta = ~2,3x2,1.
- Causa vera della dimensione: (a) _split_into_lots produce quasi sempre n=1 (target_lot_len 11 contro isolati 10-16), quindi il lotto E l'isolato; (b) l'edificio riempie tutta la profondita del lotto, non c'e un tetto massimo alla profondita.

PERCHE LA TEXTURE E ORRIBILE (causa trovata, non ipotesi): res://textures/paths/cobble.png non e una pavimentazione, e una texture da MURETTO - blocchi grigi con contorno nero spesso, pensata per disegnare recinti e merlature come path. Estratte e guardate tutte le 44 texture di res://textures/paths/ dal Dungeondraft.pck (i .stex contengono un PNG/WebP incorporato): le uniche vere strade sono wagon_trail.png (sterrato con solchi, molto tenue) e path_blender_01..04 (tracciati organici a bordi irregolari: 01/02 grigio-pietra, 03/04 sabbia-terra). Tutte le altre (stone, stone_09, concrete, battlements, cliff, wood, i vari *_fence_*) sono murature o staccionate. Candidata scelta: path_blender_01.png (selciato grigio, bordo irregolare - il bordo irregolare della texture stessa aiuta anche la richiesta 2); alternativa da mostrare a Jay: path_blender_03.png (strada di terra). Contact sheet in scratchpad, non committato.

DESIGN DECISO PER IL ROUND 2 (non ancora implementato, salvo i due pezzi qui sotto):
a) ScalePreset guadagna: street_path_fraction (frazione dell'ingombro riservato che viene davvero selciata, ~0,65), street_segment_len (passo dei vertici della centro-linea), building_depth_range (profondita massima dell'edificio misurata dal fronte strada: e questo il freno vero alla dimensione), min_yard, avenues (quante vie oblique).
b) Strade irregolari: la centro-linea diventa una polilinea che serpeggia dentro l'ingombro riservato (l'ingombro resta rettangolare, quindi le garanzie di fronte-strada e non-sovrapposizione di TASK-35 restano intatte per costruzione). Estremi non spostati, cosi gli incroci restano allineati. Il selciato e piu stretto dell'ingombro: e da li che viene lo spazio per serpeggiare.
c) Vie oblique: 1-2 per mappa, da un bordo al bordo opposto, con vertici sbandati; gli edifici che incontrano vengono tolti. E' quello che risponde davvero a 'non solo verticali e orizzontali'.
d) Isolati piu grandi dei lotti (quartiere 13-22 contro lotti ~8) cosi n>1 e i lotti smettono di coincidere con l'isolato; e lotti su DUE file schiena contro schiena quando l'isolato e abbastanza profondo, ognuna col proprio fronte strada sul lato opposto, con il cortile in mezzo. front_side puo cosi valere anche _LEFT/_TOP, che _building_area gia gestisce.
e) Tipi di edificio diversi nel preset quartiere: scelta pesata fra house, house a L (building.generate ha gia l_shaped), tavern, warehouse, manor, con una soglia di lato minimo per le tipologie multi-piano (misurato: sotto 9x9 il loro piano terra si riduce a una stanza sola). Delle multi-piano si disegna il solo piano terra, che e cio che ha senso su una mappa cittadina.
f) La varieta degli edifici del preset CITTA non va costruita qui: e TASK-46, che sostituisce l'ingombro astratto con gli sprite del pack BB Houses1 (33 case diverse). Costruire ora un meccanismo di varieta per rettangoli che verranno buttati sarebbe lavoro sprecato.

FATTO PRIMA DI SOSPENDERE (albero verde, 523 passed 1 skipped):
- building.py: un edificio a un solo piano non riceve piu il vano scale. Era un difetto vero: ogni casa generata da city.py aveva una fascia larga 2 quadretti su tutta l'altezza (un terzo della pianta di una casetta) che portava da nessuna parte, quindi la casa era un ripostiglio murato piu una stanza. Ora house a 5x5 da una pianta 3x3 piena invece di 1x3. Tocca solo la tipologia 'house' (le altre tre sono multi-piano), quindi solo city.py.
- model.py: nuova dataclass Street (points, width, corridor, main), che serve al punto b/c. NON ancora usata da nessuno: city.py popola ancora blueprint.streets con dei Rect. E' codice additivo e inerte, non rompe niente.
- Rigenerato tests/fixtures/golden/city_seed_1337.json per la rimozione del vano scale. Diff verificato a mano: fuori dal livello tutto identico; dentro, 19 muri, 14 portali e 7 pattern in meno (una stanza in meno per edificio), mentre paths (15), roofs (12) e objects (2) sono invariati. Il golden andra rigenerato di nuovo quando arriva la geometria del round 2.

DA FARE ALLA RIPRESA, in ordine: (1) implementare a-e in city.py/compose.py; (2) cambiare _STREET_TEXTURE in compose.py; (3) aggiornare i test che trattano blueprint.streets come Rect (ora sono Street: usare street.corridor e street.width) e aggiungerne per centro-linea dentro l'ingombro, vie oblique senza edifici addosso, profondita massima rispettata, tipi di edificio piu di uno; (4) rigenerare il golden; (5) rigenerare i due file di generated/ e far vedere a Jay anche le due varianti di texture (path_blender_01 contro path_blender_03) prima che apra Dungeondraft; (6) AC4 resta aperta: i tempi di apertura li puo dare solo Jay.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Aggiunti i tre preset di scala richiesti da Jay al round 2 del gate (isolato/quartiere/citta, default isolato) in generators/city.py SCALE_PRESETS, con --scale su cli.py. isolato e quartiere sono i due preset esistenti rinominati senza cambiare un byte del loro output (golden file invariato); citta e' nuovo, tarato ~3,25x piu denso di quartiere per ottenere l'ordine di grandezza (~10x, misurato 9,6x-10,8x su 7 seed) richiesto da Jay ("una decina di quartieri"). Nel percorso e' emerso e stato corretto un bug latente in ddforge.godot._fmt_number: repr() passava a notazione scientifica per coordinate vicine a zero (amplificate dalla geometria minuta del preset citta), non riconosciuta dal parser PoolVector2Array ne' da Godot; corretto in modo generico (nessun impatto sugli altri generatori, verificato sull'intera suite).

Verificato con: 613 test (era 563), golden file invariato, sweep di robustezza dedicata (240 combinazioni preset x dimensione x seed, zero sovrapposizioni/uscite dal canvas/errori di validate), tre file reali generati e aperti da Jay su blank_80x80 (isolato 30 edifici/1,87MB, quartiere 322/2,09MB, citta 3.325/5,44MB), piu una quarta prova su un template 160x160 (mondo reale 128x128) aggiunto da Jay per verificare la scala a un canvas piu grande: 8.927 edifici, validate() pulito, densita' ~10x confermata anche li'. Documentato in README.md, skill/references/styles.md, docs/SPEC.md 9.4.

AC5 (dimensioni in byte e tempi di apertura): byte misurati e documentati su quattro canvas reali; i tempi di apertura restano una conferma qualitativa di Jay (aperture ripetute senza problemi nei tre round del gate), mai un numero cronometrato - Jay ha confermato ed esplicitamente chiesto la chiusura del task su questa base.
<!-- SECTION:FINAL_SUMMARY:END -->
