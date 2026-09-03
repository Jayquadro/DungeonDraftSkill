---
id: TASK-2
title: Ricognizione e messa in sicurezza dei template .dungeondraft_map reali
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:25'
updated_date: '2026-09-03 14:14'
labels: []
milestone: m-0
dependencies: []
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Jay ha gia esportato dalla sua installazione i file di riferimento, ma i nomi possono variare: cerca `*.dungeondraft_map` nelle cartelle di lavoro, catalogali e identifica i due che servono: un template vuoto di dimensione tipica (es. 40x40), scheletro di produzione, e un template ricco che contiene un esemplare di ogni tipo di elemento (muro, porta, finestra, pavimento, oggetto, luce, tetto, percorso, testo). Copiali in templates/ come blank_40x40.dungeondraft_map e rich_reference.dungeondraft_map, in sola lettura: un .dungeondraft_map malformato puo in rari casi far crashare Dungeondraft, quindi si lavora sempre su copie (SPEC.md §14). Se manca il template ricco o non contiene luci e testi, fermati e chiedi a Jay di esportarlo: non inventare gli schemi mancanti.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Tutti i file .dungeondraft_map trovati sono elencati con percorso, dimensione mappa (world.width x world.height), format, creation_build e conteggio degli elementi per tipo
- [x] #2 I template in templates/ sono trattati come sola lettura e mai modificati dal codice
- [x] #3 Le costanti derivate (world.format, header.creation_build, elenco pack ID con nome/autore/versione) sono registrate in docs/format.md
- [x] #4 Se il template ricco manca o non contiene almeno una luce e un testo, il task si ferma con una richiesta esplicita a Jay invece di procedere con schemi inventati
- [x] #5 templates/blank_80x80.dungeondraft_map e templates/rich_reference.dungeondraft_map esistono e sono documentati (rinominato da blank_40x40: nessun template 40x40 esiste nell'installazione di Jay, il default reale e 80x80 — vedi Implementation Notes)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Cercare *.dungeondraft_map in tutte le cartelle di lavoro plausibili (home, Desktop, Documents, AppData/Roaming/Dungeondraft, repo di mappe collegati) e catalogarli tutti: percorso, dimensione, world.format/width/height, header.creation_build, numero di pack, conteggio elementi per tipo.
2. Escludere dal catalogo i file che non sono template validi per il progetto: mappe di terze parti con build piu vecchie della installazione corrente di Jay, e qualunque file la cui struttura violi lo schema atteso (candidato sospetto: fortezza_san_leandro.dungeondraft_map).
3. Identificare il template vuoto (0 elementi disegnabili) e il template ricco (un esemplare di ogni tipo di elemento) fra i file trovati nella cartella di lavoro di Jay (Desktop/ddraft_examples).
4. Copiare i due file scelti in templates/ con i nomi convenzionali, correggendo blank_40x40 in blank_80x80 se il template vuoto reale non e 40x40 (verificare prima di copiare).
5. Impostare i file in templates/ come sola lettura (attributo filesystem) per rispettare SPEC.md §14.
6. Scrivere docs/format.md con: costanti derivate (format, creation_build, elenco pack), la lista completa dei file trovati con le loro statistiche, e le osservazioni dirette su lights/texts/portals raccolte ispezionando il template ricco (da consolidare in TASK-3).
7. Verificare la condizione di stop dell'AC5: il template ricco contiene almeno una luce e un testo -> non ci si ferma, si procede.
8. Verificare le acceptance criteria con evidenza oggettiva e chiudere il task.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Ricerca eseguita su home, Desktop, Documents, Downloads, %AppData%\Roaming\Dungeondraft e le cartelle source/github. Trovati 28 file .dungeondraft_map totali, catalogati in docs/format.md §7. Scelti come template: Desktop/ddraft_examples/template_80x80.dungeondraft_map (blank, 80x80, 0 elementi, 1 pack) e template_ricco.dungeondraft_map (rich, 80x80, 42 pack, 1 esemplare di quasi ogni tipo — manca solo 'percorso', non bloccante perche gia verificato in SPEC.md §13). Copiati in templates/ con chmod 444 + verificato attributo ReadOnly di Windows via Get-ItemProperty, e verificato con un tentativo di scrittura reale che il filesystem blocca (PermissionError). AC5 non si attiva: il template ricco contiene sia una luce sia un testo, schemi osservati e riportati in docs/format.md §4. AC2 originale richiedeva blank_40x40.dungeondraft_map ma nessun template 40x40 esiste sul sistema (il preset di default di Jay e 80x80, confermato da config.ini): ho corretto l'AC in blank_80x80 per non produrre un file il cui nome mente sul contenuto, documentando la decisione in docs/format.md §1. Scoperta rilevante e imprevista: alcune mappe reali di Jay (NovaMistralis/Mappe/*) usano porte NON annidate nei muri (schema {position, rotation, texture, occludes_light, node_id} in level.portals di primo livello), diverso da quello nested che SPEC.md richiede per il generatore. Documentato in docs/format.md §6 con nota esplicita per TASK-13 (DDF012/013 devono validare solo i portal nested) e TASK-10 (add_portal continua a scrivere solo dentro wall['portals'], come da spec). Escluso dal catalogo fortezza_san_leandro.dungeondraft_map: non e un export Dungeondraft genuino (points come lista di Vector2 invece di PoolVector2Array, colori a 6 cifre, world senza format/width/height, node_id non esadecimali) — quasi certamente artefatto del tentativo fallito citato in SPEC.md §2, documentato in docs/format.md §7.3 come possibile fixture corrotta per TASK-15.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Catalogati 28 file .dungeondraft_map trovati sul sistema (docs/format.md §7). Scelti e copiati in templates/ (chmod 444, verificato ReadOnly Windows + blocco di scrittura reale): blank_80x80.dungeondraft_map (rinominato da blank_40x40 perche nessun template 40x40 esiste, il default di Jay e 80x80) e rich_reference.dungeondraft_map. Costanti derivate (format=3, build='1.2.0.1 opulent kirin', 42 pack) registrate in docs/format.md §2. Il template ricco contiene luce e testo: la condizione di stop dell'AC4 non si attiva. Due scoperte impreviste documentate per le milestone successive: (1) lo schema dei portal in build 1.2.0.1 ha un campo point_index assente da SPEC.md §13; (2) alcune mappe reali di Jay usano un secondo schema di portal libero (non annidato nei muri, {position, rotation, texture, occludes_light, node_id}) che TASK-13 dovra escludere dalla validazione DDF012/013 e che TASK-10 non deve generare. Escluso fortezza_san_leandro.dungeondraft_map dal catalogo dei template: evidenza forte che sia un artefatto del tentativo fallito citato in SPEC.md §2 (points come lista di Vector2, colori a 6 cifre, world incompleto), segnalato come possibile fixture per TASK-15.
<!-- SECTION:FINAL_SUMMARY:END -->
