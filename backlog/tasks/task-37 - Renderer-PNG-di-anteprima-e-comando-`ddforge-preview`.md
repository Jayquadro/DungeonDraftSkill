---
id: TASK-37
title: Renderer PNG di anteprima e comando `ddforge preview`
status: Done
assignee:
  - '@claude'
created_date: '2026-09-03 11:35'
updated_date: '2026-09-08 14:13'
labels: []
milestone: m-6
dependencies:
  - TASK-26
documentation:
  - docs/SPEC.md
priority: medium
type: feature
ordinal: 37000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Anteprima raster della planimetria senza dover aprire Dungeondraft (SPEC.md §1.3, §5, §8). Unico punto del progetto in cui è ammessa una dipendenza esterna, Pillow, che deve restare opzionale: il core continua a funzionare senza. Il renderer legge il .dungeondraft_map generato, non il Blueprint, così l'anteprima verifica davvero ciò che è stato scritto sul file.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 ddforge preview <file.dungeondraft_map> produce un PNG leggibile della planimetria
- [x] #2 Il PNG mostra muri, porte, pavimenti e oggetti in modo distinguibile
- [x] #3 Il renderer legge il file .dungeondraft_map, non il Blueprint in memoria
- [x] #4 Pillow è una dipendenza opzionale: il core e gli altri comandi funzionano senza averla installata
- [x] #5 Se Pillow manca, il comando preview lo dice con un messaggio chiaro invece di un traceback
- [x] #6 Il comando è coperto da test che verificano la produzione del PNG
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Nuovo modulo src/ddforge/preview.py: render_preview(doc, out_path, *, level_id=None, scale=8). Importa Pillow pigramente (solo qui in tutto il progetto); se manca, solleva PillowMissingError con messaggio chiaro (AC4/AC5).
2. Legge SOLO il documento .dungeondraft_map gia caricato da JSON (AC3): sceglie il livello (default il primo, es. '0'), disegna in ordine background -> cave.bitmap nativo (decode_cave_bitmap, se presente, per i generatori cave/decision-1) -> patterns (pavimenti) -> muri (linee spesse) -> porte (marker colorato sulla posizione del portal, distinguibile dai muri) -> oggetti (quadratini colorati) (AC2).
3. Nessuna dipendenza da Blueprint/model: legge solo points/position/texture dal JSON, coerente con "verifica cio che e stato scritto sul file" (AC3).
4. cli.py: implementa _cmd_preview usando render_preview; aggiunge --out/--level/--scale al subparser preview; messaggi di errore chiari (file mancante/JSON invalido gia gestiti da _load_document, Pillow mancante e livello inesistente via preview.py).
5. pyproject.toml: extra 'preview' con Pillow>=10 gia presente, nessuna modifica al core (dependencies resta []) (AC4).
6. Test (tests/test_preview.py): unit su render_preview con pytest.importorskip("PIL") per i test che producono davvero un PNG (dimensioni, apertura con Image.open); test del messaggio "Pillow mancante" via monkeypatch sys.modules['PIL']=None (non serve Pillow disinstallato); test CLI end-to-end (genera una dungeon in tmp_path via subprocess, poi ddforge preview su di essa, verifica file .png scritto) (AC6).
7. Installo Pillow nel venv locale (extra dev) solo per eseguire davvero i test e verificare a occhio un PNG di esempio prima di chiudere il task.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementato src/ddforge/preview.py: render_preview(doc, out_path, level_id=None, scale=8) legge SOLO il documento .dungeondraft_map gia caricato (nessun import di model/compose/Blueprint), sceglie il primo livello per default, disegna in ordine: cave.bitmap nativo decodificato via cave_bitmap.decode_cave_bitmap (grotte, decision-1) -> patterns (pavimenti, tan) -> muri (linee nere spesse, loop chiuso se wall['loop']) -> porte (marker arancione sulla posizione del portal annidato) -> oggetti (quadratini teal). Pillow importato pigramente solo in _require_pillow(), mai a livello di modulo: PillowMissingError con messaggio "pip install ddforge[preview]" se assente, nessun altro comando ne risente (nessun import di ddforge.preview fuori da _cmd_preview).
cli.py: _cmd_preview implementato, subparser preview esteso con --out/--level/--scale.
Verifica: 486 test verdi (475 preesistenti + 11 nuovi in tests/test_preview.py, 1 skip preesistente non correlato). I test che producono un PNG vero usano pytest.importorskip("PIL") (installato in locale via pip install -e .[preview] per eseguirli davvero); il test del messaggio Pillow-mancante forza sys.modules['PIL']=None, non richiede disinstallazione. Verifica visiva: preview di generated/dungeon_m3.dungeondraft_map (stanze/corridoi/porte/oggetti chiaramente distinguibili) e generated/cave_m5.dungeondraft_map (bitmap nativo leggibile, forma organica corretta) ispezionate a occhio.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Aggiunto src/ddforge/preview.py (render_preview) e implementato ddforge preview <file> [--out] [--level] [--scale] in cli.py. Il renderer legge il documento .dungeondraft_map gia scritto su disco (mai il Blueprint), disegna muri/porte/pavimenti/oggetti con colori distinti e decodifica cave.bitmap per le grotte native. Pillow resta opzionale: import pigro, PillowMissingError con messaggio chiaro se assente, nessun altro comando ne dipende. Verificato con 486 test verdi (11 nuovi in tests/test_preview.py, coprono AC1-AC6) e ispezione visiva di due PNG generati da mappe reali del progetto (dungeon e cave).
<!-- SECTION:FINAL_SUMMARY:END -->
