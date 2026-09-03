---
id: TASK-3
title: Derivare e documentare lo schema di lights e texts dal template ricco
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:25'
updated_date: '2026-09-03 14:19'
labels: []
milestone: m-0
dependencies:
  - TASK-2
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Lo schema di `lights` e `texts` NON e stato verificato nell'analisi che ha prodotto SPEC.md: nessuna delle mappe pubbliche analizzate ne conteneva (SPEC.md §3, §13). Va derivato leggendo il template ricco, campo per campo, e documentato in docs/format.md insieme al resto del formato verificato. Senza questo, add_light e add_text di build.py non sono implementabili: non inventare i campi.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 docs/format.md contiene lo schema completo di un elemento di level.lights: nome, tipo e valore osservato di ogni campo
- [x] #2 docs/format.md contiene lo schema completo di un elemento di level.texts, incluso come e codificato il contenuto testuale e il font
- [x] #3 Per ogni campo e indicato se e stato osservato direttamente nel template ricco o solo ipotizzato
- [x] #4 docs/format.md riporta anche lo schema verificato degli altri elementi (wall, portal, pattern, object, path, roof) come riferimento unico del progetto
- [x] #5 Se il template ricco non contiene luci o testi, il task si ferma e chiede a Jay un nuovo export invece di ipotizzare i campi
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Estrarre piu campioni di light e text dalle mappe reali di Jay (NovaMistralis, che hanno fino a 41 luci) per confermare tipi e range dei campi oltre al singolo esemplare del template ricco.
2. Determinare il significato di light.range/intensity/shadows e text.box_shape confrontando piu istanze.
3. Aggiornare docs/format.md: sezione lights/texts completa con provenienza di ogni campo (osservato nel rich template vs osservato solo nelle mappe reali vs ipotizzato), piu tabella riassuntiva di wall/portal/pattern/object/path/roof gia verificati in TASK-2 come riferimento unico.
4. Verificare che il template ricco contenga effettivamente luci e testi (gia confermato in TASK-2): non fermarsi.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Cross-check di 82 luci reali dalle mappe NovaMistralis (piu il campione gia noto di rich_reference): rivelato che esistono DUE varianti di light, non una — 'puntiforme' (position/range/color a 6 cifre/intensity/shadows/node_id, 82 campioni) e 'con sprite' (aggiunge rotation e texture, colore a 8 cifre ARGB, 1 solo campione in rich_reference). Documentato in docs/format.md §4 con provenienza di ogni campo. Nessun campione aggiuntivo di text trovato ne nelle altre mappe reali di Jay ne nelle mappe di terze parti in dungeondraft_maps/crosshead_style: resta un solo esemplare in tutto il progetto, box_shape resta non determinato e segnalato come tale. Aggiunta sezione §5 con lo schema consolidato di wall/portal/pattern/object/path/roof preso da SPEC.md §13, riferimento unico richiesto dall'AC4. Rinumerate le sezioni successive (vecchie §5-8 -> §6-9).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
docs/format.md §4 documenta lo schema di light (due varianti, 83 campioni totali analizzati) e text (1 campione, unico in tutto il progetto) con provenienza esplicita per ogni campo. Aggiunta §5 con lo schema consolidato di wall/portal/pattern/object/path/roof come riferimento unico. Condizione di stop non applicabile: rich_reference contiene luce e testo.
<!-- SECTION:FINAL_SUMMARY:END -->
