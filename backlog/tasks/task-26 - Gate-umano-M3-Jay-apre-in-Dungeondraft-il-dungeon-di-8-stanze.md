---
id: TASK-26
title: 'Gate umano M3: Jay apre in Dungeondraft il dungeon di 8 stanze'
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:32'
updated_date: '2026-09-04 14:06'
labels: []
milestone: m-3
dependencies:
  - TASK-25
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Secondo e ultimo passaggio manuale obbligatorio (SPEC.md §5). Genera un dungeon di 8 stanze validato, poi fermati e chiedi esplicitamente a Jay di aprirlo in Dungeondraft indicando cosa controllare. Le correzioni di orientamento e allineamento emerse qui vanno codificate, non solo documentate.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A Jay è chiesto esplicitamente di verificare: tutte le stanze sono raggiungibili, le porte sono orientate bene, i pavimenti non sbordano
- [x] #2 Jay conferma che la mappa è utilizzabile al tavolo senza ritocchi manuali di struttura
- [x] #3 Ogni difetto segnalato è riprodotto in un test prima di essere corretto
- [x] #4 Le regole di orientamento e allineamento definitive sono codificate e annotate in docs/format.md
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Correzioni gate M3 (dopo il feedback di Jay). Misurato sul generatore, non sono difetti del seed 1337: 37/40 seed hanno almeno un corridoio che attraversa una stanza, e 102 segmenti su 40 seed sono quadrati (orientamento ambiguo).
5. Test di regressione PRIMA della correzione: (a) nessun Rect di Blueprint.corridors si sovrappone in modo strettamente interno a una Room, su molti seed; (b) l'orientamento del segmento di gomito 1x1 di plan_corridor e verticale/orizzontale come da geometria, e render_blueprint disegna i due lati lunghi giusti.
6. model.py: Corridor(Rect) con campo esplicito horizontal, cosi l'orientamento non si indovina piu da w>=h (difetto 3: gomiti quadrati con i muri sui lati sbagliati che sigillano il passaggio).
7. compose.plan_corridor: accetta obstacles e sceglie fra piu rotte candidate (dritta con linea centrale spostabile nella banda di overlap, L orizzontale-prima, L verticale-prima) quella che non attraversa stanze (difetti 1 e 2).
8. bsp._connect_subtree: collega la coppia di stanze piu vicina fra i due sottoalberi invece di un rappresentante casuale, cosi i corridoi restano locali al taglio BSP e non attraversano meta mappa.
9. Rigenerare generated/dungeon_m3.dungeondraft_map, rivalidare, aggiornare docs/format.md con le regole definitive di orientamento e allineamento, e riportare il file a Jay.

10. [FATTO] bsp._reproject_doors: dopo _enlarge_room, riproietta Door.t di ogni porta sul nuovo perimetro al punto assoluto pre-ingrandimento.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Feedback Jay (2026-09-04): pavimenti OK (bianchi, previsto). Muri con problemi: (1) stanza in alto a destra, due coppie di corridoi sforano dentro la stanza; (2) muri del corridoio che esce dalla stanza in alto al centro e scende verso il basso sono troppo lunghi.

Feedback Jay (2026-09-04) sul gate M3, dungeon_m3 (seed 1337): pavimenti OK. Tre difetti sui corridoi: (1) il corridoio fra la stanza in basso a sinistra e quella in alto al centro interseca altre stanze; (2) il corridoio fra la stanza a sinistra al centro e quella in alto al centro entra completamente dentro la stanza in alto a sinistra; (3) il corridoio che esce dall'angolo in basso a destra della stanza in alto a sinistra ha i muri sui lati sbagliati.

Correzioni implementate dopo il feedback di Jay (test scritti prima, tutti e 5 rossi in partenza, in tests/test_corridor_routing.py):
- Difetto 3 (muri sui lati sbagliati): model.Corridor(Rect) con campo esplicito 'horizontal'; compose._long_sides lo usa al posto dell'euristica w>=h, che sui segmenti di gomito 1x1 murava le testate sigillando il passaggio (102 segmenti ambigui su 40 seed di prova).
- Regola aggiuntiva emersa lavorandoci: nel gomito di una L il muro di un braccio attraversava l'imbocco dell'altro. compose._channel_wall_pieces non disegna il tratto di muro che cade dentro un altro canale; i corridoi vanno percio disegnati in blocco con draw_corridor_network.
- Difetti 1 e 2 (corridoi che attraversano stanze): tre correzioni, servono tutte e tre. compose.plan_corridor ora sceglie fra piu rotte candidate quella che non entra in nessuna stanza (37 seed su 40 con attraversamenti -> 14); bsp._connect_subtree collega la coppia di stanze piu vicina fra i due sottoalberi invece di due rappresentanti a caso (era questo a produrre il collegamento angolo-angolo segnalato da Jay); i collegamenti facoltativi (anelli, porte segrete) rinunciano se la rotta migliore entra comunque in una terza stanza (14 -> 0). In piu bsp._enlarge_room tratta i corridoi come ostacoli, cosi la stanza boss non si allarga sopra un corridoio.
Suite: 312 test verdi (307 preesistenti + 5 nuovi). Golden bsp_seed_1337 rigenerato dopo verifica del diff (solo walls/patterns/objects/next_node_id, nessun cambio di formato). Taratura di test_long_corridors_exist_on_a_large_sparse_map corretta: passava per il motivo sbagliato, i corridoi lunghi che trovava erano l'effetto del difetto. Regole scritte in docs/format.md §9. Mappa rigenerata: generated/dungeon_m3.dungeondraft_map, validazione pulita (zero problemi, spariti anche i 2 DDF102 di prima).

Riapertura dopo la prima correzione: Jay ha confermato che i 3 difetti precedenti sono risolti, e ha segnalato un quarto difetto residuo: 'nella stanza in basso a sinistra il muro che arriva alla porta in alto a destra e lungo mezzo quadretto in piu e ostacola il passaggio'. Riprodotto in tests/test_corridor_routing.py (test_m3_seed_1337_has_no_door_offset_from_its_corridor + test_enlarging_a_room_does_not_move_its_doors) prima della correzione. Causa: bsp._enlarge_room (usata per ingrandire la stanza boss) allarga i lati SENZA porte, ma allargare un lato perpendicolare allunga comunque il muro su cui e appoggiata la porta di un lato adiacente; Door.t e una frazione di quel muro, quindi la porta scivola (nel caso reale: da x=31.0, allineata al corridoio, a x=31.487). Corretto con bsp._reproject_doors: dopo l'ingrandimento, ogni porta viene riproiettata sul nuovo perimetro al punto assoluto che occupava prima, cosi resta allineata al corridoio esterno. Golden bsp_seed_1337 rigenerato (diff verificato: un solo portal.wall_distance cambiato, 0.74359->0.73171, coerente con lo spostamento atteso). Suite: 315 test verdi. generated/dungeon_m3.dungeondraft_map rigenerato, validazione pulita. In attesa che Jay riapra e confermi.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-04 07:17
---
File pronto: generated/dungeon_m3.dungeondraft_map (dungeon di 8 stanze, seed 1337, arredo medium, luci attive; rigenerabile con 'ddforge generate dungeon --template templates/blank_80x80.dungeondraft_map --out generated/dungeon_m3.dungeondraft_map --width 80 --height 80 --rooms 8 --seed 1337 --furnish medium --lights'). Passa la validazione con 2 soli avvisi non bloccanti (DDF102 su una piega di corridoio, limite noto e documentato del validatore, non un difetto della mappa). Include gia la correzione di direction/rotation trovata nel gate di TASK-12. In attesa che Jay lo apra e verifichi: tutte le stanze raggiungibili, porte orientate bene, pavimenti che non sbordano.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Gate umano M3 chiuso dopo due round di verifica manuale di Jay in Dungeondraft su generated/dungeon_m3.dungeondraft_map (seed 1337). Round 1: 3 difetti sui corridoi (attraversamento di stanze x2, orientamento muri del canale sbagliato). Round 2, dopo la prima correzione: 1 difetto residuo (porta disallineata dal corridoio dopo l'ingrandimento della stanza boss). Tutti e 4 riprodotti in test PRIMA della correzione (tests/test_corridor_routing.py, 8 test). Cause e correzioni: (1) model.Corridor con orientamento esplicito invece di dedurlo da w>=h; (2) compose._channel_wall_pieces taglia i muri dove un altro canale li attraversa, cosi i corridoi si disegnano in blocco (draw_corridor_network); (3) compose.plan_corridor sceglie fra piu rotte candidate quella che non attraversa altre stanze; bsp._connect_subtree collega le due stanze piu vicine fra sottoalberi invece di rappresentanti a caso; i collegamenti facoltativi (anelli, porte segrete) rinunciano se l'unica rotta disponibile attraversa una terza stanza; (4) bsp._reproject_doors riallinea le porte esistenti dopo un ingrandimento di stanza. Verificato con: suite completa 315 test verdi (307 preesistenti + 8 nuovi), golden file bsp_seed_1337 rigenerato con diff verificato a mano (solo geometria/next_node_id), generated/dungeon_m3.dungeondraft_map rigenerato e validato senza errori ne warning. Regole definitive codificate e annotate in docs/format.md §9.1-9.6, con riferimento a dove vivono nel codice e quale test le protegge. Jay ha confermato la mappa utilizzabile al tavolo senza ritocchi manuali di struttura. Follow-up separato aperto su richiesta di Jay: TASK-43 (pavimenti kind-specifici, oggi tutti uniformi).
<!-- SECTION:FINAL_SUMMARY:END -->
