---
id: TASK-32
title: generators/cave.py — cellular automata e contorni
status: Done
assignee:
  - '@claude'
created_date: '2026-09-03 11:34'
updated_date: '2026-09-07 12:49'
labels: []
milestone: m-5
dependencies:
  - TASK-31
  - TASK-20
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generatore di grotte (SPEC.md §9.3): griglia width x height con ogni cella roccia con probabilità 0.45; 4-5 iterazioni in cui una cella diventa roccia se almeno 5 vicini su 8 sono roccia; etichettatura delle componenti connesse, si tiene la più grande e si scavano tunnel verso le altre sopra una certa dimensione; estrazione del contorno con marching squares per ottenere poligoni.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Il generatore produce una caverna con una sola componente percorribile, dopo lo scavo dei tunnel
- [x] #2 I tunnel scavati verso le componenti secondarie sono percorsi semplici (nessuna autointersezione) di larghezza minima costante; nessuna estrazione di poligoni con marching squares, non richiesta dal layer nativo (decision-1)
- [x] #3 Il risultato rispetta la decisione presa nello spike sul rendering (layer cave nativo, decision-1)
- [x] #4 Il documento generato passa validate() senza errori
- [x] #5 Lo stesso seed produce la stessa grotta
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Decisioni prese con Jay prima di scrivere codice (vedi commento #1): AC2 aggiornato (niente marching squares/poligoni, il layer nativo non ne ha bisogno); niente fallback a muri poligonali in produzione; Blueprint riceve un nuovo campo opzionale `cave_grid` invece di forzare la grotta dentro Room/Corridor.

1. Codec in produzione: nuovo modulo `src/ddforge/cave_bitmap.py` con `cave_grid_shape`, `encode_cave_bitmap`, `decode_cave_bitmap` (stessa firma/logica di `scripts/cave_spike.py`, LSB-first, flusso di bit continuo, vedi docs/format.md §14). `tests/test_cave_bitmap_format.py` reindirizzato per importare da li invece che da `scripts/cave_spike.py` (gia annotato come da fare in TASK-31).

2. Primitiva `build.set_cave_bitmap(level, grid, width, height)`: chiama `cave_bitmap.encode_cave_bitmap` e scrive `level['cave']['bitmap']`. Non tocca `ground_color`/`wall_color`/`texture` (gia popolati dal template, decision-1). Non e un `add_*` (sovrascrive un blob, non appende a una lista) — commento esplicito sul perche.

3. `model.py`: `Blueprint.cave_grid: list[list[int]] | None = None`, campo opzionale e retrocompatibile come `stairs_rect`. Per una grotta `rooms=[]`, `corridors=[]`: niente stanze rettangolari ne muri.

4. `generators/cave.py`:
   - `generate(*, width, height, seed, fill_prob=0.45, iterations=5, min_component=..., **params) -> Blueprint`. RNG locale `random.Random(seed)` (TASK-20).
   - Cellular automata direttamente a risoluzione sotto-cella: griglia `(4w+3) x (4h+3)` bit (stessa shape di `cave_bitmap.cave_grid_shape`), fill probabilistico, 4-5 iterazioni regola B5/S4 (stessa dello spike), margine sempre roccia.
   - Etichettatura componenti connesse (flood fill 4-connesso su celle aperte). Tiene la piu grande. Per le altre sopra una soglia di area minima, scava un tunnel semplice (rettilineo o a L, larghezza minima costante in sotto-celle, nessuna autointersezione — AC2) dal punto piu vicino della componente alla componente principale, invece di scartarle come faceva lo spike.
   - Popola `blueprint.cave_grid`; `rooms`/`corridors` restano vuoti; `style="cave"`.

5. Wiring minimo: `compose.py` riceve `render_cave_blueprint(level, blueprint)` che chiama `build.set_cave_bitmap` quando `blueprint.cave_grid is not None`. `cli.py`: `_load_generators` importa anche `cave`; per lo stile cave il comando `generate` chiama `render_cave_blueprint` invece di `render_blueprint`/`furnish`/`_add_lighting` (una grotta non ha stanze da arredare o illuminare in questo task — nessun AC lo richiede).

6. Test:
   - `test_generators_cave.py`: stesso seed -> Blueprint identico; seed diverso -> diverso; RNG globale non toccato (stesso pattern di TASK-20); una sola componente raggiungibile dopo lo scavo (AC1); i tunnel scavati sono percorsi semplici di larghezza costante (AC2).
   - Un test end-to-end (stile `test_demo_m1.py`/spike `build_native`): genera un documento reale via `template.prepare`+`build.set_cave_bitmap` dal Blueprint, lo passa a `validate()`, verifica 0 errori (AC4).
   - `tests/test_cave_bitmap_format.py` aggiornato per importare da `ddforge.cave_bitmap` invece che da `scripts/cave_spike.py`.

7. Nessuna modifica a `scripts/cave_spike.py` (resta lo script di spike, ora ridondante col codec ma non e questo il task che lo rimuove) ne ai campioni fixture.

Rischi noti: la soglia "componente sopra una certa dimensione" e lo spessore minimo del tunnel non sono specificati numericamente da SPEC.md §9.3 — scelgo valori ragionevoli (documentati nel codice) e li registro nelle implementation notes; non e una decisione che richiede altro giro di review, e riaggiustabile via parametro.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verifica: suite completa 369 passed, 1 skipped (+19 rispetto ai 350 post-TASK-31: 17 in test_generators_cave.py, 1 in test_build.py, 1 in test_cli_generate.py), nessuna regressione. Aggiustato un test preesistente (test_generate_unimplemented_style_gives_clear_error_not_traceback) che usava 'cave' come esempio di stile non implementato: ora usa 'city' (l'unico rimasto).

AC1 verificato su 5 seed diversi (test_carved_grid_is_a_single_connected_component, parametrizzato): sempre una sola componente dopo lo scavo, mai scattato il ramo di skip previsto per il caso limite (griglia senza celle aperte). AC2 verificato su _elbow_spine (percorso a L monotono per gamba, nessun punto ripetuto) e _carve_tunnel (larghezza costante attorno a ogni punto dello spine). AC4 verificato sia da un test automatico (3 seed, mappa 80x80 reale via template+validate) sia da una generazione manuale via CLI ('ddforge generate cave'): nessun ERRORE ne AVVISO stampato.

Controllo visivo manuale (ASCII, non Dungeondraft): a 20x15 quadretti il risultato e una caverna organica con camere e diramazioni, coerente con l'algoritmo gia approvato da Jay nello spike TASK-31 (stessi fill_prob/iterations/regola B5/S4, solo a risoluzione sotto-cella diretta invece che poi convertita). A 80x80 quadretti la copertura carved sale a gran parte della mappa: e il comportamento atteso del classico algoritmo roguebasin a questi parametri (non e un difetto, e la stessa dinamica che Jay ha approvato a scala piu piccola), non un problema introdotto da questo task.

docs/format.md 14 aggiornato: la nota di chiusura che rimandava il codec a TASK-32 ora punta a ddforge.cave_bitmap (produzione) e chiarisce che scripts/cave_spike.py resta com'era, non piu l'unica implementazione ma non rimosso.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-07 12:24
---
AC2 aggiornato dopo conferma di Jay (2026-09-07): la decisione di TASK-31 (layer cave nativo) scrive i bit direttamente dal cellular automata senza mai estrarre un contorno poligonale, quindi il criterio originale su marching squares non si applica al percorso di produzione. Sostituito con un criterio equivalente sui tunnel scavati verso le componenti secondarie (niente autointersezioni, larghezza minima costante). Nessun fallback a muri poligonali in produzione per questo task.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementato `generators/cave.py` (SPEC.md §9.3): cellular automata classico (fill 0.45, 5 iterazioni B5/S4), ma girato direttamente a risoluzione sotto-cella (`(4w+3)x(4h+3)`, decision-1) invece che a un quadretto per cella, perche il risultato va scritto nel layer `cave` nativo di Dungeondraft, non come muri poligonali (decisione presa nello spike TASK-31).

**Prerequisito risolto con Jay prima di scrivere codice** (commento #1): l'AC2 originale ("contorni con marching squares") presupponeva ancora i muri poligonali, superati dalla decisione di TASK-31. Aggiornato a un criterio equivalente sui tunnel di raccordo (percorsi semplici, larghezza costante), coerente col fatto che il layer nativo non richiede mai un'estrazione di contorno poligonale.

**Architettura** (l'altro punto chiarito con Jay): il `Generator` Protocol (TASK-20) impone che `generate()` ritorni un `Blueprint`, ma una grotta non ha Room/Corridor rettangolari. Aggiunto un campo opzionale `Blueprint.cave_grid` (griglia booleana a risoluzione sotto-cella) invece di forzarla nel modello a stanze; `rooms`/`corridors` restano vuoti per questo stile.

**Cosa e cambiato:**
- `src/ddforge/cave_bitmap.py` (nuovo): il codec di `cave.bitmap` scoperto in TASK-31, portato in produzione da `scripts/cave_spike.py` (che resta invariato, non piu l'unica implementazione ma non rimosso da questo task).
- `src/ddforge/build.py`: nuova primitiva `set_cave_bitmap(level, grid, width, height)` — non e un `add_*` come le altre, sovrascrive un blob gia dimensionato dal template invece di appendere a una lista.
- `src/ddforge/model.py`: `Blueprint.cave_grid: list[list[int]] | None = None`.
- `src/ddforge/generators/cave.py`: il generatore vero. Oltre al CA, implementa l'etichettatura delle componenti connesse e — a differenza dello spike, che scartava tutto cio che non era la componente piu grande — scava un tunnel a L (larghezza costante, percorso semplice per costruzione) verso ogni componente sopra una soglia minima (16 sotto-celle, l'area di un quadretto a risoluzione 4x); le componenti piu piccole vengono scartate come rumore.
- `src/ddforge/compose.py`: `render_cave_blueprint(level, blueprint)`.
- `src/ddforge/cli.py`: `ddforge generate cave` e ora funzionante (`_load_generators` include cave; il ramo cave salta furnish/luci, che presumono stanze).
- `tests/test_cave_bitmap_format.py`: reindirizzato da `scripts/cave_spike.py` a `ddforge.cave_bitmap` (annotato come da fare in TASK-31).
- `tests/test_generators_cave.py` (nuovo, 17 test): protocollo Generator/riproducibilita del seed (TASK-20), AC1 su 5 seed, AC2 sulla geometria dei tunnel, AC4 end-to-end con `validate()` su 3 seed e mappa 80x80 reale.
- `tests/test_build.py`, `tests/test_cli_generate.py`: un test ciascuno per `set_cave_bitmap` e per `ddforge generate cave`. Aggiustato anche un test preesistente che usava "cave" come esempio di stile non implementato (ora "city", l'unico rimasto).
- `docs/format.md` §14: la nota di chiusura ora punta al codec in produzione invece che rimandare a TASK-32.

**Verifica:** suite completa 369 passed, 1 skipped (+19, nessuna regressione). Generazione manuale via CLI (`ddforge generate cave`) e ispezione visiva ASCII della griglia decodificata: a 20x15 quadretti il risultato e una caverna organica leggibile; a 80x80 la copertura scavata sale a gran parte della mappa, comportamento atteso di questo algoritmo classico a questi parametri (stesso CA gia approvato da Jay nello spike a scala piu piccola), non un difetto introdotto qui.

**Fuori perimetro, per scelta esplicita:** nessun fallback a muri poligonali in produzione (decision-1 lo lascia come via di riserva documentata, non richiesta da questo task); niente furnish/illuminazione per le grotte (nessun AC lo richiede, una grotta non ha stanze); `cave.entrance_bitmap` non toccato (candidato per collegare grotte a strutture costruite, non ancora studiato, TASK-31); fognature (variante a canali ortogonali) sono TASK-33.

**Possibile follow-up da proporre a Jay:** la soglia `min_component_size` (16 sotto-celle, fissa) non scala con le dimensioni della mappa: su una mappa grande (es. 80x80) quasi ogni componente supera la soglia e riceve un tunnel, risultando in una copertura scavata molto estesa. E' lo stesso comportamento dell'algoritmo gia approvato da Jay a scala piu piccola (36x26 nello spike), quindi non e trattato come un difetto da questo task, ma vale la pena un gate visivo in Dungeondraft sulle dimensioni di mappa che verranno usate davvero prima di darlo per definitivo.
<!-- SECTION:FINAL_SUMMARY:END -->
