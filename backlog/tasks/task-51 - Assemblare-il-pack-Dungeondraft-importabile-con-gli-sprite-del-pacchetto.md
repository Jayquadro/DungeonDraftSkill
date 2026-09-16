---
id: TASK-51
title: Assemblare il pack Dungeondraft importabile con gli sprite del pacchetto
status: To Do
assignee: []
created_date: '2026-09-15 07:17'
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
- [ ] #1 Esiste un comando che, data la cartella dei PNG finali, assembla la cartella del pack con pack.json, textures/objects/, textures/terrain/, textures/patterns/normal/ e preview.png
- [ ] #2 pack.json contiene id, nome, autore e versione del pacchetto e l'id resta stabile fra una riassemblata e l'altra
- [ ] #3 Le soglie di custom_color_overrides scritte nel pack sono le stesse usate dalla normalizzazione del rosso di TASK-50
- [ ] #4 preview.png mostra tutti gli sprite del pacchetto affiancati e permette di giudicare la coerenza di tratto e saturazione
- [ ] #5 La documentazione spiega come ottenere il file .dungeondraft_pack a partire dalla cartella, con il packer di Dungeondraft, e cosa serve avere installato
- [ ] #6 Gate umano: Jay importa il pack in Dungeondraft, il software non da' errori e gli sprite compaiono nel pannello degli object
- [ ] #7 Gate umano: applicando un colore personalizzato a uno sprite in Dungeondraft cambia il tetto e non la pietra ne' il legno
<!-- AC:END -->
