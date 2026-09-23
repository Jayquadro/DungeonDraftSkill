---
id: TASK-63
title: Sprite dei luoghi anche a isolato e sprite piu' grandi a quartiere
status: Done
assignee:
  - '@claude'
created_date: '2026-09-22 11:42'
updated_date: '2026-09-23 09:03'
labels: []
dependencies:
  - TASK-62
documentation:
  - docs/SPEC.md
ordinal: 64000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Seguito di TASK-62, dopo che Jay ha aperto le mappe rigenerate in Dungeondraft. Due richieste: (1) i 24 luoghi chiusi coperti dal pacchetto Nova Mistralis (i 19 SITE_LOT/SITE_BAND piu' i 5 monumenti SITE_BLOCK: cattedrale, palazzo, arena, accademia, monastero) devono mostrare sempre lo sprite nm_* anche al preset isolato, non un edificio a stanze generato da building.py come oggi - questo capovolge una scelta di design scritta in docs/SPEC.md (TASK-48: 'al preset isolato un luogo chiuso dovrebbe sempre essere un edificio a stanze vero'), che va aggiornata di conseguenza. Confermato con Jay: si applica a tutti e 24, non solo al sottoinsieme SITE_LOT. (2) Gli sprite dei luoghi a preset 'quartiere' vanno ingranditi ulteriormente rispetto allo stato di TASK-62: oggi sono gia' al tetto dato dalla profondita' del lotto (building_depth_range del preset, ~3,0 quadretti) - la leva 'lots' non basta piu', allarga solo la larghezza lungo la fila. Jay ha chiesto specificamente di far occupare allo sprite una parte maggiore del suo lotto, togliendo i bordi/margine attorno se necessario, non di allargare la geometria dei lotti stessi: la leva e' quindi compose._SPRITE_FILL (oggi 0.92 fisso per ogni preset), da alzare solo per 'quartiere'. La 'citta' resta invariata (Jay ha detto esplicitamente di non toccarla).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 I 24 luoghi chiusi coperti dal pacchetto (19 SITE_LOT/SITE_BAND + cattedrale/palazzo/arena/accademia/monastero) mostrano sempre lo sprite nm_* al preset isolato, mai piu' un edificio a stanze da building.py
- [x] #2 I luoghi ancora sul ripiego (dogana, conceria, macello, mulino, lazzaretto, torre_guardia) e i luoghi open_air restano invariati: nessun cambiamento al loro rendering
- [x] #3 docs/SPEC.md e' aggiornato per riflettere che i luoghi coperti dal pacchetto sono sempre sprite a isolato, non piu' sempre edificio a stanze
- [x] #4 Gli sprite dei luoghi al preset quartiere occupano una parte piu' grande del proprio lotto (fill alzato da 0.92, margine ridotto o azzerato) senza sconfinare nel lotto/isolato confinante, misurato sulle mappe rigenerate
- [x] #5 Il preset citta' non cambia: stessa dimensione/fill di TASK-62, verificato per non regressione
- [x] #6 Le mappe di valutazione in generated/ per i tre preset sono rigenerate con seed fissi, nome che indica il task, e superano ddforge validate
- [x] #7 Suite di test completa verde, golden aggiornati dove il cambio li tocca
- [x] #8 Gate umano: Jay apre le mappe rigenerate in Dungeondraft e conferma il risultato
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. LandmarkKind (landmarks.py): aggiungere un campo booleano (es. sprite_only, default False) e impostarlo a True sui 24 luoghi chiusi coperti dal pacchetto (i 19 gia' a lots=3.0 + cattedrale, palazzo, arena, accademia, monastero). Non toccare i luoghi sul ripiego ne' gli open_air (gia' sempre sprite).
2. city.py._claim: quando kind.sprite_only e' True, non chiamare _landmark_building anche a preset isolato - building_blueprint resta None, draw_landmark in compose.py ripiega gia' sullo sprite quando building e' None (percorso esistente).
3. model.py: aggiungere Blueprint.scale (stringa, default vuota) per portare il nome del preset fino a compose.py. city.py.generate: valorizzarlo con lo scale effettivo nel Blueprint finale.
4. compose.py: aggiungere una costante _SPRITE_FILL_QUARTIERE (1.0) usata solo quando blueprint.scale=='quartiere'; il fill viaggia da render_city_blueprint a draw_landmark a _draw_landmark_sprites come parametro esplicito, default _SPRITE_FILL cosi' isolato e citta' restano invariati.
5. docs/SPEC.md: aggiornare la sezione luoghi per riflettere che i luoghi coperti dal pacchetto sono sempre sprite a isolato; docs/sprite-luoghi.md se serve.
6. Verifica diretta in process: sui 24 luoghi a isolato, landmark.building e' sempre None; i luoghi sul ripiego lo hanno ancora quando il lotto e' abbastanza grande. Misurare la crescita a quartiere senza sconfinamento; citta' invariata a parita' di seed rispetto a generated/city_citta_task62.
7. Rigenerare golden e mappe di valutazione nei tre preset (seed 1337, canvas 78x78, naming _task63); ddforge validate su tutte e tre; pytest -q sull'intera suite.
8. Verifica oggettiva (AC1-7), poi gate umano (AC8).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Sprite anche a isolato (AC1/AC2): aggiunto LandmarkKind.sprite_only (default False), True per i 24 luoghi chiusi coperti dal pacchetto (i 19 gia' a lots=3.0 da TASK-62 + cattedrale, palazzo, arena, accademia, monastero) via un set _SPRITE_ONLY_KEYS applicato con dataclasses.replace su _LANDMARK_KINDS_RAW (un solo punto da aggiornare, non 24 call site separati). city._claim: quando kind.sprite_only e' True non chiama piu' _landmark_building nemmeno a isolato; draw_landmark in compose.py ripiega gia' sullo sprite quando building e' None (stesso percorso gia' usato per i lotti troppo piccoli, nessun codice nuovo li'). Verificato in process su 5 seed a isolato: tutti i landmark con kind.sprite_only hanno building is None; i 6 luoghi ancora sul ripiego (dogana, conceria, macello, mulino, lazzaretto, torre_guardia) continuano a ottenere un edificio a stanze vero quando il lotto e' abbastanza grande (22/22 nel campione), invariati.

Sprite piu' grandi a quartiere, citta' invariata (AC4/AC5): aggiunta Blueprint.scale (model.py) per portare il nome del preset a compose.py (quartiere e citta' condividono abstract_buildings=True, serviva un modo per distinguerli a valle). compose._SPRITE_FILL_QUARTIERE=1.0 (contro _SPRITE_FILL=0.92 usato altrove) passato come parametro esplicito da render_city_blueprint a draw_landmark a _draw_landmark_sprites solo quando blueprint.scale=='quartiere'. Fill 1.0 riempie l'intero rettangolo buildable del lotto (gia' arretrato da side_margin/setback, quindi senza sconfinare nel lotto vicino) invece di lasciare l'8% di _SPRITE_FILL. Misurato in process: crescita reale +8.7% (1/0.92), es. tempio a quartiere passa da una scala media 2.48 a 2.69 quadretti sui 10 seed testati - coerente con l'aritmetica del fill, non un miglioramento drammatico ma reale e verificato, comunicato a Jay senza sovrastimarlo. Citta' verificata byte-per-byte identica a generated/city_citta_task62.dungeondraft_map a parita' di seed (cmp): nessuna regressione.

Documentazione (AC3): docs/SPEC.md aggiornato (le tre forme di disegno di un luogo, la nota su isolato/edificio a stanze, nuovo paragrafo su _SPRITE_FILL_QUARTIERE). docs/sprite-luoghi.md sez. 1 e 7 corrette (fornaio/macelleria non 'ricadono spesso' sullo sprite, lo mostrano sempre per design) e nuova sez. 10 'Sprite sempre, anche a isolato; fill maggiore a quartiere (TASK-63)'.

Mappe e verifica (AC6/AC7): generated/city_{isolato,quartiere,citta}_task63.dungeondraft_map rigenerate (seed 1337, canvas 78x78). Tutte e tre superano ddforge validate. Golden tests/fixtures/golden/city_seed_1337_landmarks.json rigenerato (city_seed_1337.json invariato, confermando che la geometria di base non e' toccata). Suite completa: 779 passed, 1 skipped (preesistente), 0 failed.

APERTO: AC8 (gate umano) - Jay deve aprire i tre file in Dungeondraft e confermare il risultato.

Gate umano confermato da Jay (2026-09-23): sprite anche a isolato e fill maggiore a quartiere approvati sulle mappe rigenerate.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
I 24 luoghi chiusi coperti dal pacchetto (i 19 con lots=3.0 di TASK-62 piu' i 5 monumenti SITE_BLOCK) mostrano ora sempre lo sprite dedicato, anche a isolato: LandmarkKind.sprite_only=True fa saltare _landmark_building anche li', dove prima diventavano un edificio a stanze quando il lotto era abbastanza grande. I luoghi ancora sul ripiego restano invariati (edificio a stanze a isolato, come prima). A quartiere lo sprite riempie di piu' il lotto (compose._SPRITE_FILL_QUARTIERE=1.0 contro 0.92, +8.7% misurato, senza sconfinare: il rettangolo e' gia' arretrato da side_margin/setback). Citta' verificata byte-per-byte identica a TASK-62: nessuna modifica. docs/SPEC.md e docs/sprite-luoghi.md aggiornati. Verificato con: pytest -q sull'intera suite (779 passed, 1 skipped), golden rigenerato, tre mappe generated/city_*_task63 validate senza errori, confronto diretto in process (building sempre None per i 24 coperti, sempre presente per il ripiego quando il lotto e' capiente, cmp byte-a-byte per citta'). In attesa del gate umano di Jay (AC8).
<!-- SECTION:FINAL_SUMMARY:END -->
