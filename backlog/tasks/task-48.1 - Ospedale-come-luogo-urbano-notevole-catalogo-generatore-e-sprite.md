---
id: TASK-48.1
title: 'Ospedale come luogo urbano notevole: catalogo, generatore e sprite'
status: Done
assignee:
  - '@claude'
created_date: '2026-09-11 13:37'
updated_date: '2026-09-14 08:35'
labels: []
milestone: m-8
dependencies: []
documentation:
  - docs/sprite-luoghi.md
parent_task_id: TASK-48
ordinal: 49000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fra i luoghi notevoli delle mappe cittadine manca l'ospedale. Il piu' vicino e' il lazzaretto, che e' un'altra cosa: edificio d'isolamento, lungo e basso, recintato, piazzato fuori le mura. Un ospedale cittadino sta invece dentro le mura, in mezzo al tessuto abitato, ed e' uno dei luoghi che il tavolo cerca per primi. Il prompt per generare lo sprite dedicato (nm_ospedale.png, 768x768, tetto ricolorabile) e' gia' scritto in prompt/01-ospedale.md; quello che manca e' il luogo dentro il sistema: non compare fra i tipi generabili da generators/city.py, non ha una voce in assets._CITY_LANDMARK_SPRITES e non e' elencato in docs/sprite-luoghi.md. Finche' lo sprite dipinto non esiste serve uno sprite di ripiego scelto fra i 440 object gia' in catalogo.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Il tipo di luogo `ospedale` e' generabile da generators/city.py e compare sulla mappa con l'etichetta Ospedale
- [x] #2 assets._CITY_LANDMARK_SPRITES ha una voce `ospedale` che risolve a uno sprite presente nei pack installati, cosi' il luogo si disegna anche prima che nm_ospedale.png esista
- [x] #3 L'ospedale e' richiedibile esplicitamente come gli altri luoghi notevoli, e quando non e' richiesto puo' uscire a sorte al piu' una volta per mappa
- [x] #4 docs/sprite-luoghi.md elenca l'ospedale fra i luoghi chiusi, con la dimensione misurata a cui viene disegnato nei preset quartiere e citta
- [x] #5 I golden di tests/fixtures/golden sono rigenerati e la suite passa
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Aggiungere ospedale a generators/landmarks.py: LandmarkKind SITE_LOT (non SITE_BAND come lazzaretto, l'ospedale sta dentro le mura), unique=True, chance=0.5, lots=1.5, scale _BIG (come bagni); aggiungere a BUILDING_TYPE come manor.
2. Aggiungere assets._CITY_LANDMARK_SPRITES['ospedale'] con uno sprite di ripiego libero fra i 440 object (house_02, non usato da nessun altro luogo), in attesa di nm_ospedale.png.
3. Verificare manualmente che city.generate(..., requested_landmarks=['ospedale']) piazzi il luogo con etichetta 'Ospedale' e che palette_for('city', catalog) risolva lo sprite.
4. Misurare con 20 seed (stesso metodo di scripts/city_landmarks_census.py) la dimensione disegnata a 'quartiere'/'citta' e la frequenza per mappa, aggiungere la riga a docs/sprite-luoghi.md fra bagni e mulino.
5. Rigenerare tests/fixtures/golden con scripts/regen_city_golden.py (il solo golden con landmarks cambia, perche' l'inserimento in LANDMARK_KINDS sposta l'ordine di estrazione rng) e far girare l'intera suite.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verificato manualmente: city.generate(seed=1, scale='quartiere', requested_landmarks=['ospedale']) piazza un Landmark(kind='ospedale', label='Ospedale', site='lot'). palette_for('city', catalog).landmark_sprites['ospedale'] risolve a house_02 (208x262, pack Bp03igMq). Misura su 20 seed (script ad-hoc equivalente a city_landmarks_census.py): quartiere 4,0x4,1 q, citta 1,1x1,3 q; frequenza per mappa (non richiesto) 0,60/0,65 su 20 seed con city_landmarks_census.py --seeds 20. Golden rigenerato con scripts/regen_city_golden.py --write: solo city_seed_1337_landmarks.json cambia (atteso: l'inserimento nel tuple LANDMARK_KINDS sposta l'ordine dei rng.random() successivi); city_seed_1337.json (senza landmarks) invariato. Suite completa: 745 passed, 1 skipped (./.venv/Scripts/python.exe -m pytest -q).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Ospedale aggiunto al catalogo dei luoghi urbani notevoli: LandmarkKind SITE_LOT/unique/chance 0.5/lots 1.5 in generators/landmarks.py (dentro le mura, a differenza del lazzaretto che e' SITE_BAND/RULE_EDGE), voce 'ospedale': manor in BUILDING_TYPE, sprite di ripiego house_02 in assets._CITY_LANDMARK_SPRITES (libero, in attesa di nm_ospedale.png), riga aggiunta a docs/sprite-luoghi.md fra bagni e mulino con dimensioni e frequenza misurate su 20 seed. Golden tests/fixtures/golden/city_seed_1337_landmarks.json rigenerato con scripts/regen_city_golden.py --write (solo file interessato). Verificato: piazzamento esplicito via requested_landmarks, risoluzione sprite via palette_for, suite completa 745 passed/1 skipped.
<!-- SECTION:FINAL_SUMMARY:END -->
