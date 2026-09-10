---
id: TASK-46
title: Edifici cittadini come object da asset pack invece che geometria generata
status: Done
assignee:
  - '@claude'
created_date: '2026-09-08 08:57'
updated_date: '2026-09-10 06:30'
labels: []
milestone: m-8
dependencies:
  - TASK-35
ordinal: 46000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Gate umano M5 (TASK-36): Jay valuta che il disegno della città (generators/city.py, TASK-35) debba concentrarsi su strade e piazze, mentre gli edifici sui lotti vadano rappresentati con object (sprite) pescati da un asset pack dedicato invece che con la geometria completa (muri/tetto/stanze) oggi generata riusando building.py a un solo piano. Jay deve ancora trovare/scegliere l'asset pack di edifici da usare: questo task va ripreso solo quando l'asset pack e' disponibile, non prima.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 L'asset pack di edifici scelto da Jay e' catalogato in data/assets.json (ddforge catalog) con i suoi object/texture disponibili
- [x] #2 generators/city.py piazza un object edificio per lotto (dal nuovo asset pack) invece di disegnare un building.py completo, mantenendo fronte strada e arretramento gia' garantiti da TASK-35
- [x] #3 Il documento generato passa validate() senza errori
- [x] #4 Jay apre una città generata in Dungeondraft e conferma che il risultato e' utilizzabile al tavolo
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Confermato con Jay: il redesign tocca SOLO i preset "quartiere"/"citta" (gia' astratti, rettangolo di ingombro senza building.py). Il preset "isolato" (5 ft/quadretto, edifici giocabili con building.py) resta invariato: e' l'unico pensato per il tavolo, coerente con TASK-41.

RICERCA GIA' FATTA (formato .dungeondraft_pack verificato sul file reale di Jay, C:/Users/lorenzo_m/Documents/Dungeondraft/BB-51-Assets-Houses1.dungeondraft_pack): Godot PCK "GDPC", pack_version=1 (Godot 3.2.1), header 4+16+64 byte poi file_count(int32), poi per ogni entry: path_len(uint32)+path+offset(uint64)+size(uint64)+md5(16 byte), tutto little-endian, offset assoluti nel file. Contiene res://packs/6VxwaRdj.json (manifest id/name/author/version) e 51 texture object (33 case, 10 tetti, 2 torri, 3 tende, 1 balcone, 2 bandiere) tutte .png, dimensioni lette dall'IHDR (es. House11 131x74, House12 152x102). Verificato anche res://packs/.../pack.json duplicato identico, e sottocartelle /textures/paths/ e /textures/terrain/ non rilevanti per AC2.

PIANO:

1) AC1 - assets.py: nuova `read_dungeondraft_pack(path) -> {"manifest": {...}, "textures": {res_path: (w_px,h_px)}}` che parsa il GDPC (solo pack_version==1, altrimenti errore esplicito) e legge IHDR dei soli file .png sotto res://packs/<id>/. `build_catalog(*docs, pack_sources=())`: nuovo parametro; per ogni pack_source, se il suo manifest["id"] non e' fra i pack raccolti dai documenti --from, ValueError esplicito (vincolo non negoziabile, mai un pack orfano); altrimenti le sue texture entrano nei bucket esistenti via _classify/_slug con setdefault (i documenti restano prioritari) e le dimensioni note popolano un nuovo top-level catalog["object_sizes"]: {key: [w,h]}. cli.py: nuovo flag ripetibile `--pack <file.dungeondraft_pack>` su `catalog`, letto e passato a build_catalog.

2) AC1 - rigenerazione data/assets.json: stesso --from di TASK-45 (rich_reference + 8 file NovaMistralis su disco + 2 estratti da `git show <NovaMistralis>@fda264f`) + `--pack ".../BB-51-Assets-Houses1.dungeondraft_pack"`. Verificare determinismo (2 run identiche), nessun pack orfano, diff col catalogo attuale (solo aggiunte).

3) AC1 - assets.py Palette/palette_for: Palette guadagna `building_variants: list[tuple[str,float,float]]` (texture, w_px, h_px) e `building_colors: tuple[str,...]`. palette_for("city", ...) risolve in piu' una lista letterale delle 33 chiavi bb_houses1_house1..33 (solo le "case": tetti/torri/tende/balconi/bandiere del pack restano catalogati ma fuori scope AC2) via _lookup(objects)+nuova _lookup_size(object_sizes), e allega 5-6 tinte ARGB fisse (il pack e' "Colorable": custom_color da variare per edificio).

4) AC2 - build.py: add_object guadagna `custom_color: str | None = None` (nel dict solo se non None, stesso schema osservato in rich_reference: campo fra block_light e node_id).

5) AC2 - compose.py: NESSUNA modifica a generators/city.py (blueprint.building_footprints resta lo stesso Rect gia' garantito da _building_area/TASK-35/41: fronte strada + arretramento invariati, compose.py lo interpreta diversamente). Rimuovere draw_city_footprint; nuova draw_city_building(level, ids, footprint, palette, rng): rng.choice(palette.building_variants), scala UNICA che fa stare lo sprite nativo dentro footprint senza sbordare (min(footprint.w/(w_px/GRID), footprint.h/(h_px/GRID)), add_object ha una sola scala per asse), centrata su footprint.center(), custom_color = rng.choice(palette.building_colors). Nessun pavimento sintetico sotto (lo sprite e' gia' una casa completa vista dall'alto). render_city_blueprint guadagna un parametro obbligatorio rng: random.Random (stesso pattern esplicito di furnish/furnish_building), usato solo nel loop su building_footprints; blueprint.buildings (preset isolato) resta su draw_building, invariato. cli.py: render_city_blueprint(..., rng=random.Random(args.seed)).

6) AC3/AC4: validate() atteso pulito senza nuovi controlli (schema objects gia' validato). Generare generated/city_quartiere_task46.dungeondraft_map e generated/city_citta_task46.dungeondraft_map (stesso canvas/seed di TASK-41) e chiedere il gate umano finale a Jay; il task resta In Progress finche' non conferma (AC4).

7) Test: tests/test_assets.py (read_dungeondraft_pack su fixture minimale costruita al volo, rifiuto pack orfano, object_sizes nel catalogo CLI, palette_for("city") popola building_variants/building_colors); tests/test_build.py (add_object custom_color); tests/test_generators_city.py (le 6 chiamate a render_city_blueprint ricevono rng=random.Random(...); riscrivere test_abstract_preset_renders_and_validates_clean e test_abstract_roof_eaves_land_on_the_footprint_edges per asserzioni su objects/sprite invece di patterns/roofs); tests/test_cli_generate.py (confronti su objects invece di roofs["roofs"] per quartiere/citta). Golden tests/fixtures/golden/city_seed_1337.json (preset isolato di default) NON dovrebbe cambiare: building_footprints e' vuoto per isolato, il nuovo codice non viene mai eseguito su quel path - verificare che passi senza rigenerarlo.

8) Documentazione: docs/format.md nuova sezione con provenienza pack (comando, id/nome/autore, formato GDPC verificato), schema catalog["object_sizes"], nota custom_color nello schema objects; skill/references/styles.md e README aggiornati per dire che quartiere/citta usano ora sprite del pack invece di rettangoli/tetti astratti.

Rischio principale: AC4 e' un gate umano, non automatizzabile - il task resta aperto dopo l'implementazione finche' Jay non apre i file e conferma.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Ripreso il lavoro gia' implementato in una sessione precedente (codice, catalogo, test tutti gia' scritti e nel working tree non committato): verificata l'implementazione completa contro il piano registrato (punti 1-7) confrontando i diff di assets.py/build.py/compose.py/cli.py/data/assets.json/tests con il piano. Tutto presente e coerente: read_dungeondraft_pack (GDPC), build_catalog(pack_sources=...) col vincolo pack-orfano, Palette.building_variants/building_colors, add_object(custom_color=...), compose.draw_city_building/_fit_scale, render_city_blueprint(..., rng=...), cli --pack.

VERIFICA OGGETTIVA eseguita in questa sessione (non solo lettura del codice):
- Suite completa: `pytest -q` -> 633 passed, 1 skipped, 0 regressioni (316s). Rieseguiti anche solo i 4 file toccati da TASK-46 (test_assets/test_build/test_generators_city/test_cli_generate): 256 passed.
- `data/assets.json` rigenerato: 51 pack (invariato), objects 59->106 (+47 texture del pack 6VxwaRdj non ancora osservate in un documento reale), paths 0->6 (prima volta che questa categoria si popola: il pack contiene 6 texture strada/fiume/costa, mai viste in un .dungeondraft_map reale di Jay), object_sizes nuovo campo con 57 voci (51 object + 6 paths del pack). Nessun pack orfano, nessuna chiave preesistente rimossa.
- Golden file tests/fixtures/golden/city_seed_1337.json (preset isolato) verificato NON modificato (git status pulito su tests/fixtures/golden/): conferma che il preset isolato e' byte-per-byte invariato, come atteso (building_footprints e' vuoto per isolato, il nuovo codice non viene mai eseguito su quel path).
- generated/city_quartiere_task46.dungeondraft_map e generated/city_citta_task46.dungeondraft_map (gia' presenti dalla sessione precedente, non versionati per .gitignore) validati con `ddforge validate`: 'Nessun problema trovato' su entrambi (AC3). Ispezionati a mano: quartiere 322 edifici/324 objects totali, citta 3.325/3.327 - stessi conteggi di TASK-41 (la rete stradale non e' cambiata), roofs=0/walls=0 su entrambi (nessun tetto/pavimento sintetico residuo), 6 tinte custom_color osservate su entrambi i file (palette.building_colors applicata). Dimensioni: quartiere 1,92 MB (~768 B/edificio, era 2,09 MB/~1,3 KB con l'ingombro astratto), citta 3,71 MB (~613 B/edificio, era 5,44 MB/~1,1 KB) - piu leggeri di prima, uno sprite costa meno di pattern+roof.

COMPLETATO IN QUESTA SESSIONE (mancava dal piano, punto 8): documentazione.
- docs/format.md: nuova sezione 10.2 (provenienza TASK-46 - formato GDPC verificato, comando ddforge catalog --pack, risultato numerico, vincolo pack-orfano invariato, Palette.building_variants/building_colors, formula di scala _fit_scale); nota su custom_color aggiunta allo schema object di SS5.
- README.md: riga 'Cos'e un edificio' e 'Dimensione del file' della tabella preset aggiornate ai nuovi numeri/comportamento (sprite invece di ingombro astratto), aggiunta nota esplicita che solo 'isolato' e' giocabile al tavolo.
- skill/references/styles.md: stessa riga tabella aggiornata, aggiunto un paragrafo che spiega perche' quartiere/citta' usano sprite da TASK-46.

AC1/AC2/AC3 spuntate su questa base (catalogo esteso e verificato, piazzamento sprite verificato su file reali + test, validate() pulito su entrambi i preset). AC4 resta APERTA: e' un gate umano (Jay deve aprire generated/city_quartiere_task46.dungeondraft_map e generated/city_citta_task46.dungeondraft_map in Dungeondraft e confermare che il risultato si legge come mappa di citta dall'alto). Task lasciato In Progress in attesa della sua risposta.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-08 09:54
---
Pack scelto per gli edifici cittadini: 6VxwaRdj "BB 51 Assets Houses1" (BluBerrey). Gia' catalogato in via preliminare in TASK-45 (2 object: BB_Houses1_House11.png, BB_Houses1_House12.png, disegnati in templates/rich_reference.dungeondraft_map). Riprendere questo task quando TASK-45 e' chiuso e data/assets.json committato con questo pack.
---

author: @claude
created: 2026-09-08 13:12
---
Decisioni/domande aperte spostate qui da TASK-36 (Jay: 'voglio modificare tutta la gestione della città nel task 46, chiudi TASK-36 con solo le cose relative alle grotte').

Dal gate umano round 1 di TASK-36 (file generated/city_task35.dungeondraft_map / city_m5.dungeondraft_map, mai confermato da Jay — sostituito qui dal redesign):

1. Nota già in TASK-35 (implementation notes): l'ingresso di ogni edificio è sempre sul lato sud LOCALE del lotto (comportamento di building.py, mai corretto), indipendentemente da quale lato del lotto è il fronte-strada. Per i lotti con fronte diverso da 'sud', l'ingresso non guarda la strada. Con la nuova gestione a object da asset pack (questo task) il problema potrebbe sparire da solo (un object piazzato non ha un 'ingresso' nello stesso senso) — da verificare quando si progetta il piazzamento.

2. Domanda mai risposta da Jay: isolati/strade/piazze (la parte che TASK-46 vuole mantenere procedurale) si leggono bene così come generate da TASK-35? Se il redesign tocca anche la rete stradale, vale la pena chiedere di nuovo con un file aggiornato una volta scelto l'asset pack.
---

author: @claude
created: 2026-09-08 14:16
---
Ricerca fatta il 2026-09-08 prima di sospendere il task: Jay ha chiesto di implementare TASK-41 (preset di scala) PRIMA di questo.

MISURE REALI sul pack scelto (6VxwaRdj 'BB 51 Assets Houses1'), estratte dal file C:/Users/lorenzo_m/Documents/Dungeondraft/BB-51-Assets-Houses1.dungeondraft_pack (formato Godot PCK 'GDPC', letto con uno script di parsing; header IHDR dei PNG per le dimensioni):
- 51 texture object: 33 case, 10 tetti, 2 torri, 3 tende, 1 balcone, 2 bandiere.
- Le case vanno da 51x45 px a 248x205 px, cioe 0,20-0,97 quadretti a scala 1 (256 px/quadretto). Sono sprite da mappa di citta vista dall'alto, NON dalla scala giocabile 5 ft.
- Il pack e taggato 'Colorable': ogni object di questo pack piazzato da Dungeondraft porta il campo custom_color, sempre 'ff6b3834' nei 7 campioni colorabili di templates/rich_reference.dungeondraft_map (e il default del programma). Gli object non colorabili non hanno affatto il campo. Variare custom_color per edificio e il modo naturale di dare varieta ai tetti.

CONSEGUENZA SULLA SCALA: un lotto di TASK-35 e largo 8-16 quadretti; riempirlo con uno di questi sprite richiede scala ~15-20x (152 px stirati a ~2800). Mockup mostrati a Jay (render PIL, non output Dungeondraft): a scala citta ricalibrata (strade 1,5-3 q, lotti ~2,6 q, sprite 1-2x) un canvas 80x80 tiene ~230 edifici nitidi; con i lotti di TASK-35 lo sprite ingrandito e visibilmente sgranato da vicino. Per questo Jay ha chiesto TASK-41 prima: la scelta della scala va fatta come preset, non dentro questo task.

DECISIONE PRESA DA JAY su AC1 (catalogo): estendere 'ddforge catalog' a leggere direttamente i file .dungeondraft_pack, cosi entrano tutte e 51 le texture del pack piu le loro dimensioni in pixel (indispensabili per calcolare la scala di piazzamento e non ricavabili da un .dungeondraft_map, che non le contiene). Vincolo non negoziabile da mantenere: rifiutare le texture di un pack assente da header.asset_manifest del template. Oggi in data/assets.json ci sono solo 3 case (House10/House12/House28) piu Roof7, le uniche disegnate da Jay in rich_reference.
---

author: @claude
created: 2026-09-08 14:22
---
Vincolo di design da tenere presente per tutto il redesign di questo task (Jay, 2026-09-08): le mappe generate in modalita citta NON sono pensate per essere giocate/giocabili al tavolo in scala 5 ft come le mappe dungeon/grotta. Sono mappe di citta viste dall'alto (bird's-eye/top-down), uno sfondo/riferimento visivo — non serve un layout tattico con ingressi, arretramenti o dettagli utilizzabili in combattimento. Questo vincolo va tenuto presente nel piazzamento degli object edificio (AC2) e nella verifica finale con Jay (AC4): 'utilizzabile al tavolo' va inteso come 'leggibile come mappa di citta dall'alto', non come 'giocabile'.
---

created: 2026-09-10 06:30
---
GATE UMANO FINALE - Jay ha aperto generated/city_quartiere_task46.dungeondraft_map e generated/city_citta_task46.dungeondraft_map in Dungeondraft e confermato: 'si, i due file mi vanno bene'. AC4 spuntata su questa base.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Edifici cittadini dei preset \"quartiere\"/\"citta\" (generators/city.py) sostituiti da uno sprite `object` del pack scelto da Jay (6VxwaRdj, \"BB 51 Assets Houses1\", 33 varianti \"casa\") invece della geometria astratta (pavimento+tetto a colmo) di TASK-41. Il preset \"isolato\" (5 ft/quadretto, giocabile al tavolo con building.py) resta invariato: solo quartiere/citta sono mappe viste dall'alto, coerente col vincolo di design di Jay (non pensate per essere giocate in scala 5 ft).

**AC1 (catalogo)**: `ddforge catalog` estesa a leggere direttamente i file `.dungeondraft_pack` (nuova `assets.read_dungeondraft_pack`, formato Godot PCK \"GDPC\" verificato sul file reale di Jay), oltre ai `.dungeondraft_map` gia supportati. Nuovo flag ripetibile `--pack`. `build_catalog(*docs, pack_sources=...)` mantiene il vincolo non negoziabile gia in vigore per i documenti: una texture di un pack assente da `header.asset_manifest` viene rifiutata con errore esplicito, mai inclusa in silenzio. Le texture del pack popolano i bucket esistenti piu un nuovo campo top-level `object_sizes: {key: [w_px, h_px]}` (dimensioni pixel, non ricavabili da un `.dungeondraft_map`, indispensabili per calcolare la scala di piazzamento). `data/assets.json` rigenerato: 51 pack (invariato), objects 59->106, paths 0->6 (prima volta popolata), object_sizes 57 voci; nessun pack orfano, nessuna chiave preesistente rimossa.

**AC2 (piazzamento)**: `Palette` guadagna `building_variants` (le 33 texture \"casa\", chiavi letterali per evitare l'ambiguita degli alias su substring gia vista in TASK-45) e `building_colors` (6 tinte ARGB fisse, il pack e \"Colorable\"). `add_object` guadagna `custom_color` opzionale (omesso, non `null`, quando assente). Nuova `compose.draw_city_building` + `_fit_scale`: sceglie una variante e un colore a caso per lotto, calcola la scala uniforme che fa stare lo sprite nativo dentro il footprint del lotto senza sbordare (preservando fronte strada e arretramento gia garantiti da TASK-35/41, mai ricalcolati), lo centra. Sostituisce interamente la vecchia `draw_city_footprint` (pavimento+tetto sintetico): niente muri/pavimenti/tetti residui sui preset astratti, solo lo sprite. `render_city_blueprint` riceve un `rng` esplicito per la scelta di variante/colore.

**AC3 (validate pulito)**: verificato sia via test automatici sia sui due file reali generati (`ddforge validate`: \"Nessun problema trovato\" su entrambi).

**AC4 (gate umano)**: Jay ha aperto entrambi i file in Dungeondraft e confermato che il risultato va bene.

**Effetto collaterale positivo**: gli edifici sprite pesano meno della vecchia geometria astratta (quartiere ~768 B/edificio contro ~1,3 KB, citta ~613 B contro ~1,1 KB) - un pattern+roof per edificio costava piu di un singolo object.

**Verifica**: suite completa 633 passed, 1 skipped, zero regressioni. Golden file del preset isolato (`tests/fixtures/golden/city_seed_1337.json`) verificato byte-per-byte invariato (building_footprints e vuoto per isolato, il nuovo codice non viene mai eseguito su quel path). Nuovi test in tests/test_assets.py (read_dungeondraft_pack su fixture PCK costruita al volo, rifiuto pack orfano, CLI --pack, Palette.building_variants/colors), tests/test_build.py (custom_color), tests/test_generators_city.py e tests/test_cli_generate.py (riscritti per asserire su object/sprite invece di pattern/roof sintetici).

**Documentazione**: docs/format.md (nuova sezione 10.2 con provenienza/formato GDPC/comando/risultato, nota custom_color nello schema object), README.md e skill/references/styles.md (tabella preset aggiornata, nota che solo \"isolato\" e giocabile al tavolo).

Nessuna modifica al preset \"isolato\" ne a generators/city.py: blueprint.building_footprints resta lo stesso Rect di prima, solo l'interpretazione in compose.py e cambiata.
<!-- SECTION:FINAL_SUMMARY:END -->
