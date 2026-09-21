---
id: TASK-61
title: >-
  Elaborare gli sprite grezzi di Palazzo, Arena e Cattedrale con la procedura
  sprite_prep
status: Done
assignee:
  - '@claude'
created_date: '2026-09-21 07:48'
updated_date: '2026-09-21 08:12'
labels: []
dependencies: []
references:
  - prompt/26-palazzo.md
  - prompt/27-arena.md
  - prompt/28-cattedrale.md
  - TASK-50
documentation:
  - docs/sprite-postprocessing.md
priority: high
ordinal: 62000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
assets/palazzo.jpg, assets/arena.jpg e assets/cattedrale.jpg sono i JPEG grezzi generati da Jay per i tre monumenti commissionati in TASK-55/TASK-57/TASK-58 (schede prompt/26-palazzo.md, prompt/27-arena.md, prompt/28-cattedrale.md), ma non sono ancora registrati nel manifest di src/ddforge/sprite_prep/manifest.py ne' passati nella procedura di post-processing introdotta in TASK-50 (scripts/prepare_sprites.py). Vanno aggiunti al manifest ed elaborati fino a PNG pronti per il pack, con gli stessi numeri gia' usati per gli altri sprite C1 (accademia, monastero).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Il manifest (src/ddforge/sprite_prep/manifest.py) include voci per palazzo.jpg, arena.jpg e cattedrale.jpg mappate su nm_palazzo, nm_arena, nm_cattedrale, categoria C1 canvas 1024, coerenti con le tabelle di intestazione di prompt/26, prompt/27, prompt/28
- [x] #2 scripts/prepare_sprites.py elabora i tre file senza errori e produce nm_palazzo.png, nm_arena.png, nm_cattedrale.png in assets/sprites/ con canale alfa reale, margine trasparente 5% e canvas 1024x1024
- [x] #3 I tre PNG risultanti sono versionati nel repo e assets/sprites/rapporto.json e' aggiornato di conseguenza
- [x] #4 pytest -q sull'intera suite passa dopo l'aggiunta delle voci al manifest
- [x] #5 Il rapporto della procedura non segnala controlli falliti per i tre sprite (alfa, margine, canvas quadrato, soggetto che tocca il bordo); eventuali avvisi legittimi sono documentati
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Aggiungere al manifest (src/ddforge/sprite_prep/manifest.py) tre SpriteJob: palazzo.jpg -> nm_palazzo C1, arena.jpg -> nm_arena C1, cattedrale.jpg -> nm_cattedrale C1, in continuita' con le voci C1 esistenti (accademia, monastero), scale_mode default 'canvas'.
2. Eseguire python scripts/prepare_sprites.py --input assets --output assets/sprites --only palazzo,arena,cattedrale e leggere rapporto.json per controllare warning/errori sui tre sprite.
3. Ispezionare visivamente i 3 PNG (Read) per verificare sfondo trasparente pulito, ombra, nessuna frangia magenta.
4. Eseguire il batch completo su tutti i 30 file (senza --only) per rigenerare rapporto.json coerente con l'intero manifest e versionare i nuovi PNG + il rapporto aggiornato.
5. pytest -q sull'intera suite.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Manifest esteso con 3 SpriteJob C1 (palazzo, arena, cattedrale), canvas 1024, scale_mode canvas, coerenti con prompt/26-27-28 e le altre voci C1 (accademia, monastero).

Batch --only palazzo,arena,cattedrale: 3/3 ok, 0 avvisi. Ispezione visiva dei 3 PNG: sfondo trasparente pulito, ombra, nessun residuo magenta; palazzo mostra corte interna (non castello isolato), arena anfiteatro ellittico a gradinate, cattedrale pianta cruciforme piu' grande del tempio.

Batch completo (30 file, tutto il manifest): 29 ok, 1 avviso preesistente su nm_cimitero_lapide_1 (proporzioni, gia' noto da TASK-50, non collegato ai tre nuovi sprite). assets/sprites/rapporto.json rigenerato.

pytest -q sull'intera suite: 779 passed, 1 skipped (preesistente), 0 failed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Aggiunte al manifest di src/ddforge/sprite_prep/ le voci per palazzo.jpg, arena.jpg, cattedrale.jpg (C1, 1024x1024) ed eseguita la procedura scripts/prepare_sprites.py su tutto assets/: nm_palazzo.png, nm_arena.png, nm_cattedrale.png prodotti senza avvisi, con canale alfa, margine e canvas corretti. Verificato con: output del batch (3/3 ok poi 29/30 ok con l'unico avviso preesistente non collegato), ispezione visiva dei 3 PNG, pytest -q sull'intera suite (779 passed, 1 skipped preesistente, 0 failed). File nuovi/modificati non ancora committati: assets/sprites/nm_{palazzo,arena,cattedrale}.png, assets/sprites/rapporto.json, src/ddforge/sprite_prep/manifest.py.
<!-- SECTION:FINAL_SUMMARY:END -->
