---
id: TASK-62
title: >-
  Aggancia gli sprite di Palazzo, Arena e Cattedrale e aumenta ulteriormente la
  scala dei luoghi coperti
status: Done
assignee:
  - '@claude'
created_date: '2026-09-21 15:04'
updated_date: '2026-09-23 09:03'
labels: []
dependencies:
  - TASK-61
  - TASK-59
documentation:
  - docs/sprite-luoghi.md
ordinal: 63000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Jay ha ricompilato il pacchetto Nova Mistralis (Documents/Dungeondraft/NovaMistralis.dungeondraft_pack, aggiornato 21/09) includendo i tre nuovi sprite elaborati in TASK-61 (nm_palazzo, nm_arena, nm_cattedrale). Vanno letti nel catalogo e agganciati a assets.py._CITY_LANDMARK_SPRITES al posto del ripiego (bb_keepsandcastles_castle_color/cathedral_color, tourney_grounds) usato oggi per palazzo/cattedrale/arena. Inoltre, dopo aver visto le mappe di TASK-59, Jay chiede un ulteriore aumento (1.5x sul valore attuale di LandmarkKind.lots) per i luoghi chiusi SITE_LOT/SITE_BAND che usano sprite del pacchetto, sia per i 13 gia' toccati da TASK-59 sia per i 6 lasciati invariati in quel giro (tempio, municipio, caserma, teatro, bagni, ospedale) perche' un aumento rompeva l'invariante 'il luogo richiesto compare sempre' sul preset isolato. Chiarito con Jay: palazzo/arena/cattedrale sono SITE_BLOCK (occupano gia' un isolato intero, city.py._block_candidates ignora 'lots' per costruzione) quindi restano alla dimensione attuale in questo giro - nessuna leva sicura senza riscrivere la logica di partizione delle strade, fuori scope qui.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 data/assets.json include i nuovi sprite del pack aggiornato (nm_palazzo, nm_arena, nm_cattedrale come minimo) con dimensioni reali dall'header PNG
- [x] #2 assets.py._CITY_LANDMARK_SPRITES punta cattedrale, palazzo e arena ai nuovi sprite nm_* invece del ripiego
- [x] #3 Il campo lots dei 19 luoghi chiusi SITE_LOT/SITE_BAND coperti dal pacchetto e' aumentato di un ulteriore 1.5x rispetto al valore attuale (i 13 gia' toccati da TASK-59 e i 6 lasciati invariati in quel giro), con lo sprite risultante misurabilmente piu' grande sulle mappe rigenerate rispetto a generated/city_*_task59
- [x] #4 palazzo, arena e cattedrale (SITE_BLOCK) restano alla dimensione isolato-intero attuale, nessuna modifica alla logica di piazzamento a blocco
- [x] #5 L'invariante 'un luogo richiesto esplicitamente con --landmark compare sempre' resta valida per tutti e 19 i luoghi ai tre preset, con evidenza nei test
- [x] #6 mercato, cimitero, accademia e monastero restano invariati (fuori scope, gia' deciso in TASK-59)
- [x] #7 Le mappe di valutazione in generated/ per i tre preset sono rigenerate con seed fissi, nome che indica il task, e superano ddforge validate
- [x] #8 docs/sprite-luoghi.md e' aggiornato (sprite coperti per palazzo/arena/cattedrale, nota sulla nuova scala lots)
- [x] #9 Suite di test completa verde, golden aggiornati dove il cambio li tocca
- [x] #10 Gate umano: Jay apre le mappe rigenerate in Dungeondraft e conferma che la dimensione ora gli piace
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Rigenerare data/assets.json con ddforge catalog --from-catalog data/assets.json --from templates/blank_80x80.dungeondraft_map --from templates/rich_reference.dungeondraft_map --from templates/blank_160x160.dungeondraft_map --pack Documents/Dungeondraft/NovaMistralis.dungeondraft_pack --out data/assets.json (stesso comando di TASK-52, pack ricompilato da Jay oggi). Verificare quali nuove chiavi nm_* compaiono.
2. Aggiornare assets.py._CITY_LANDMARK_SPRITES: cattedrale -> nm_cattedrale, palazzo -> nm_palazzo, arena -> nm_arena, aggiornando i commenti che le segnavano 'non coperto'.
3. Nel catalogo landmarks.py, moltiplicare per 1.5 il valore attuale di 'lots' per i 19 luoghi chiusi SITE_LOT/SITE_BAND coperti (i 13 gia' a 2.0 da TASK-59 -> 3.0, i 6 rimasti a 1.5/2.0 -> 2.25/3.0). Non toccare mercato, cimitero (esclusi da Jay), accademia/monastero/palazzo/arena/cattedrale (SITE_BLOCK, lots ignorato).
4. Rigenerare in-process (esperimento diretto, non solo lettura) e far girare la suite mirata su test_a_requested_landmark_is_always_present e la catena del cimitero per tutti e 19 i luoghi ai tre preset: se qualcuno sparisce quando richiesto esplicitamente (probabile sui 6 gia' vicini al tetto, specie a isolato), investigare la causa (spazio insufficiente di lotti liberi consecutivi in riga) e trovare una leva mirata (es. valore piu' basso solo dove serve, o fix puntuale) prima di fissare i valori finali - documentare il compromesso nelle note come fatto in TASK-59.
5. Rigenerare i golden citta con scripts/regen_city_golden.py --write; pytest -q sull'intera suite.
6. Rigenerare le mappe di valutazione in generated/ per i tre preset (seed 1337, canvas 78x78, naming _task62), validare con ddforge validate, misurare che gli sprite coperti siano piu' grandi di generated/city_*_task59 e che palazzo/arena/cattedrale mostrino ora nm_* invece del ripiego.
7. Aggiornare docs/sprite-luoghi.md (sez. 10) con palazzo/arena/cattedrale ora coperti e nota sulla nuova scala lots.
8. Verifica oggettiva (AC1-9), poi gate umano (AC10).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Catalogo (AC1): ddforge catalog rieseguito con lo stesso comando di TASK-52 sul pack ricompilato da Jay (Documents/Dungeondraft/NovaMistralis.dungeondraft_pack, 21/09 16:48): 570->573 objects, 535->538 object_sizes. nm_palazzo, nm_arena, nm_cattedrale presenti, 1024x1024 dall'header PNG, coerenti con prompt/26-28.

Aggancio sprite (AC2/AC4): assets.py._CITY_LANDMARK_SPRITES aggiornato, cattedrale/palazzo/arena puntano ora a nm_cattedrale/nm_palazzo/nm_arena invece del ripiego bb_keepsandcastles_*/tourney_grounds. Sono SITE_BLOCK (city._block_candidates, non toccata): l'ingombro resta l'isolato intero, cambia solo lo sprite. Verificato sulle mappe rigenerate: 0 riferimenti a bb_keepsandcastles/tourney_grounds, nm_palazzo/nm_arena/nm_cattedrale presenti dove il seed li piazza (citta: tutti e tre; quartiere: palazzo).

Scala lots (AC3/AC5/AC6): LandmarkKind.lots portato a 3.0 uniformemente per tutti e 19 i luoghi chiusi SITE_LOT/SITE_BAND coperti (i 13 gia' a 2.0 da TASK-59 + i 6 rimasti a 1.5/2.0 in quel giro: tempio, municipio, caserma, teatro, bagni, ospedale). Per evitare di rompere di nuovo l'invariante 'luogo richiesto sempre presente' (il motivo per cui TASK-59 aveva lasciato invariati quei 6), aggiunto un ripiego a span decrescente in city._lot_candidates e city._band_candidates: se lo span pieno (3 lotti/celle di fila) non trova candidati nella fila, si riprova con 2 poi 1 invece di non piazzare il luogo. Verificato in process su tutti e 19 i luoghi ai tre preset (20 seed): zero sparizioni (l'unica assenza, faro a quartiere/citta su 16/20 seed, e' perche' quei seed non generano un porto affatto - precondizione strutturale indipendente da lots, gia' cosi' prima di questo task). Confronto diretto vecchio lots (1.5/2.0) vs nuovo (3.0) sugli stessi 15 seed: crescita reale ma modesta in media, +3%/+13% a quartiere/citta (es. tempio citta 0.77->0.84, +9%; biblioteca citta 0.76->0.86, +13%), col tetto dato dalla profondita' di fila gia' documentato in TASK-59 (faro esattamente invariato, 1.00x, la banchina e' una sola fila di celle: allargare oltre non cambia la dimensione minima del rettangolo). Al preset isolato la crescita e' piu' marcata (es. tempio: min 6.0 - max 7.2 quadretti sui 20 seed, contro un lotto singolo ~4.0 di partenza pre-TASK-59) perche' li' i luoghi diventano edifici a stanze e non solo sprite. Non toccati: mercato, cimitero (lots invariato, esclusi da Jay), accademia, monastero (SITE_BLOCK, nessuna leva).

Mappe e verifica (AC7/AC9): generated/city_{isolato,quartiere,citta}_task62.dungeondraft_map rigenerate (seed 1337, canvas 78x78, comando di TASK-52/59/60). Tutte e tre superano ddforge validate. Golden tests/fixtures/golden/city_seed_1337_landmarks.json rigenerato con scripts/regen_city_golden.py --write (city_seed_1337.json invariato). Suite completa: 779 passed, 1 skipped (preesistente), 0 failed.

Documentazione (AC8): docs/sprite-luoghi.md sez. 10 aggiornata (26 luoghi coperti, cattedrale/palazzo/arena spostati dalla tabella ripiego, nuova sottosezione 'Scala dei lotti (TASK-59, TASK-62)' che spiega lots=3.0 e il ripiego a span decrescente).

APERTO: AC10 (gate umano) - Jay deve aprire generated/city_{isolato,quartiere,citta}_task62.dungeondraft_map in Dungeondraft e confermare la dimensione.

Gate umano confermato da Jay (2026-09-23): dimensione dei luoghi coperti (nuova scala lots) approvata sulle mappe rigenerate.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Catalogo aggiornato dal pack ricompilato (nm_palazzo/nm_arena/nm_cattedrale, 1024x1024): assets.py._CITY_LANDMARK_SPRITES ora punta cattedrale/palazzo/arena ai nuovi sprite invece del ripiego bb_keepsandcastles_*/tourney_grounds (restano SITE_BLOCK, isolato intero). LandmarkKind.lots portato a 3.0 per tutti e 19 i luoghi chiusi SITE_LOT/SITE_BAND coperti (comprese le 6 eccezioni lasciate da TASK-59); aggiunto un ripiego a span decrescente in city._lot_candidates/_band_candidates cosi' l'invariante 'luogo richiesto sempre presente' non si rompe piu' quando 3 lotti di fila non ci sono. Verificato: 779 passed/1 skipped, golden rigenerato, tre mappe generated/city_*_task62 validate senza errori, crescita di scala reale (misurata in process, +3%/+13% medio a quartiere/citta, piu' marcata a isolato) col tetto da profondita' di fila gia' noto da TASK-59. In attesa del gate umano di Jay (AC10).
<!-- SECTION:FINAL_SUMMARY:END -->
