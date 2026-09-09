---
id: TASK-47
title: Il tetto di draw_building sborda 2 quadretti oltre l edificio
status: Done
assignee:
  - '@claude'
created_date: '2026-09-08 14:57'
updated_date: '2026-09-09 13:19'
labels: []
dependencies: []
documentation:
  - docs/format.md
type: bug
ordinal: 47000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TASK-41 ha verificato su un file scritto da Dungeondraft (dungeondraft_maps/crosshead_style/tresendar_manor_full.dungeondraft_map, 11 roof su un livello dedicato e i muri su un altro) che in un elemento roof il campo points e la linea di COLMO e il campo width e la MEZZA larghezza, cioe la distanza dal colmo alla gronda, non la larghezza totale: il colmo verticale a x=2560 con width 768 ha i muri delledificio a x=1790,5 e x=3325,9 (2560 -/+ 768) e quello a x=5632 con la stessa width ha il muro a x=4864. Prova e tabella in docs/format.md sezione 5.

compose.draw_building (TASK-27) passa invece al tetto i 4 vertici del footprint come poligono chiuso, con la width di default 512 px. Con la semantica appena verificata, quel tetto si estende quindi 2 quadretti oltre il perimetro delledificio su ogni lato: su una mappa cittadina (generators/city.py, preset quartiere) significa tetti che coprono la strada e si sovrappongono fra edifici vicini.

Non e stato corretto in TASK-41 di proposito: gli edifici di draw_building sono lo stesso output che Jay ha approvato al gate umano M4 (TASK-30) e al gate M3 dopo tre round di correzioni. Cambiare la geometria del tetto senza un nuovo riscontro visivo di Jay rischia di peggiorare un risultato gia validato, ed e esattamente la classe di rischio (bug di orientamento/geometria silenzioso) che il progetto ha imparato a non prendere. Serve quindi un giro di verifica visiva dedicato.

Il preset citta di city.py non e interessato: compose.draw_city_footprint usa gia la linea di colmo con width = meta del lato corto, e ha un test che verifica che le gronde cadano sui bordi del footprint.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 La geometria del tetto prodotto da draw_building e coerente con la semantica verificata di roof.points/roof.width: il tetto copre il footprint dell edificio senza sbordare oltre il perimetro
- [x] #2 Su una mappa cittadina generata con --scale quartiere nessun tetto si sovrappone a una strada o al tetto di un edificio vicino
- [x] #3 Jay apre in Dungeondraft un edificio singolo (uno dei tre di building_m4) e una citta a scala quartiere e conferma che i tetti si leggono meglio di prima, non peggio
- [x] #4 I golden file che contengono tetti sono rigenerati e il diff e verificato a mano
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. compose.draw_building: sostituire il tetto a poligono chiuso (add_roof con
   footprint_corners e width di default) con add_ridge_roof(level, ids,
   footprint, palette) sull'ultimo piano, come gia fa add_ridge_roof per i
   preset di city.py. Aggiornare i docstring di draw_building/add_ridge_roof
   che descrivono il difetto come ancora presente sull'edificio singolo.
2. Aggiungere un test in tests/test_draw_building.py, modellato su
   test_isolato_roofs_do_not_overhang_the_building (tests/test_generators_city.py):
   il tetto di un edificio generato da building.generate() deve avere 2 punti
   (colmo, non poligono chiuso) e le gronde non devono sborda oltre il
   footprint.
3. Rigenerare tests/fixtures/golden/building_tavern_seed_1337.json con lo
   script indicato in test_building_integration.py (_generate_full_document,
   seed 1337) e verificare a mano che l'unico diff sia la geometria del tetto
   (roofs[0].points passa da 4 punti chiusi a 2, width cambia).
4. Aggiornare docs/format.md §5 (sezione roof): il tetto a poligono di
   draw_building non esiste piu, entrambi i percorsi (edificio singolo e
   city.py) usano ora add_ridge_roof.
5. Girare la suite di test completa (pytest) e verificare che nessun altro
   golden/test dipenda dalla vecchia geometria.
6. AC3 (riscontro visivo di Jay su un edificio building_m4 e una citta a
   scala quartiere) e un gate umano: non posso chiuderlo da solo. Genero i
   file .dungeondraft_map aggiornati e segnalo a Jay che sono pronti per
   l'apertura in Dungeondraft, poi mi fermo prima di spuntare AC3/AC4 e
   passare lo stato a Done (vedi task-finalization).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementato: compose.draw_building ora disegna il tetto dell'ultimo piano
con add_ridge_roof (colmo + mezza larghezza) invece del vecchio poligono
chiuso a width di default; docstring di draw_building/add_ridge_roof e
docs/format.md §5 aggiornati per riflettere che il difetto non c'e' piu'.
render_city_blueprint resta invariato (roof=False + add_ridge_roof
esplicito): produce lo stesso identico tetto, non l'ho toccato per non
allargare lo scope.

Test: nuovo tests/test_draw_building.py::test_roof_does_not_overhang_the_building
(colmo a 2 punti, gronde sul perimetro), modellato sull'analogo test lato
citta' gia' esistente (test_isolato_roofs_do_not_overhang_the_building, che
copre AC2 e continua a passare col nuovo nome "isolato" post rename di
TASK-41 round 2). Suite completa: 617 test, 1 skip, 0 fail dopo la
rigenerazione del golden.

Golden rigenerato: tests/fixtures/golden/building_tavern_seed_1337.json.
Diff verificato a mano (vedi sotto) — unico cambiamento i due campi del
tetto, points da poligono chiuso a 8 valori (4 vertici) a linea di colmo a 4
valori (2 punti), width da 512 a 1536:
  -  "points": "PoolVector2Array( 256, 256, 4352, 256, 4352, 3328, 256, 3328 )",
  +  "points": "PoolVector2Array( 256, 1792, 4352, 1792 )",
  -  "width": 512,
  +  "width": 1536,
Nessun altro campo del documento e' cambiato.

File pronti per il riscontro visivo di Jay (AC3), rigenerati con lo stesso
comando CLI usato per i golden esistenti in generated/ (cartella
gitignored): generated/building_m4_tavern_task47.dungeondraft_map (taverna,
seed 1337, style tavern) e generated/city_isolato_task47.dungeondraft_map
(preset --scale isolato, seed 1337, style city). Entrambi passano
`ddforge validate` (la taverna con l'unico avviso DDF102 gia' noto e non
correlato, vedi docs/format.md §9.5).

Nota sull'AC3 come scritta: cita "una citta a scala quartiere", ma dopo il
rename di TASK-41 round 2 (vedi commento #2) il preset con edifici a pianta
completa — quello davvero interessato da questo bug — si chiama ora
"isolato"; "quartiere" e' l'astrazione 1 quadretto = 1 edificio (mai
esposta al difetto, usa gia' add_ridge_roof da prima di questo task). Ho
generato city_isolato_task47 di conseguenza.

AC3 confermato da Jay (2026-09-09): riscontro visivo sui file generated/building_m4_tavern_task47.dungeondraft_map e generated/city_isolato_task47.dungeondraft_map ok.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-09 08:06
---
Aggiornamento da TASK-41 round 2: le mappe cittadine NON sono piu esposte a questo difetto, quindi il perimetro di questo task si e ristretto all'edificio singolo.

Perche e stato affrontato la: al round 2 del gate Jay ha chiesto case grandi la meta, e a quel punto lo sbordo di 2 quadretti per lato e diventato il difetto dominante invece di un dettaglio - su una casa da 5x5 quadretti il tetto risultava 9x9, arrivava in mezzo alla strada e si sovrapponeva a quello del vicino. Verificato renderizzando i tetti come fascia centrata sul perimetro (l'unico modo di vederlo: riempiendo il poligono lo sbordo non si nota).

Correzione applicata, a raggio minimo: draw_building ha ora un parametro roof=True/False, e compose.render_city_blueprint lo chiama con roof=False disegnando il tetto con la nuova compose.add_ridge_roof (linea di colmo, width = meta del lato corto, gronde esattamente sui bordi del footprint). L'output di 'ddforge generate building' e rimasto identico - nessun golden di building rigenerato - proprio per non cambiare in silenzio un risultato approvato al gate M4.

Resta da fare qui: far usare il tetto giusto anche all'edificio singolo, con il riscontro visivo di Jay che gli AC di questo task chiedono. Un test dedicato esiste gia sul lato citta (test_quartiere_roofs_do_not_overhang_the_building in tests/test_generators_city.py) e puo servire da modello. Documentazione: docs/format.md 5 ora descrive entrambi i tetti e perche sono diversi.
---

author: @claude
created: 2026-09-09 10:05
---
Nota di rinomina da TASK-41 round 2 del gate: il preset di scala di generators/city.py che questo task chiama "quartiere" (edifici a pianta completa) e' stato rinominato "isolato" - "quartiere" ora indica il preset astratto 1 quadretto = 1 edificio (ex "citta"), e "citta" e' un nuovo terzo preset piu denso. Il test citato come modello, test_quartiere_roofs_do_not_overhang_the_building, si chiama ora test_isolato_roofs_do_not_overhang_the_building in tests/test_generators_city.py. Nessun impatto sull'AC di questo task (riguarda solo l'edificio singolo/building.py), solo sui nomi da usare quando lo si riprende.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
draw_building disegna ora il tetto con add_ridge_roof (colmo + mezza larghezza) invece del poligono chiuso a width di default, che sbordava 2 quadretti per lato sull'edificio singolo. Verificato con nuovo test tests/test_draw_building.py::test_roof_does_not_overhang_the_building, golden building_tavern_seed_1337.json rigenerato (diff verificato a mano: solo points/width del tetto), suite completa verde (617 test), e riscontro visivo di Jay sui file generati in generated/.
<!-- SECTION:FINAL_SUMMARY:END -->
