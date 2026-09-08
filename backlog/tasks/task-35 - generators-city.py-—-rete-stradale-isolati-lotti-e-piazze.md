---
id: TASK-35
title: 'generators/city.py — rete stradale, isolati, lotti e piazze'
status: Done
assignee:
  - '@claude'
created_date: '2026-09-03 11:35'
updated_date: '2026-09-08 06:34'
labels: []
milestone: m-8
dependencies:
  - TASK-34
  - TASK-28
documentation:
  - docs/SPEC.md
modified_files:
  - src/ddforge/model.py
  - src/ddforge/generators/building.py
  - src/ddforge/generators/city.py
  - src/ddforge/assets.py
  - src/ddforge/compose.py
  - src/ddforge/cli.py
  - tests/test_generators_city.py
  - tests/test_cli_generate.py
priority: high
type: feature
ordinal: 35000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generatore di quartieri e città (SPEC.md §9.4): partizione ricorsiva del canvas in isolati con strade larghe 2-4 quadretti e una via principale più larga; suddivisione degli isolati in lotti con fronte strada garantito; un edificio per lotto riusando building.py a un solo piano, con arretramento casuale dal fronte; tetti su tutti gli edifici, perché in una mappa cittadina si vede dall'alto; 1-2 isolati lasciati vuoti come piazze con pavimentazione diversa e pozzo o fontana al centro. Le strade vanno realizzate con add_path e texture di acciottolato, non come pattern.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Ogni lotto ha fronte strada e nessun edificio è inaccessibile
- [x] #2 Le strade sono realizzate con add_path e texture di acciottolato, non con pattern
- [x] #3 La via principale è più larga delle strade secondarie
- [x] #4 Tutti gli edifici hanno un tetto
- [x] #5 Sono presenti 1-2 piazze con pavimentazione diversa e un elemento centrale
- [x] #6 Il documento generato passa validate() senza errori
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Ricerca fatta: bsp.py (_build_tree/_split_rect, partizione ricorsiva senza gap), building.py (generate() produce un Blueprint multi-piano riusando _build_tree; _BUILDING_TYPES e un dict floor->kinds facilmente estendibile; default_size/_STAIRS_MIN_SIDE/_TILE_METERS), compose.py (draw_building disegna UN edificio per Blueprint: perimetro dal bounding box delle sue room+stairs_rect, un tetto, un vano scale — non si presta a piu edifici nello stesso Blueprint), model.Blueprint (gia estesa per varianti con campi opzionali dedicati: cave_grid per le grotte, chambers per le fognature — stesso pattern da seguire per city), assets.py (style "city" gia esiste: wall=cobble, floor=cobblestone, door=threshold_01, accents={fountain}, ma SENZA roof/wall_load_bearing/stairs — draw_building non disegnerebbe tetti, AC4 fallirebbe), cli.py (l'algoritmo "city" e gia nelle choices del parser ma non in _load_generators: dungeon/building/cave/sewer mostrano che il wiring CLI (_load_generators + ramo dedicato in _cmd_generate) e sempre stato parte del task del singolo generatore, non rimandato a TASK-36 — TASK-33/sewer, ancora In Progress ma con CLI gia cablata, conferma il pattern).

Decisioni di design (materiali, presentate all'utente prima di procedere):
1. Blueprint riceve 3 campi opzionali nuovi, dedicati a city.py come cave_grid/chambers: `streets: list[Rect]` (segmenti di strada, un Rect per tratto = centro-linea + larghezza sull'asse corto), `plazas: list[Rect]` (isolati lasciati vuoti), `buildings: list[Blueprint]` (un Blueprint completo per edificio, gia tradotto in coordinate assolute della mappa). rooms/corridors restano vuoti per city, come cave_grid/chambers per gli altri stili.
2. Nuovo building_type "house" in building.py._BUILDING_TYPES: un solo piano, 1-3 stanze generiche ("stanza"), per un edificio da lotto cittadino — nessuna delle 3 tipologie esistenti (tavern/manor/warehouse) e a un piano solo, e SPEC.md non chiede una semantica specifica per gli edifici di contorno di una via.
3. assets.py: style "city" riceve "roof": "tiles" (stessa texture gia usata da tavern/manor/warehouse, presente nel catalogo). Senza, palette_for("city") da roof=None e draw_building non disegnerebbe alcun tetto (AC4 fallirebbe). Wall_load_bearing/stairs restano assenti (draw_building ricade su palette.wall se load_bearing e None; niente icona scala per un edificio a un piano).
4. Rendering: nuova compose.render_city_blueprint(level_stack, ids, blueprint, palette) — non riusa render_blueprint (quello presume rooms/corridors) ne render_sewer_blueprint: disegna le strade con add_path (AC2, texture cobblestone della stessa palette "city", larghezza = lato corto del Rect), le piazze con add_pattern (texture diversa, altro accent) + add_object al centro (palette.accents["fountain"], AC5), e per ogni blueprint.buildings chiama draw_building(level_stack, ids, building_bp, palette) — riusa building.py "a un solo piano" esattamente come richiesto, un footprint/tetto per edificio perche ogni chiamata vede un Blueprint diverso.
5. Generazione (city.py):
   - Rete stradale: partizione ricorsiva del canvas con un gap (strada) a ogni taglio — non bsp._build_tree (taglio netto, niente gap): nuova _split_with_gap(rect, rng, width) che riserva `width` quadretti fra le due meta e restituisce anche il Rect della strada. Il taglio di profondita 0 usa una via principale piu larga (AC3); i tagli successivi usano una larghezza secondaria casuale 2-4 quadretti (SPEC.md §9.4). Le foglie sono gli isolati.
   - 1-2 isolati scelti a caso come piazze (AC5), esclusi dalla suddivisione in lotti.
   - Isolati restanti: suddivisi in lotti con un'unica passata a strisce lungo il lato piu lungo dell'isolato (ogni striscia copre l'intera profondita/larghezza dell'isolato sull'asse corto): garantisce fronte strada per costruzione, perche i due lati corti di ogni striscia coincidono coi lati dell'isolato, che e sempre bordato da una strada (o dal margine esterno della mappa, trattato come bordo cittadino — nessuna strada disegnata li, annotato nel codice). Front = uno dei due lati corti (quello coerente con l'asse di taglio), usato per l'arretramento.
   - Un edificio per lotto: building.generate(width=lot_w, height=lot_h, seed derivato, building_type="house"), poi traslato (nuova funzione di traslazione per Rect/Room/Corridor/Blueprint, dato che sono frozen) dentro il lotto con margine fisso piccolo sui lati non-fronte e arretramento casuale (0-2 quadretti) sul lato fronte (AC1 "arretramento casuale dal fronte").
6. CLI: _load_generators aggiunge "city" -> generators.city; _cmd_generate riceve un ramo is_city (come is_sewer/is_cave: niente furnish/luci, che presumono blueprint.rooms — qui sono gli edifici via render_city_blueprint ad avere le loro stanze, ma furnish() lavora su un Blueprint a se, non su blueprint.buildings: lasciato fuori da questo task, coerente con building.py che non arreda i lotti gia di suo se non passato esplicitamente — riverificare se AC lo richiede, non e negli AC di TASK-35).
7. Test: tests/test_generators_city.py (riproducibilita seed, RNG locale, via principale piu larga delle secondarie AC3, ogni lotto/building rect dentro i confini dell'isolato e con lato fronte su un bordo dell'isolato AC1, 1-2 piazze presenti con elemento centrale AC5, end-to-end render_city_blueprint+validate() zero errori AC6, ispezione che le strade siano in level['paths'] non in level['patterns'] AC2, ogni edificio ha un roof AC4). tests/test_cli_generate.py: `ddforge generate city` end-to-end.
8. Nessuna modifica a bsp.py/cave.py/sewer.py. building.py riceve solo la nuova voce in _BUILDING_TYPES.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementato: model.py (Blueprint.streets/plazas/buildings), building.py (building_type 'house', un piano, 1-3 stanze generiche), assets.py (style 'city' riceve roof='tiles' e floors={'piazza':'tileset_brick_basketweave'}, entrambe le chiavi verificate presenti in data/assets.json), generators/city.py (_build_blocks partizione ricorsiva con gap=strada, via principale a depth 0 sempre piu larga per costruzione; _split_into_lots a strisce con fronte garantito; _place_building riusa building.generate con building_type='house' e trasla il Blueprint risultante nel lotto), compose.render_city_blueprint (strade via add_path con res://textures/paths/cobble.png, piazze via add_pattern+add_object fontana, un draw_building per edificio), cli.py (_load_generators + ramo is_city, coerente col pattern gia usato da cave/sewer nei rispettivi task).

Texture strada (AC2): nessun template disponibile (blank_80x80, rich_reference) contiene un elemento 'path', quindi data/assets.json['paths'] e vuoto e non c'e una chiave di catalogo da cui prenderla. Verificata cercando 'res://textures/paths/' dentro Dungeondraft.pck (installazione locale, C:/Program Files/Dungeondraft): res://textures/paths/cobble.png esiste, e' una texture BASE (non di un pack, quindi esente dal controllo DDF014 su asset_manifest), hardcoded in compose.py come scripts/demo_m1.py fa gia' per stone.png. Da confermare visivamente in Dungeondraft (TASK-36): e' un metodo di verifica diverso da quello finora usato nel progetto (osservare un campione reale esportato), documentato nel codice.

Semplificazione nota e NON risolta: l'ingresso di un edificio (building.py, bsp._ensure_entry) e' sempre sul lato sud LOCALE, indipendentemente da quale lato del lotto e' il fronte-strada. Per i lotti con front=_BOTTOM (isolati piu larghi che alti) l'ingresso combacia col fronte; per front=_RIGHT (isolati piu alti che larghi) l'ingresso resta sul lato sud del lotto, che li' e' un muro cieco fra lotti, non il fronte. Non viola nessun AC di TASK-35 (il lotto ha comunque fronte strada, l'edificio ha comunque una porta funzionante) ma incide sulla qualita' visiva: annotato nel docstring di city.py. Ruotare la geometria (Rect + Door.wall_index/t) risolverebbe ma e' stato scartato per rischio di bug di orientamento silenzioso senza un riscontro visivo di Jay (la stessa classe di difetti vista ai gate M1/M3) - proposto come follow-up, non deciso qui.

Verifica robustezza oltre agli AC: 240 combinazioni (60 seed x 4 dimensioni) generate+validate()+overlap-check senza errori ne eccezioni; canvas molto piccoli (3x3, 10x10, 20x8) degradano a citta' vuota (0 strade/piazze/edifici) senza crash. Suite completa: 467 passed, 1 skipped (+41 test nuovi per city, inclusa la sostituzione del vecchio test 'city non ancora implementato' in test_cli_generate.py, ora falso).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementato `generators/city.py`: quartieri/città a rete stradale, isolati, lotti con fronte strada garantito, un edificio per lotto e 1-2 piazze (SPEC.md §9.4). CLI wiring incluso (`ddforge generate city`), coerente col pattern già usato da cave/sewer nei rispettivi task.

**Design** (approvato prima dell'implementazione): `Blueprint` riceve 3 campi dedicati — `streets`, `plazas`, `buildings: list[Blueprint]` — stesso pattern di `cave_grid`/`chambers` per le altre varianti, invece di forzare city dentro il modello a stanze. Ogni edificio è un `Blueprint` completo prodotto da `building.generate(..., building_type="house")` (nuovo tipo a un solo piano, aggiunto a `building.py`) e poi tradotto in coordinate assolute; `compose.render_city_blueprint` chiama `draw_building` una volta per edificio, così ognuno ha il proprio footprint e il proprio tetto (AC4). Le strade sono `add_path` (AC2), le piazze `add_pattern` con una texture diversa (`floors.piazza`, riusando il meccanismo esistente di `Palette.floors`) più una fontana centrale (AC5). Lo style `city` in `assets.py` ha ricevuto un `roof` (mancava, avrebbe fatto fallire AC4).

**Fronte strada (AC1)**: garantito per costruzione, non verificato a posteriori. La rete stradale è una partizione ricorsiva del canvas che riserva un gap (strada) a ogni taglio — il taglio a profondità 0 è sempre la via principale, più larga per costruzione (`_MAIN_STREET_WIDTH=5` > range secondario `2-4`, AC3). Ogni isolato-foglia è tagliato in lotti a strisce lungo il lato più lungo: entrambi i lati corti di ogni striscia coincidono sempre con un bordo dell'isolato (strada, o il margine esterno mappa trattato come confine cittadino).

**Texture strada** — nota di trasparenza: nessun template disponibile ha mai avuto un elemento `path`, quindi `data/assets.json['paths']` è vuoto e non c'è una chiave di catalogo da cui prenderla. Verificata cercando `res://textures/paths/` dentro `Dungeondraft.pck` (installazione locale): `cobble.png` esiste come texture base (non di un pack, quindi esente da DDF014), hardcoded in `compose.py` come `stone.png` in `demo_m1.py`. Metodo di verifica diverso dal solito (ispezione dei file dell'app invece di un template esportato) — da confermare visivamente al gate umano TASK-36.

**Semplificazione nota, non risolta**: l'ingresso di ogni edificio è sempre sul lato sud *locale* (comportamento esistente di `building.py`), non ruotato per allinearsi al lato fronte del lotto quando quel lato è `_RIGHT` invece di `_BOTTOM`. Nessun AC ne risente (il lotto ha comunque fronte strada, l'edificio ha comunque una porta funzionante — verificato su tutti i seed testati), ma la porta non sempre guarda la strada. Scartata una rotazione geometrica della porta/stanza per rischio di bug di orientamento silenzioso senza un riscontro visivo di Jay; proposta come possibile follow-up.

**Verifica**: 41 test nuovi in `tests/test_generators_city.py` (riproducibilità, indipendenza dal random globale, via principale più larga per costruzione, fronte-strada per costruzione, porta d'ingresso funzionante su ogni edificio, nessuna sovrapposizione edificio/strada/piazza, 1-2 piazze con pavimento diverso e fontana, render end-to-end + `validate()` pulito) più 2 test CLI in `test_cli_generate.py`. Il vecchio test che asseriva "city non è ancora implementato" è stato sostituito (falso ora) con un test che verifica che ogni stile dichiarato nel parser sia cablato in `_load_generators`. Fuzzing aggiuntivo: 240 combinazioni seed×dimensione generate+validate()+overlap-check senza errori né eccezioni; canvas minuscoli degradano a città vuota senza crash. Suite completa: 467 passed, 1 skipped (nessuna regressione).

Nessuna modifica a `bsp.py`/`cave.py`/`sewer.py`. `building.py` ha ricevuto solo la nuova voce `_BUILDING_TYPES["house"]`.
<!-- SECTION:FINAL_SUMMARY:END -->
