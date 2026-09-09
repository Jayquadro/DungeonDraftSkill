---
id: TASK-47
title: Il tetto di draw_building sborda 2 quadretti oltre l edificio
status: To Do
assignee: []
created_date: '2026-09-08 14:57'
updated_date: '2026-09-09 10:05'
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
- [ ] #1 La geometria del tetto prodotto da draw_building e coerente con la semantica verificata di roof.points/roof.width: il tetto copre il footprint dell edificio senza sbordare oltre il perimetro
- [ ] #2 Su una mappa cittadina generata con --scale quartiere nessun tetto si sovrappone a una strada o al tetto di un edificio vicino
- [ ] #3 Jay apre in Dungeondraft un edificio singolo (uno dei tre di building_m4) e una citta a scala quartiere e conferma che i tetti si leggono meglio di prima, non peggio
- [ ] #4 I golden file che contengono tetti sono rigenerati e il diff e verificato a mano
<!-- AC:END -->

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
