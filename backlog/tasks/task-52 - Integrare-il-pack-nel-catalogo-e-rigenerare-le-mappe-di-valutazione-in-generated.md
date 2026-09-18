---
id: TASK-52
title: >-
  Integrare il pack nel catalogo e rigenerare le mappe di valutazione in
  generated/
status: In Progress
assignee:
  - '@claude'
created_date: '2026-09-15 07:18'
updated_date: '2026-09-18 08:00'
labels: []
milestone: m-9
dependencies:
  - TASK-51
documentation:
  - docs/sprite-luoghi.md
priority: high
type: feature
ordinal: 53000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Finche' il pacchetto non e' montato sulle mappe non si puo' dire se funziona. Oggi i luoghi urbani notevoli usano sprite di ripiego scelti fra i 440 object dei pack di Jay (assets._CITY_LANDMARK_SPRITES: l'ospedale, per esempio, cade su house_02), e le case ordinarie usano le icone piatte del pacchetto BB Houses1. E' proprio la convivenza di due registri grafici diversi il motivo per cui la mappa non e' ancora bella, come annotato in docs/sprite-luoghi.md sez. 8.

Quando il pack e' importabile (TASK-51) va agganciato al sistema e i file in generated/ vanno rigenerati, perche' e' li' che Jay guarda il risultato: aprendo i .dungeondraft_map in Dungeondraft deve vedere i nuovi sprite al posto dei ripieghi e poter giudicare l'insieme, non il singolo pezzo.

Da coprire: lettura del nuovo pack nel catalogo asset (data/assets.json), voci di assets._CITY_LANDMARK_SPRITES che puntano ai nuovi nm_* per i luoghi coperti dal pacchetto lasciando il ripiego a quelli ancora scoperti, e rigenerazione dei file di valutazione in generated/ sui tre preset di scala (isolato, quartiere, citta) con seed fissi, cosi' che due rigenerazioni successive siano confrontabili.

Vanno rigenerati anche i golden di tests/fixtures/golden se il cambio di sprite li tocca, e la suite deve restare verde.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Il pack nuovo e' letto dal catalogo asset e i suoi sprite compaiono in data/assets.json con le dimensioni native lette dall'header PNG
- [x] #2 assets._CITY_LANDMARK_SPRITES punta ai nuovi nm_* per ogni luogo coperto dal pacchetto, e conserva lo sprite di ripiego per i luoghi non ancora coperti
- [x] #3 generated/ contiene mappe di valutazione rigenerate per i tre preset isolato, quartiere e citta, con seed fissi e nomi che dicono a quale task appartengono
- [ ] #4 Le mappe rigenerate si aprono in Dungeondraft senza errori e superano ddforge validate
- [x] #5 Un documento o una sezione di docs/ elenca quali luoghi usano ormai uno sprite del pacchetto e quali sono ancora sul ripiego, cosi' si sa cosa resta da disegnare
- [x] #6 I golden di tests/fixtures/golden sono aggiornati dove il cambio di sprite li tocca e la suite completa passa
- [ ] #7 Gate umano: Jay apre le mappe di generated/ in Dungeondraft e giudica il risultato complessivo
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Rigenerare data/assets.json: ddforge catalog --from-catalog data/assets.json --from templates/blank_80x80.dungeondraft_map --from templates/rich_reference.dungeondraft_map --from templates/blank_160x160.dungeondraft_map --pack "C:\Users\lorenzo_m\Documents\Dungeondraft\NovaMistralis.dungeondraft_pack" --out data/assets.json (pack Ada7IQuz gia' in asset_manifest dei tre template dal commit 6ef9d96; il file .dungeondraft_pack compilato e' su disco in Documents/Dungeondraft, non nel repo). Verifica: 52 pack invariati, 27 nuove chiavi nm_* in objects, con object_sizes reali dall'IHDR PNG.
2. Aggiornare src/ddforge/assets.py _CITY_LANDMARK_SPRITES: sostituire il fallback con lo sprite nm_* per i 21 luoghi chiusi coperti 1:1 dal pacchetto (ospedale, teatro, accademia, prigione, municipio, faro, bagni, biblioteca, tempio, monastero, caserma, banca, alchimista, magazzino, fabbro, stalle, fornaio, macelleria, taverna, locanda, bordello) e per i due luoghi open_air coperti (cimitero: nm_cimitero_croce/fossa/lapide_1 al posto dei gravestone_*/grave_* BB; mercato: nm_banco_mercato_1 al posto di canopy_01), aggiornando i commenti che spiegano la provenienza. Lasciare invariato il ripiego per i luoghi non coperti (cattedrale, palazzo, arena, gilda, dogana, conceria, macello, mulino, lazzaretto, torre_guardia, patibolo, statua, fiera, giardino). nm_villa_nobiliare e nm_armeria restano nel catalogo ma non agganciati: non esiste ancora un LandmarkKind per loro (TASK-49), fuori scope qui.
3. Rigenerare le mappe di valutazione in generated/ per i tre preset con seed fisso 1337, canvas 78x78 (stessa convenzione di TASK-48): city_isolato_task52.dungeondraft_map, city_quartiere_task52.dungeondraft_map, city_citta_task52.dungeondraft_map, con ddforge generate city --template templates/blank_80x80.dungeondraft_map --seed 1337 --width 78 --height 78 --scale <preset> --out generated/city_<preset>_task52.dungeondraft_map. Validare ciascuna con ddforge validate.
4. Aggiornare docs/sprite-luoghi.md (o nuova sezione) con l'elenco dei luoghi ora su sprite del pacchetto vs quelli ancora sul ripiego (AC5).
5. Rigenerare i golden di tests/fixtures/golden toccati dal cambio sprite (city_seed_1337_landmarks.json e chi altro referenzia texture di luogo) con scripts/regen_city_golden.py; pytest -q sull'intera suite verde.
6. Verifica oggettiva, poi gate umano: Jay apre le mappe di generated/ in Dungeondraft (AC7).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Catalogo (AC1): ddforge catalog --from-catalog data/assets.json --from templates/blank_80x80.dungeondraft_map --from templates/rich_reference.dungeondraft_map --from templates/blank_160x160.dungeondraft_map --pack "Documents/Dungeondraft/NovaMistralis.dungeondraft_pack" --out data/assets.json. Pack Ada7IQuz gia' in asset_manifest dei tre template (commit 6ef9d96, Jay lo aveva gia' importato e i template risalvati): bastava aggiungere il --pack, nessun errore di pack orfano. Il .dungeondraft_pack compilato non e' nel repo (dist/ e' ignorata, il packer ufficiale gira solo sulla macchina di Jay): letto da Documents/Dungeondraft/NovaMistralis.dungeondraft_pack sul disco locale. Risultato: 51->52 pack, objects 543->570 (+27 nm_*), object_sizes 508->535, tutte con dimensioni reali dall'IHDR PNG (verificato stampando catalog["object_sizes"] per le 27 chiavi nm_*). Comando documentato in docs/format.md 10.3.

Palette (AC2): src/ddforge/assets.py _CITY_LANDMARK_SPRITES aggiornato per i 21 luoghi chiusi coperti 1:1 (ospedale, teatro, accademia, prigione, municipio, faro, bagni, biblioteca, tempio, monastero, caserma, banca, alchimista, magazzino, fabbro, stalle, fornaio, macelleria, taverna, locanda, bordello) piu' i due open_air coperti (cimitero: nm_cimitero_croce/fossa/lapide_1, sostituisce per intero il ripiego BB invece di mischiare i due registri grafici; mercato: nm_banco_mercato_1). I 14 luoghi non commissionati (cattedrale, palazzo, arena, gilda, dogana, conceria, macello, mulino, lazzaretto, torre_guardia, patibolo, statua, fiera, giardino) restano sul ripiego, invariati. nm_villa_nobiliare e nm_armeria sono nel catalogo ma non agganciati: nessun LandmarkKind per loro in generators/landmarks.py (TASK-49 lo segnalava gia'), fuori scope di questo task - serve un task a parte per aggiungerli. Verificato con palette_for("city", load_catalog()): tutte le 37 chiavi si risolvono senza errori, le 23 coperte puntano a res://packs/Ada7IQuz/..., le 14 sul ripiego invariate.

Mappe di valutazione (AC3/AC4): generated/city_isolato_task52.dungeondraft_map, city_quartiere_task52.dungeondraft_map, city_citta_task52.dungeondraft_map, seed 1337, canvas 78x78 (stessa convenzione di TASK-48), comando ddforge generate city --template templates/blank_80x80.dungeondraft_map --seed 1337 --width 78 --height 78 --scale <preset>. Verificato che le tre mappe referenzino davvero texture nm_* (isolato 9 texture diverse, quartiere 15, citta 6 - dipende da quali luoghi il seed estrae a quel preset). ddforge validate: "Nessun problema trovato" su tutte e tre (AC4 automatico). generated/ e' gitignorata (nessuna mappa precedente era tracciata), quindi i file restano solo su disco per Jay: non c'e' niente da committare li'. Resta da verificare l'apertura reale in Dungeondraft (parte non automatizzabile di AC4, bundle con AC7).

Documentazione (AC5): docs/sprite-luoghi.md nuova sez. 10 "Chi ha gia' lo sprite del pacchetto, chi e' ancora sul ripiego": tabella dei 23 coperti, tabella dei 14 sul ripiego con motivo, nota sui due sprite generati ma non agganciati (villa_nobiliare, armeria). docs/format.md 10.3: comando ddforge catalog usato in TASK-52 documentato accanto a quello di TASK-48, stesso stile.

Golden e suite (AC6): scripts/regen_city_golden.py --write ha rigenerato solo tests/fixtures/golden/city_seed_1337_landmarks.json (city_seed_1337.json, senza landmarks, invariato come atteso). Diff verificato: solo texture/scale degli object di cimitero e mercato (i due open_air coperti), nessuna regressione altrove. pytest -q sull'intera suite: 779 passed, 1 skipped (preesistente, non collegato), 0 failed.

APERTO: AC4 (parte "si aprono in Dungeondraft senza errori") e AC7 (gate umano) restano da confermare - Jay deve aprire i tre file di generated/city_*_task52.dungeondraft_map in Dungeondraft e giudicare il risultato complessivo (luoghi coerenti con lo stile del pacchetto invece delle icone piatte BB).
<!-- SECTION:NOTES:END -->
