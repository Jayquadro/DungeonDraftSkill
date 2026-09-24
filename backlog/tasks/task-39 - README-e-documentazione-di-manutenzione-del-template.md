---
id: TASK-39
title: README e documentazione di manutenzione del template
status: Done
assignee:
  - '@claude'
created_date: '2026-09-03 11:35'
updated_date: '2026-09-24 11:41'
labels: []
milestone: m-7
dependencies:
  - TASK-37
documentation:
  - docs/SPEC.md
priority: medium
type: docs
ordinal: 39000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Requisito esplicito della definizione di fatto (SPEC.md §15): il README deve spiegare come esportare un nuovo template quando Dungeondraft aggiorna il formato. È la procedura che tiene in vita il progetto negli anni, perché tutta l'architettura dipende dal template (SPEC.md §2). Vanno documentati anche installazione, uso del CLI, e le trappole di §14.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Il README spiega installazione, uso dei comandi generate, validate, inspect, catalog e preview
- [x] #2 Il README contiene la procedura passo-passo per esportare un nuovo template da Dungeondraft quando il formato cambia
- [x] #3 Il README rimanda a docs/format.md per lo schema e riassume le trappole di SPEC.md §14
- [x] #4 docs/format.md è aggiornato con tutto ciò che è stato calibrato nei gate umani di M1 e M3
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. AC1: riscrivere la sezione 'Uso' del README con un sottoparagrafo per comando (generate, validate, inspect, catalog, preview), con un esempio minimo eseguibile per ciascuno, preso da cli.py (argomenti reali: --template/--out/--width/--height/--rooms/--seed/--style/--lights/--furnish per generate; file singolo per validate/inspect; --from/--pack/--from-catalog/--base-pck/--base-include/--out per catalog; file/--out/--level/--scale per preview), rimandando a --help per l'elenco completo invece di duplicare ogni flag.
2. AC2: scrivere in README una procedura passo-passo 'Esportare un nuovo template quando Dungeondraft aggiorna il formato': (a) esportare da Dungeondraft un template vuoto e uno ricco con un esemplare di ogni elemento (muro/porta/finestra/pavimento/oggetto/luce/tetto/percorso/testo), mai modificare i template esistenti in place; (b) mettere i nuovi file in templates/ e ispezionarli con `ddforge inspect` (format, creation_build, dimensioni, pack) confrontandoli con i vecchi; (c) verificare a mano le chiavi di livello (LEVEL_KEYS in template.py) e le formule dei blob (tiles.cells, terrain.splat, cave.bitmap - docs/format.md §14) contro il nuovo file; (d) far girare pytest e in particolare i golden file e test_cave_bitmap_format.py per intercettare regressioni di formato; (e) se lo schema e cambiato (nuove chiavi, nuovi campi nei portal, ecc.) aggiornare template.py/validate.py e documentare la differenza in docs/format.md seguendo lo stile delle sezioni esistenti (mai inventare un valore: ispezionare il file reale); (f) rigenerare data/assets.json con `ddforge catalog --from-catalog` se compaiono nuovi pack; (g) ripetere il gate umano (generare un dungeon di prova e farlo aprire a Jay in Dungeondraft) prima di considerare il nuovo template pronto per la produzione.
3. AC3: nella sezione d'uso aggiungere un rimando esplicito a docs/format.md per lo schema completo, e un riepilogo breve (poche righe, non una copia) delle trappole di SPEC.md §14 (blob sintetizzati, points come lista invece di stringa, colori a 6 cifre, porte a livello mappa, next_node_id non aggiornato, pack id inventati, format diverso dalla build, coordinate in px nel world, path.edit_points assoluti, primo punto ripetuto con loop=true).
4. AC4: verificare se docs/format.md contiene gia tutto cio che e stato calibrato nei gate umani di M1 e M3 (sembra di si: sezioni 9.1-9.7 coprono direction/tangente, orientamento corridoi, muri di canale, attraversamenti, riproiezione porte, muri sovrapposti - tutte con riferimento a task e test). Se durante la stesura del README emergono lacune, integrarle in docs/format.md; altrimenti lasciare il file invariato e annotarlo nella nota finale del task.
5. Aggiornare la riga finale del README ('Esportare un nuovo template: Documentazione da completare in TASK-39...') con la procedura vera, rimuovendo il placeholder.
6. Rileggere il README finito per coerenza con lo stile del resto del documento (italiano, tono diretto, esempi bash reali) prima di chiudere il task.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
README.md riscritto: sezione Uso con un esempio minimo per ciascuno dei 5 sottocomandi (generate/validate/inspect/catalog/preview, verificati contro src/ddforge/cli.py e con 'ddforge --help' eseguito davvero), nuova sezione 'Schema del formato e trappole' che rimanda a docs/format.md e riassume la tabella di SPEC.md §14, e sezione 'Esportare un nuovo template' con la procedura in 7 passi (export da Dungeondraft, ddforge inspect, verifica formule blob, pytest, aggiornamento schema/documentazione, ricatalogazione incrementale, ripetizione del gate umano). Sezione 'Stato' obsoleta (diceva ancora 'bootstrap M0, moduli stub') corretta per riflettere M0-M5 completate. AC4: docs/format.md NON modificato — verificato che il §9 ('Regole definitive di orientamento e allineamento, gate umani M1 e M3') gia copre per intero le calibrazioni di quei due gate (tangente porta TASK-12, orientamento/instradamento corridoi e riproiezione porte TASK-26), con riferimenti a codice e test; sezioni citate nel README (§4, §9, §10, §10.2, §10.3, §11, §12, §14) verificate presenti con 'grep ^## '.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
README.md aggiornato con: (1) una sotto-sezione per ciascuno dei 5 sottocomandi CLI con esempio eseguibile, verificati contro cli.py e 'ddforge --help'; (2) sezione 'Schema del formato e trappole' che rimanda a docs/format.md e riassume la tabella delle trappole di SPEC.md §14; (3) procedura passo-passo in 7 punti per esportare un nuovo template quando Dungeondraft aggiorna il formato (export, ddforge inspect, verifica formule blob, pytest/golden file, aggiornamento schema e docs/format.md, ricatalogazione incrementale con --from-catalog, ripetizione del gate umano), al posto del placeholder 'da completare in TASK-39'. Sezione 'Stato' obsoleta corretta. docs/format.md non modificato: verificato (sezione §9, gate umani M1/M3) che contiene gia tutte le calibrazioni richieste dall'AC4.
<!-- SECTION:FINAL_SUMMARY:END -->
