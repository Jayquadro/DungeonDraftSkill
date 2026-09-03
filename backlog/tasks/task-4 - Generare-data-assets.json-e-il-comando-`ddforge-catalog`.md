---
id: TASK-4
title: Generare data/assets.json e il comando `ddforge catalog`
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:25'
updated_date: '2026-09-03 14:26'
labels: []
milestone: m-0
dependencies:
  - TASK-2
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Produrre il catalogo asset del progetto leggendo i template reali, con la struttura definita in SPEC.md §6.7: elenco packs (name, id, author, version) preso da header.asset_manifest, piu le mappe logiche walls/floors/portals/roofs/paths/objects verso i path texture res://. Regola non negoziabile: ogni path res://packs/<ID>/... deve avere <ID> presente in header.asset_manifest del template, altrimenti Dungeondraft segnala missing assets al caricamento. Il comando `ddforge catalog --from <template>` deve poter rigenerare il file quando Jay installa nuovi pack.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 data/assets.json esiste e contiene solo pack ID realmente presenti in header.asset_manifest dei template
- [x] #2 Ogni texture nel catalogo e verificata come esistente nel template o negli asset di default (uses_default_assets)
- [x] #3 Un test verifica che nessuna voce del catalogo referenzi un pack ID assente dal manifest
- [x] #4 Le categorie logiche previste in SPEC.md §6.7 (walls, floors, portals, roofs, objects; paths resta vuota, nessuna texture di percorso e mai stata osservata) sono popolate con texture reali estratte dai documenti sorgente, chiave = slug del nome file. Dove il nome semantico di SPEC.md (torch, table_round, chair, bed, crate, barrel, bookshelf, altar, sarcophagus, column, brazier, chest) corrisponde a una texture realmente osservata, e aggiunto come alias verso la stessa texture; le categorie senza controparte osservata in nessun file reale di Jay (verificato: torch, altar, sarcophagus, column, chest) restano assenti e documentate come tali, mai inventate
- [x] #5 `ddforge catalog --from <file1> --from <file2> ...` (opzione ripetibile) rigenera data/assets.json in modo deterministico dato lo stesso insieme di file sorgente; l'insieme usato per il file committato e elencato esplicitamente nella documentazione
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Implementare in assets.py: _slug (nome file -> chiave), _classify (path -> categoria per sottostringa /walls/, /patterns|tilesets/, /portals/, /roofs/, /paths/, /objects/), _iter_textures (cammina un documento e produce tutte le texture usate), build_catalog(*docs) che unisce piu documenti, raccoglie i pack da asset_manifest e popola le categorie con chiave=slug, valore=path reale, piu alias semantici verso i nomi di SPEC.md quando il filename li contiene.
2. Implementare load_catalog(path) per leggere data/assets.json.
3. Estendere cli.py: --from diventa ripetibile (action=append), aggiungere --out con default data/assets.json, implementare _cmd_catalog per caricare ogni file, chiamare build_catalog e scrivere il JSON con indent=2 ordinato.
4. Generare data/assets.json usando come sorgenti: templates/rich_reference.dungeondraft_map (la fonte canonica) piu le mappe reali della campagna di Jay in NovaMistralis (per arricchire walls/floors/portals/objects, che nel solo rich_reference sono troppo poveri) — documentare l'elenco esatto dei file usati.
5. Scrivere test: build_catalog su documenti fittizi minimi produce le categorie attese; nessuna voce referenzia un pack ID assente dal manifest; load_catalog legge il file scritto; la CLI e deterministica a parita di input.
6. Verificare con pytest ed eseguire il comando reale per rigenerare data/assets.json, controllando che il file sia identico a se stesso su una seconda esecuzione.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementato build_catalog/load_catalog in assets.py (classificazione per sottostringa di path, slug deterministico dal nome file, alias semantici verso i nomi di SPEC.md solo se una texture reale li contiene). CLI catalog esteso: --from ripetibile, --out configurabile. 9 test nuovi in tests/test_assets.py (classificazione, alias, merge multi-documento, nessun pack assente dal manifest, determinismo CLI via subprocess). Generato data/assets.json reale unendo rich_reference.dungeondraft_map con 10 mappe reali della campagna NovaMistralis di Jay (rich_reference da solo era troppo povero: 1 muro, 1 oggetto). Risultato: 44 pack, 6 walls, 6 floors, 15 portals, 1 roof, 0 paths, 46 oggetti. Verificato con script dedicato: zero voci che referenziano un pack ID assente dal manifest. Determinismo confermato rigenerando due volte lo stesso file e diffando (identici). 7 alias semantici popolati con texture reali (table_round, chair, bed, crate, barrel, bookshelf, brazier); 5 lasciati assenti perche nessun file reale di Jay li contiene (torch, altar, sarcophagus, column, chest) — documentato in docs/format.md §10, non inventati. Provenienza completa (elenco file, comando esatto) documentata in docs/format.md §10.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementato build_catalog/load_catalog (assets.py) e il comando ddforge catalog (--from ripetibile, --out configurabile). data/assets.json generato unendo rich_reference.dungeondraft_map con 10 mappe reali della campagna di Jay (necessario: il solo rich_reference era troppo povero). 44 pack, 6 walls, 6 floors, 15 portals, 1 roof, 46 objects, verificato senza pack ID orfani (script + test dedicato) e deterministico (diff di due generazioni identiche). 7/12 alias semantici di SPEC.md popolati con texture reali; i 5 senza controparte reale (torch, altar, sarcophagus, column, chest) restano assenti e documentati, mai inventati. Verificato con 9 test nuovi + suite completa (11 test totali) verde.
<!-- SECTION:FINAL_SUMMARY:END -->
