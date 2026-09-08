---
id: TASK-45
title: Estendere il catalogo asset con i nuovi pack DungeonDraft di Jay
status: Done
assignee:
  - '@claude'
created_date: '2026-09-08 08:56'
updated_date: '2026-09-08 13:15'
labels: []
dependencies: []
documentation:
  - docs/SPEC.md
  - docs/format.md
type: feature
ordinal: 45000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Jay ha installato in DungeonDraft diversi pacchetti di asset aggiuntivi rispetto ai 44 pack già catalogati in data/assets.json (generato in TASK-4). Questi nuovi pacchetti non sono ancora usabili dalla skill: assets.py (TASK-4/TASK-17) accetta solo pack ID presenti in header.asset_manifest dei template sorgente usati per costruire il catalogo, e ddforge catalog estrae le texture da documenti .dungeondraft_map reali, non dai file dei pack stessi. Bisogna incorporare i nuovi pacchetti nel catalogo cosi generators e palette_for possano usarli, mantenendo la regola non negoziabile: nessun path res://packs/<ID>/... nel catalogo puo referenziare un pack assente dal manifest del template finale.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Elenco dei nuovi pacchetti asset di Jay raccolto e documentato (nome pack, id, provenienza)
- [x] #2 Individuate o prodotte mappe/template sorgente reali che usano questi pacchetti, necessarie a ddforge catalog per estrarne le texture
- [x] #3 data/assets.json rigenerato con ddforge catalog --from includendo le nuove fonti, e verificato deterministico su una seconda generazione identica
- [x] #4 Nessuna voce del catalogo rigenerato referenzia un pack ID assente da header.asset_manifest del template (stesso invariante verificato in TASK-4)
- [x] #5 palette_for in assets.py aggiornato se i nuovi pacchetti introducono texture rilevanti per uno o piu degli 8 stili esistenti (dungeon, crypt, sewer, cave, tavern, manor, warehouse, city)
- [x] #6 Provenienza (elenco file sorgente usati, comando eseguito) documentata in docs/format.md §10 come per il catalogo esistente
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. rich_reference.dungeondraft_map modificato da Jay in DungeonDraft (52 pack in asset_manifest, prima 42; nuovi walls/patterns/portals/objects/roofs). Diffare la lista pack vecchia/nuova per ottenere l'elenco preciso dei nuovi pack (AC1).
2. Verificare quali file NovaMistralis usati in TASK-4 esistono ancora su disco (2 mancanti: Carcere_Nova.dungeondraft_map, Carcere_Nova_2.dungeondraft_map, rinominati/rimossi dalla campagna di Jay fuori dal nostro controllo). Usare rich_reference + gli 8 NovaMistralis rimasti come --from (AC2).
3. Rigenerare data/assets.json con ddforge catalog --from, verificare determinismo su due run identiche (AC3).
4. Verificare l'invariante nessun pack ID orfano sul catalogo rigenerato (AC4).
5. Confrontare vecchio/nuovo assets.json, valutare se le nuove texture sono rilevanti per uno o piu degli 8 stili e aggiornare palette_for in assets.py di conseguenza (AC5).
6. Aggiornare test_cli_validate_inspect.py (asserzione hardcoded 42 pack -> 52) per riflettere il nuovo rich_reference.
7. Documentare in docs/format.md: nota su rich_reference non piu byte-identico alla sorgente pristina, nuovi pack in tabella id/nome/autore/versione, nuova provenienza catalogo in §10 (comando, elenco file, nota sui 2 file NovaMistralis mancanti, nuovo conteggio) (AC6).
8. Girare l'intera suite pytest, zero regressioni.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Trovata collisione: rich_reference.dungeondraft_map modificato in-place da Jay (era read-only/pristino), 42->52 pack in asset_manifest. Utente ha scelto di tenerlo come nuovo riferimento canonico (test 'Pack referenziati (42)' da aggiornare a 52). Rigenerato data/assets.json (scratch, non ancora committato) con rich_reference + 8/10 file NovaMistralis originali di TASK-4 (Carcere_Nova.dungeondraft_map e Carcere_Nova_2.dungeondraft_map non piu' presenti su disco, rinominati/rimossi dalla campagna di Jay, fuori controllo): 52 pack, determinismo verificato (2 run identiche), zero pack orfani verificato. Confronto vecchio/nuovo catalogo: dei 10 nuovi pack solo 1 (6VxwaRdj, BB 51 Assets Houses1) ha texture realmente disegnate nel file (2 object House11/House12 - confermato da Jay essere il pack scelto per TASK-46 edifici citta'). Gli altri 9 pack sono nel manifest ma senza controparte disegnata, quindi non entrano nel catalogo. Jay ha chiesto l'elenco dei 9 pack ancora da popolare e di aspettare conferma prima di procedere con la rigenerazione finale/documentazione. In attesa.

Risolto un problema critico scoperto durante la rigenerazione: 2 dei 10 file sorgente NovaMistralis di TASK-4 (Carcere_Nova.dungeondraft_map, Carcere_Nova_2.dungeondraft_map) risultavano cancellati nella working tree del repo NovaMistralis (lavoro di campagna in corso di Jay). Omitterli avrebbe rotto palette_for per 7 stili su 8 (chiavi come brazier, archway, wood_planks, rug_01, crate, fountain_stone_01 sarebbero sparite dal catalogo). Recuperati in sola lettura dall'ultimo commit di quel repo (git show fda264f, nessuna modifica al repo NovaMistralis) e usati come --from al posto dei file assenti su disco.

Scoperto e corretto un secondo problema: gli alias semantici bed/bookshelf (OBJECT_ALIASES in assets.py) si agganciano al primo file osservato il cui nome li contiene, nell'ordine dei --from. Con rich_reference.dungeondraft_map come prima fonte, i nuovi oggetti dei pack sWxkyx98/OfL7DytA avrebbero silenziosamente dirottato tavern.accents['bed'] e manor.accents['bookshelf'] dalle texture di sempre (gia approvate al gate umano) a texture nuove mai viste da Jay in quel contesto -- nessun errore di validazione (i pack sono comunque nel manifest di blank_80x80.dungeondraft_map) ma una deriva visiva non richiesta. Corretto ripuntando entrambi alla chiave letterale (bed_wood_single_01, bookshelf_wood_01) invece dell'alias, stesso schema di correzione gia usato in TASK-29. Verificato che tutti e 8 gli stili producono esattamente le stesse texture di prima del cambiamento (confronto diretto pre/post fix).

Scoperto durante il lavoro che anche templates/blank_80x80.dungeondraft_map (skeleton di produzione, prima 1 solo pack FA30DDXY) e stato salvato da Jay in Dungeondraft con lo stesso progetto e ora referenzia 52 pack (0 elementi disegnati, invariato). Questo e cio che rende sicuro l'uso dei nuovi pack: senza, ogni texture dei nuovi pack in palette_for avrebbe rotto DDF014 sulle mappe generate in produzione (che partono sempre da blank_80x80). Effetto collaterale: 2 golden file (bsp_seed_1337.json, building_tavern_seed_1337.json) confrontano il documento intero incluso header.asset_manifest, quindi sono diventati stale per il solo cambio di manifest del template (contenuto/layout generato invariato, verificato a mano nel diff). Rigenerati con lo stesso script gia documentato nei rispettivi file di test.

data/assets.json rigenerato: 51 pack (44 prima), 6 walls, 6 floors, 15 portals, 1 roof, 59 objects (46 prima). Diff col catalogo precedente: solo 13 oggetti nuovi aggiunti, zero chiavi rimosse o modificate. Determinismo verificato (2 run, diff vuoto). Zero pack orfani verificato con script dedicato. palette_for(style, catalog) verificato per tutti gli 8 stili, sia prima che dopo la correzione alias, con lo stesso output di texture.

Non aggiunte le texture dei nuovi pack a _STYLE_DEFINITIONS: nessun gap reale da colmare negli 8 stili esistenti (muro/pavimento/porta/tetto gia tutti popolati con texture gia approvate). L'unica candidata ovvia -- gli object casa del pack 6VxwaRdj (BB 51 Assets Houses1, confermato da Jay come il pack scelto per TASK-46) -- non e un accent da sparpagliare in una stanza ma l'edificio intero da piazzare per lotto: resta catalogata, in attesa che TASK-46 la usi. Commento aggiunto su TASK-46 con questa nota.

Suite completa: 475 passed, 1 skipped, zero regressioni. Aggiornato tests/test_cli_validate_inspect.py (asserzione hardcoded 42->51 pack per il nuovo rich_reference.dungeondraft_map). Documentazione aggiornata in docs/format.md: §1 (rich_reference/blank_80x80 non piu pristini, nota sulla modifica manuale di Jay), §2 (tabella pack id/nome/autore/versione aggiornata a 51 voci), §10.1 (nuova provenienza TASK-45: elenco file, comando, recupero git dei 2 file mancanti, risultato numerico, decisione su palette_for, fix alias).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
data/assets.json rigenerato con i 9 pack nuovi installati da Jay (10 meno BasePackRemade Colored, scartato su richiesta): 51 pack (44 prima), 59 objects (46 prima), zero chiavi preesistenti rimosse. Determinismo e assenza di pack orfani verificati con script dedicati. Durante il lavoro risolti due problemi scoperti: (1) 2 file NovaMistralis usati da TASK-4 risultavano cancellati sul disco (lavoro di campagna di Jay in corso) e sono stati recuperati in sola lettura dall'ultimo commit del repo NovaMistralis, altrimenti la rigenerazione avrebbe rotto palette_for per 7 stili su 8; (2) gli alias semantici bed/bookshelf si erano silenziosamente riassegnati alle texture dei pack nuovi per un problema di ordine dei --from, corretto ripuntandoli alla chiave letterale (stesso schema di TASK-29) cosi tavern/manor restano visivamente identici a prima. palette_for non aggiornato con le nuove texture: nessun gap reale negli 8 stili esistenti; gli object casa di 6VxwaRdj (confermato pack scelto per TASK-46) restano catalogati in attesa che quel task li usi. blank_80x80.dungeondraft_map risultava anch'esso aggiornato da Jay (52 pack nel manifest, 0 elementi), il che rende sicuro l'uso futuro dei nuovi pack contro DDF014; effetto collaterale: 2 golden file (bsp, building) sono stati rigenerati perche confrontavano l'header intero. Documentazione aggiornata in docs/format.md §1/§2/§10.1. Suite completa verde: 475 passed, 1 skipped.
<!-- SECTION:FINAL_SUMMARY:END -->
