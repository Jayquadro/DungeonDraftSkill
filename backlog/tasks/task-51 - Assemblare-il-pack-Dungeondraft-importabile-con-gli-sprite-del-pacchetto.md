---
id: TASK-51
title: Assemblare il pack Dungeondraft importabile con gli sprite del pacchetto
status: Done
assignee:
  - '@claude'
created_date: '2026-09-15 07:17'
updated_date: '2026-09-17 12:03'
labels: []
milestone: m-9
dependencies:
  - TASK-50
references:
  - sprite-batch.zip
documentation:
  - docs/sprite-luoghi.md
priority: high
type: feature
ordinal: 52000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Una volta che gli sprite sono scontornati e normalizzati (TASK-50) restano dei PNG sciolti: Dungeondraft non li vede finche' non stanno in un pack con i suoi metadati. Serve produrre il pacchetto vero e proprio, quello che Jay importa dal menu dei pack del software.

Struttura attesa, quella che il packer di Dungeondraft si aspetta: una cartella del pack con pack.json (id, nome, autore, versione), textures/objects/ per gli sprite, textures/terrain/ e textures/patterns/normal/ per le eventuali texture di terreno, e una preview.png che mostri tutti gli sprite affiancati per giudicare a colpo d'occhio la coerenza del tratto. Il file .dungeondraft_pack finale lo produce il packer ufficiale del software a partire da quella cartella: la procedura deve dire come invocarlo e cosa fare se non e' disponibile.

Va deciso e scritto anche il resto dei metadati che servono a far funzionare la ricolorabilita' dei tetti: le soglie di custom_color_overrides (min_redness, min_saturation, red_tolerance) devono essere coerenti con la normalizzazione del rosso fatta in TASK-50, altrimenti i tetti non cambiano colore sulla mappa o si ricolora anche la pietra.

sprite-batch.zip contiene gia' un modulo pack.py che assembla questa cartella: vale come punto di partenza, come per TASK-50.

L'esito e' verificato da Jay: il pack si importa in Dungeondraft senza errori e gli sprite compaiono nel pannello degli object con l'anteprima giusta.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Esiste un comando che, data la cartella dei PNG finali, assembla la cartella del pack con pack.json, textures/objects/, textures/terrain/, textures/patterns/normal/ e preview.png
- [x] #2 pack.json contiene id, nome, autore e versione del pacchetto e l'id resta stabile fra una riassemblata e l'altra
- [ ] #3 Le soglie di custom_color_overrides scritte nel pack sono le stesse usate dalla normalizzazione del rosso di TASK-50
- [x] #4 preview.png mostra tutti gli sprite del pacchetto affiancati e permette di giudicare la coerenza di tratto e saturazione
- [x] #5 La documentazione spiega come ottenere il file .dungeondraft_pack a partire dalla cartella, con il packer di Dungeondraft, e cosa serve avere installato
- [x] #6 Gate umano: Jay importa il pack in Dungeondraft, il software non da' errori e gli sprite compaiono nel pannello degli object
- [ ] #7 Gate umano: applicando un colore personalizzato a uno sprite in Dungeondraft cambia il tetto e non la pietra ne' il legno
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Nuovo modulo src/ddforge/pack_build/ (settings.py, metadata.py, preview.py, builder.py, cli.py), a fianco di sprite_prep/ (TASK-50) senza toccarlo: import di ddforge.sprite_prep.manifest.MANIFEST (quali PNG assemblare, gia' filtrato/validato da TASK-50) e ddforge.sprite_prep.settings.RedSettings (stesse soglie usate per normalizzare i tetti - AC3, nessun numero duplicato).
2. settings.PackSettings (name/folder/author/version) con i default di sprite-batch.zip/catalogo.yaml (pacchetto: nome "Nova Mistralis Citta", cartella NovaMistralisCitta, autore Jay, versione 1.0), sovrascrivibili da CLI.
3. builder.resolve_pack_id(id_file): se il file esiste ne rilegge il contenuto, altrimenti genera 8 char alfanumerici (secrets.choice, stesso schema degli id reali osservati nei fixture, es. 6VxwaRdj) e lo scrive. File tracciato in git (data/pack_id.txt, non nella dist/ ignorata) cosi' l'id resta stabile fra una riassemblata e l'altra anche se dist/ viene ripulita (AC2).
4. metadata.build_pack_json(pack, red, pack_id): schema verificato su file .dungeondraft_map reali (docs/SPEC.md §13, tests/fixtures/*): name, id, version, author, keywords=null, allow_3rd_party_mapping_software_to_read=false, custom_color_overrides={enabled: true (deve ricolorare, AC7), min_redness/min_saturation/red_tolerance dagli stessi RedSettings di TASK-50}.
5. builder.assemble_pack(sprites_dir, dist_dir, pack, red, id_file): crea dist_dir/<folder>/{pack.json, textures/objects/ (i PNG del manifest presenti in sprites_dir), textures/terrain/, textures/patterns/normal/ (vuote oggi: nessuna voce C7/texture nel manifest ancora), preview.png}. Copia solo i file con una voce nel manifest di TASK-50 (stessa disciplina "niente elaborato a caso"); segnala mancanti senza fallire silenziosamente. preview.py: contact sheet con tutti gli sprite copiati affiancati (miniatura + etichetta), sfondo pergamena, adattato da sprite-batch.zip/spritebatch/pack.py::contact_sheet.
6. cli.py + scripts/build_pack.py, stesso pattern di scripts/prepare_sprites.py: --input assets/sprites (default) --output dist (default, gia' in .gitignore) --id-file data/pack_id.txt --name/--author/--version opzionali. Stampa riepilogo, exit code diverso da zero se mancano sprite del manifest.
7. docs/pack-assembly.md: comando, struttura prodotta, provenienza delle soglie di custom_color_overrides (identiche a TASK-50), come ottenere il .dungeondraft_pack finale col packer ufficiale di Dungeondraft (flusso "Custom Assets" -> cartella in Documents/Dungeondraft/unpacked_assets/ -> Package, da confermare sulla macchina di Jay: nessun riferimento nel repo lo conferma) e cosa fare se il packer non e' disponibile (consegnare la cartella cosi' com'e', Dungeondraft la carica anche non impacchettata in modalita' sviluppo).
8. tests/test_pack_build.py: resolve_pack_id stabile fra due chiamate sullo stesso file e nel formato giusto quando generato; build_pack_json usa esattamente le soglie di sprite_prep.settings.RedSettings ed enabled=true; assemble_pack copia solo i file presenti (segnala i mancanti), crea le 4 cartelle sempre, scrive preview.png solo se c'e' almeno uno sprite copiato, id stabile su una seconda chiamata. pytest -q sull'intera suite verde.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementata in src/ddforge/pack_build/ (settings.py, metadata.py, preview.py, builder.py, cli.py) + entry point scripts/build_pack.py + doc docs/pack-assembly.md + test tests/test_pack_build.py (11 test). Non ha toccato src/ddforge/sprite_prep/ (TASK-50): riusa MANIFEST (quali PNG assemblare) e RedSettings (soglie custom_color_overrides) per import, nessun numero duplicato.

Decisioni prese (AC libero nel brief, come per TASK-50): pack.json segue lo schema verificato su .dungeondraft_map reali (docs/SPEC.md §13, tests/fixtures/*), non lo schema semplificato di sprite-batch.zip/spritebatch/pack.py (che omette keywords/allow_3rd_party e mette enabled=false di default). enabled=true perche' senza non ricolora nulla (gate AC7). Id del pack persistito in data/pack_id.txt, tracciato in git (non nella dist/ ignorata) cosi' resta stabile anche se dist/ viene ripulita fra una riassemblata e l'altra. Metadati di default (nome "Nova Mistralis Citta", cartella NovaMistralisCitta, autore Jay, versione 1.0) identici a sprite-batch.zip/catalogo.yaml, sovrascrivibili da CLI. textures/terrain/ e textures/patterns/normal/ create sempre (anche vuote oggi: il manifest di TASK-50 non ha ancora voci di terreno C7).

Verifica oggettiva:
- pytest -q sull'intera suite: 785 passed, 1 skipped (preesistente, non collegato), 0 failed (774 prima di questa modifica, +11 i nuovi test).
- python scripts/build_pack.py sui 27 PNG reali di assets/sprites/: dist/NovaMistralisCitta/ con pack.json, preview.png, textures/objects/ (27 file), textures/terrain/, textures/patterns/normal/ (vuote); 0 mancanti.
- pack.json ispezionato: id 8 char alfanumerici (formato dei pack id reali osservati nei fixture), custom_color_overrides.{min_redness,min_saturation,red_tolerance} = 0.1/0.0/0.04, identici a ddforge.sprite_prep.settings.RedSettings (TASK-50), enabled=true.
- Riassemblato due volte (una in tmp, una reale su dist/): stesso pack_id in data/pack_id.txt in entrambi i casi.
- preview.png aperto e ispezionato visivamente: 27 miniature con etichetta, sfondo pergamena, tetti rosso saturo uniforme visibile su tutto il pacchetto.

Aggiornamento post TASK-53: pack.json ora con custom_color_overrides.enabled=false (niente piu' RedSettings in pack_build). AC3 scheccato (non piu' pertinente), AC7 resta non spuntato ma non piu' rilevante (nessuna ricolorazione offerta dal pack). Unico gate umano ancora aperto: AC6 (import pulito in Dungeondraft).

Gate umano confermato da Jay (2026-09-17): 'il package che ho creato funziona bene'. AC6 spuntata.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-17 10:05
---
TASK-53 (terzo giro, 2026-09-17): Jay ha rinunciato del tutto al canale di ricolorabilita' di Dungeondraft dopo due giri di correzione insufficienti sulla normalizzazione del rosso dei tetti. Il pack ora scrive custom_color_overrides.enabled=false invece di true.

Conseguenze su questo task:
- AC #3 ("le soglie... sono le stesse usate dalla normalizzazione del rosso di TASK-50") non ha piu' senso cosi' com'e': TASK-50 non normalizza piu' il rosso, quindi non esiste piu' una normalizzazione con cui essere coerenti. Scheccato. pack_build/metadata.py non dipende piu' da ddforge.sprite_prep.settings.RedSettings (rimosso, TASK-53): i tre numeri di custom_color_overrides restano solo come campi richiesti dallo schema osservato, inerti con enabled=false.
- AC #7 ("applicando un colore personalizzato... cambia il tetto e non la pietra ne' il legno") e' superato dagli eventi: con enabled=false il pack non offre affatto la ricolorazione in Dungeondraft, quindi il test descritto dall'AC non ha piu' un'azione da compiere. Resta non spuntato perche' non e' piu' verificabile ne' rilevante, non perche' manchi lavoro.
- AC #6 (gate umano: import pulito, sprite visibili nel pannello degli object) resta invariato e pienamente valido: e' l'unico gate umano ancora da chiudere per questo task.

Pack riassemblato con lo stesso pack_id (Ada7IQuz) e i PNG rigenerati senza normalizzazione del colore (TASK-53); dist/NovaMistralisCitta/pack.json e preview.png aggiornati di conseguenza.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Aggiunto l'assemblaggio del pack Dungeondraft (src/ddforge/pack_build/ + scripts/build_pack.py): dato assets/sprites/ (i PNG di TASK-50), produce dist/NovaMistralisCitta/ con pack.json, textures/objects/ con tutti gli sprite del manifest, textures/terrain/ e textures/patterns/normal/ (vuote: nessuna texture di terreno nel manifest ancora) e preview.png (tutti gli sprite affiancati con etichetta). L'id del pack e' persistito in data/pack_id.txt (tracciato in git) e resta stabile fra una riassemblata e l'altra.

Dopo TASK-53 (Jay ha rinunciato al canale di ricolorabilita' di Dungeondraft dopo due giri di bug nella normalizzazione del rosso), pack.json scrive custom_color_overrides.enabled=false invece di true: AC #3 e #7, che presupponevano quel canale, sono scheccati come superati dagli eventi (non piu' pertinenti, non per lavoro mancante) - dettagli nel commento sul task.

Verificato con: pytest sull'intera suite verde, esecuzione reale su assets/sprites/ (27 sprite, 0 mancanti), doppia riassemblata con id_file invariato (stesso id), ispezione visiva di preview.png, e gate umano di Jay: "il package che ho creato funziona bene" (import pulito in Dungeondraft, sprite visibili nel pannello degli object, AC6).

Documentato in docs/pack-assembly.md, incluso come ottenere il .dungeondraft_pack finale dal packer ufficiale di Dungeondraft.
<!-- SECTION:FINAL_SUMMARY:END -->
