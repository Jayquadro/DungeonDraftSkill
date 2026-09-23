---
id: TASK-65
title: 'Promuovi la prigione a monumento SITE_BLOCK, come la cattedrale'
status: Done
assignee:
  - '@claude'
created_date: '2026-09-23 07:43'
updated_date: '2026-09-23 09:05'
labels: []
dependencies:
  - TASK-64
ordinal: 66000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Jay vuole la prigione fra i luoghi 'grandi' che occupano un isolato intero (SITE_BLOCK), come cattedrale/palazzo/monastero/accademia, invece che un luogo SITE_LOT su un lotto (con LandmarkKind.lots=3.0, TASK-62). Segue lo stesso pattern gia' in landmarks.py per gli altri monumenti: nessuna regola di piazzamento (RULE_ANY di default), stessa fascia di scale (_BIG: quartiere e citta', non isolato, invariato), stesso unique/chance di oggi. sprite_only resta True (gia' cosi' da TASK-63): a SITE_BLOCK 'lots' e' ignorato per costruzione (city.py._block_candidates), quindi va rimosso dalla definizione.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 LandmarkKind 'prigione' ha site=SITE_BLOCK invece di SITE_LOT, senza il campo lots (ignorato per i siti a blocco)
- [x] #2 La prigione occupa un isolato intero sulle mappe rigenerate (quartiere/citta), non piu' un lotto
- [x] #3 Nessun altro luogo (inclusi gli altri monumenti SITE_BLOCK e i 18 luoghi SITE_LOT/SITE_BAND rimasti) cambia comportamento
- [x] #4 Le mappe di valutazione in generated/ per i tre preset sono rigenerate con seed fissi, nome che indica il task, e superano ddforge validate
- [x] #5 Suite di test completa verde, golden aggiornati dove il cambio li tocca
- [x] #6 Gate umano: Jay apre le mappe rigenerate in Dungeondraft e conferma il risultato
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. landmarks.py: cambiare la LandmarkKind 'prigione' da (_BIG, SITE_LOT, unique=True, chance=0.5, lots=3.0) a (_BIG, SITE_BLOCK, unique=True, chance=0.5), stesso schema di cattedrale/palazzo/accademia (nessun RULE esplicito = RULE_ANY di default, niente 'lots'). Aggiornare/rimuovere il commento 'lots=3.0, TASK-62' sopra la voce.
2. Verificare in process (rigenerazione diretta, non solo lettura) su piu' seed a quartiere/citta che la prigione occupi ora un isolato intero (stesso ordine di grandezza di cattedrale/palazzo), e che nessun altro luogo cambi (diff dei landmark piazzati a parita' di seed, luoghi diversi da prigione invariati).
3. Rigenerare i golden con scripts/regen_city_golden.py e la suite completa.
4. Rigenerare le mappe di valutazione in generated/ per i tre preset (seed 1337, canvas 78x78, naming _task65), validare con ddforge validate.
5. Verifica oggettiva (AC1-5), poi gate umano (AC6).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Cambio in landmarks.py: 'prigione' passata da (_BIG, SITE_LOT, unique=True, chance=0.5, lots=3.0) a (_BIG, SITE_BLOCK, unique=True, chance=0.5), stesso schema esatto di cattedrale/palazzo/accademia (nessun campo lots, nessun RULE esplicito = RULE_ANY di default). Aggiornati i commenti storici vicini (il blocco su tempio che elencava 19 luoghi SITE_LOT/SITE_BAND e 5 monumenti SITE_BLOCK, e la nota su _SPRITE_ONLY_KEYS) per riflettere 18+6 invece di 19+5, con un rimando esplicito a TASK-65. sprite_only restava gia' True da TASK-63, invariato.

Verificato in process (non solo lettura) su 5 seed a quartiere e 5 a citta, richiedendo esplicitamente prigione+cattedrale insieme: l'area del rettangolo della prigione e' ora dello stesso ordine di grandezza di quella della cattedrale (es. quartiere seed 2: prigione 158.4 vs cattedrale 83.0; citta seed 3: prigione 11.5 vs cattedrale 7.4) - prima (SITE_LOT, lots=3.0) sarebbe stata un lotto, un ordine di grandezza piu' piccola. landmark.building resta None per la prigione a ogni preset (sprite_only, invariato).

Suite mirata (test_city_landmarks.py, test_generators_city.py, test_compose.py): 305 passed. Golden invariati (city_seed_1337*.json testano solo isolato, dove prigione non e' mai stata ammissibile - _BIG esclude isolato sia prima che dopo, nessun impatto). Suite completa: 779 passed, 1 skipped, 0 failed.

Mappe: generated/city_{isolato,quartiere,citta}_task65.dungeondraft_map rigenerate (seed 1337, canvas 78x78), tutte e tre superano ddforge validate. isolato verificato byte-per-byte identico a generated/city_isolato_task64.dungeondraft_map (cmp): prigione non ammissibile li', nessun impatto, come atteso.

APERTO: AC6 (gate umano) - Jay deve aprire le mappe quartiere/citta' in Dungeondraft e confermare che la prigione ora si legge come un monumento.

Gate umano confermato da Jay (2026-09-23): la prigione si legge come monumento sulle mappe rigenerate.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Prigione promossa da luogo SITE_LOT (lotto) a monumento SITE_BLOCK (isolato intero), stesso schema di cattedrale/palazzo/accademia/monastero/arena. Verificato in process: l'area occupata e' ora dello stesso ordine di grandezza della cattedrale a quartiere e citta' (isolato non ammissibile per prigione, invariato prima/dopo). Nessun altro luogo toccato. Suite completa verde (779 passed, 1 skipped), golden invariati (isolato non tocca prigione), tre mappe generated/city_*_task65 rigenerate e validate. In attesa del gate umano di Jay (AC6).
<!-- SECTION:FINAL_SUMMARY:END -->
