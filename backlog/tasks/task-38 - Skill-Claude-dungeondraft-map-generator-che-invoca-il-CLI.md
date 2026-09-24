---
id: TASK-38
title: Skill Claude dungeondraft-map-generator che invoca il CLI
status: Done
assignee:
  - '@claude'
created_date: '2026-09-03 11:35'
updated_date: '2026-09-24 09:32'
labels: []
milestone: m-7
dependencies:
  - TASK-36
documentation:
  - docs/SPEC.md
modified_files:
  - skill/SKILL.md
  - skill/references/examples.md
priority: high
type: feature
ordinal: 38000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
La skill va riscritta evitando l'errore da non ripetere (SPEC.md §11): NON deve contenere lo schema del formato né riscrivere il generatore; deve essere sottile e chiamare il CLI. SKILL.md descrive un workflow di quattro passi: interpretare la richiesta in linguaggio naturale scegliendo style, dimensioni, numero di stanze e densità di arredo; invocare ddforge generate con quei parametri; se il comando esce con errore leggere gli Issue e correggere i PARAMETRI, mai modificare il JSON a mano; consegnare il file indicando dove salvarlo e come aprirlo. Con references/styles.md (stili disponibili e quando usarli) e references/examples.md (esempi di invocazione).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 skill/SKILL.md descrive il workflow in quattro passi e non contiene schema del formato né codice di generazione
- [x] #2 skill/references/styles.md elenca gli stili disponibili e quando usarli
- [x] #3 skill/references/examples.md contiene esempi concreti di invocazione del CLI
- [x] #4 La skill istruisce esplicitamente a non modificare mai il JSON a mano e a correggere invece i parametri
- [x] #5 Una richiesta in italiano tipo una cripta di otto stanze con poca luce produce una mappa valida
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. skill/references/styles.md esiste gia' ed e' completo/coerente col CLI attuale (algoritmi, --style, --building-type, --scale, --landmark, --furnish/--lights) — nessuna modifica necessaria, verificato leggendolo insieme a cli.py e SPEC.md.
2. Scrivere skill/SKILL.md: frontmatter (name/description) + workflow a 4 passi da SPEC.md §11 (interpretare la richiesta -> invocare ddforge generate -> in caso di errore leggere gli Issue e correggere SOLO i parametri, mai il JSON -> consegnare il file indicando dove salvarlo/come aprirlo). Rimandare a references/styles.md e references/examples.md, nessuno schema del formato ne codice di generazione qui.
3. Scrivere skill/references/examples.md: invocazioni concrete e valide del CLI (dungeon/cripta, building, cave, sewer, city nei 3 preset), con --template templates/blank_80x80.dungeondraft_map (unico template di produzione, canvas utile 78x78) e output in generated/. Includere l'esempio "cripta di otto stanze con poca luce" (dungeon --style crypt --rooms 8, niente --lights).
4. Verificare AC5 davvero: lanciare 'ddforge generate dungeon --template templates/blank_80x80.dungeondraft_map --out generated/skill_demo_crypt.dungeondraft_map --width 78 --height 78 --rooms 8 --seed <seed> --style crypt' e confermare exit 0 / 0 errori.
5. Rileggere SKILL.md/examples.md/styles.md contro AC1-AC4 (niente schema, niente codice generatore, istruzione esplicita a non toccare il JSON a mano) prima di chiudere.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
AC1-4 verificate rileggendo skill/SKILL.md e skill/references/examples.md: workflow a 4 passi (interpreta -> invoca ddforge generate -> in caso di errore corregge i PARAMETRI leggendo gli Issue, mai il JSON -> consegna indicando percorso in generated/ e come aprire il file in Dungeondraft via File > Open Map), nessuno schema del formato, nessun codice di generazione. skill/references/styles.md esisteva gia' ed e' stato verificato coerente col parser CLI attuale (src/ddforge/cli.py: algoritmi dungeon/building/cave/sewer/city, --style, --building-type, --l-shaped, --scale, --landmark/--no-landmarks, --furnish, --lights) — nessuna modifica necessaria.

AC5 verificata con evidenza oggettiva, non solo lettura del codice: eseguito '.venv/Scripts/ddforge generate dungeon --template templates/blank_80x80.dungeondraft_map --out generated/skill_demo_crypt.dungeondraft_map --width 78 --height 78 --rooms 8 --seed 1337 --style crypt' (interpretazione di 'una cripta di otto stanze con poca luce': --rooms 8, --style crypt, niente --lights). Uscita 'Scritto ...' con exit 0, poi 'ddforge validate' sullo stesso file: 'Nessun problema trovato.' File di verifica rimosso dopo il controllo (generated/ e' gitignored, non e' un artefatto del task).

Revisione della skill dopo la prima stesura (richiesta di Jay: 'controlla la skill appena creata, se trovi modi per migliorarla fallo'). Ogni comando di references/examples.md e' stato ESEGUITO davvero, non solo scritto: dungeon (cripta e variante con --lights/--furnish), building tavern e manor --l-shaped, cave, sewer, city nei tre preset (isolato, quartiere con --landmark porto/faro, citta --no-landmarks), preview, validate. Sei difetti trovati e corretti:

1. MESSAGGIO DI ERRORE INVENTATO: avevo scritto a memoria 'Errore: 'arena' non e ammissibile al preset 'quartiere' (solo: citta)'. Il testo reale e "Errore: L'elemento urbano 'arena' non e' ammissibile al preset di scala 'quartiere': preset ammessi ['citta']". Sostituito con l'output verificato.
2. AFFERMAZIONE FALSA sul template: avevo scritto che blank_80x80 e 'l'unico template di produzione'. Esiste anche templates/blank_160x160.dungeondraft_map, il cui canvas reale e 128x128 (il nome inganna), stessi 52 pack, e genera perfettamente ('dungeon --width 126 --height 126 --rooms 16 --seed 1337': exit 0, zero avvisi). Ora entrambi sono documentati in una tabella con i massimi consigliati (78x78 / 126x126).
3. VINCOLO DI WORKING DIRECTORY non documentato: assets.load_catalog usa il percorso relativo 'data/assets.json', quindi lanciare il CLI da un'altra directory fallisce subito ('Errore: Catalogo asset non trovato: data\\assets.json'). Verificato eseguendo da %TEMP% con percorsi assoluti per --template/--out: fallisce comunque.
4. COME INVOCARE ddforge non documentato: non e nel PATH e 'python -m ddforge' NON funziona (il package non ha __main__.py; unico entry point e [project.scripts] ddforge = ddforge.cli:main). Serve .venv/Scripts/ddforge o l'ambiente attivato. Senza questa nota la skill falliva alla prima invocazione.
5. GUIDA AGLI AVVISI FUORVIANTE: avevo scritto che gli avvisi sono 'difetti minori che l'utente potrebbe voler correggere rigenerando'. Misurato: DDF102 ('gruppo di muri connessi senza porta') e ordinaria amministrazione (18 avvisi su una fognatura normale, 2 su quasi ogni building/dungeon) e inseguirlo porta a rigenerazioni inutili. Ora la skill distingue DDF101 (da correggere) da DDF102 (rumore, da ignorare).
6. TRAPPOLA DEL CANVAS, il difetto piu grave: chiedere --width/--height oltre il canvas del template NON fallisce. 'dungeon --width 100 --height 100' su blank_80x80 esce con codice 0 e scrive il file, con 23 avvisi DDF101 e geometria fuori dal canvas. Il passo 3 della prima stesura reagiva solo al codice di uscita != 0, quindi non avrebbe mai intercettato questo caso. Riscritto: due modi di fallire, uno solo dei quali visibile dall'exit code.

Aggiunto anche 'ddforge preview' come autocontrollo facoltativo prima della consegna (il PNG di un dungeon e leggibile: stanze, porte, arredo), con i suoi limiti verificati guardando i PNG: non disegna paths (le strade di una mappa cittadina non compaiono) ne tetti, e per le grotte esce nero (vedi nota sul bug qui sotto).
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-24 09:25
---
Jay, durante la revisione della skill ho trovato un **bug fuori dallo scope di questo task**, che ho solo documentato nella skill invece di correggerlo.

`ddforge preview` su una grotta produce un PNG completamente nero, senza nessun errore. Non e' la mappa a essere vuota: il renderer *prova* a disegnare il layer cave nativo (`preview._draw_cave_bitmap`, chiamato regolarmente), ma `cave_bitmap.decode_cave_bitmap` solleva `IndexError` su un file prodotto da `ddforge generate cave`, e il `try/except (ValueError, IndexError): return` alla riga 85 di `preview.py` lo inghiotte in silenzio, lasciando l'immagine vuota.

Riproduzione (grotta generata normalmente, 80x80 dal template di produzione):

```
ddforge generate cave --template templates/blank_80x80.dungeondraft_map --out g.dungeondraft_map --width 78 --height 78 --seed 1337
# poi, sul documento scritto:
#   decode_cave_bitmap(level['cave']['bitmap'], 80, 80) -> IndexError: list index out of range
#   (blob lungo 44831 caratteri, world 80x80)
```

Il file `.dungeondraft_map` in se' e' valido (`ddforge validate` -> 'Nessun problema trovato'): e' l'anteprima a mentire, ed e' il caso peggiore perche' un PNG nero sembra una generazione fallita. Nella skill ho scritto esplicitamente che per le grotte il preview non e' affidabile, cosi' nessuno lo interpreta come mappa vuota.

Sospetto un disallineamento fra la forma di griglia usata in scrittura e quella attesa da `cave_grid_shape`/`decode_cave_bitmap` in lettura, ma non ho indagato oltre per non uscire dallo scope.

Vuoi che apra un task di follow-up per sistemarlo (decodifica del bitmap + un test di round-trip generate->decode, visto che oggi l'except silenzioso nasconderebbe qualunque regressione)? Non ho creato niente di mia iniziativa.
---

author: @claude
created: 2026-09-24 09:32
---
Follow-up aperto su richiesta di Jay: **TASK-37.1** — "ddforge preview rende un PNG vuoto per le grotte: la decodifica del layer cave fallisce in silenzio" (bug, Medium, milestone m-6, sottotask di TASK-37 che e' il task del renderer).

Fra le AC c'e' anche la rimozione dell'avviso che ho messo in skill/SKILL.md e skill/references/examples.md sul preview delle grotte inaffidabile: va tolto quando il baco e' chiuso, altrimenti la skill continua a sconsigliare uno strumento che nel frattempo funziona.

Annotato li' anche che si tratta di una **regressione**: le implementation notes di TASK-37 riportano la verifica visiva del preview di generated/cave_m5.dungeondraft_map con esito positivo ('bitmap nativo leggibile, forma organica corretta'), quindi fra l'8 settembre e oggi scrittura e lettura del bitmap si sono disallineate.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Riscritta la skill Claude `dungeondraft-map-generator` seguendo l'errore da non ripetere di SPEC.md §11: e' sottile, chiama il CLI `ddforge` e non contiene ne' lo schema del formato ne' codice di generazione.

**Aggiunto:**
- `skill/SKILL.md` — workflow a 4 passi (interpretare la richiesta in parametri -> invocare `ddforge generate` -> leggere l'esito e correggere i PARAMETRI, mai il JSON a mano -> consegnare il file indicando il percorso e come aprirlo in Dungeondraft via File > Open Map), piu' una sezione di prerequisiti operativi (lavorare dalla root del repo, come invocare l'eseguibile) e la tabella template/canvas. Rimanda a `references/styles.md` e `references/examples.md` senza duplicarli.
- `skill/references/examples.md` — invocazioni concrete per tutti gli algoritmi (`dungeon`, `building`, `cave`, `sewer`, `city` nei tre preset), `preview`, `validate`, piu' una sezione "Leggere l'esito" con i due modi di fallire. Include l'esempio "cripta di otto stanze con poca luce" richiesto da AC5.

**Non toccato:** `skill/references/styles.md` esisteva gia' da lavoro precedente ed e' stato verificato coerente col parser CLI attuale (`src/ddforge/cli.py`) — nessuna modifica necessaria (AC2 soddisfatto com'era).

**Verifica.** Dopo una prima stesura scritta a tavolino, ogni comando della skill e' stato **eseguito davvero** (dungeon, building tavern/manor, cave, sewer, city nei tre preset, preview, validate). La verifica ha smentito sei cose che avevo scritto senza provarle — vedi le implementation notes per il dettaglio; le piu' rilevanti:

- superare il canvas del template **non e' un errore**: `--width 100` su un template 80x80 esce con codice 0 e scrive comunque il file, con geometria fuori dal canvas (23 avvisi DDF101). Il passo 3 della prima stesura, che reagiva al solo exit code, non l'avrebbe mai intercettato: ora la skill distingue esplicitamente i due modi di fallire;
- `blank_80x80` **non** e' l'unico template di produzione (come avevo scritto): esiste anche `blank_160x160`, il cui canvas reale e' 128x128 nonostante il nome, e genera senza un avviso;
- `ddforge` non e' nel PATH e `python -m ddforge` non funziona: senza questa nota la skill falliva alla prima invocazione;
- il CLI va lanciato dalla root del repo (`data/assets.json` e' un percorso relativo);
- gli avvisi DDF102 sono rumore ordinario (18 su una fognatura normale), non difetti da inseguire rigenerando;
- il messaggio di errore che avevo riportato per un `--landmark` non ammissibile era inventato: sostituito con l'output reale.

AC5 verificata end-to-end: `ddforge generate dungeon --width 78 --height 78 --rooms 8 --seed 1337 --style crypt` (niente `--lights`, per "poca luce") scrive il file con exit 0, e `ddforge validate` sul risultato conferma "Nessun problema trovato." File di verifica rimossi (`generated/` e' gitignored).

**Follow-up aperto (fuori scope, vedi commento #1):** `ddforge preview` su una grotta produce un PNG nero perche' `decode_cave_bitmap` solleva `IndexError` e `preview.py` lo inghiotte in un `except ... : return` silenzioso. Il file `.dungeondraft_map` e' valido, e' l'anteprima a mentire. Documentato nella skill come limite noto; in attesa che Jay decida se aprire un task per correggerlo.
<!-- SECTION:FINAL_SUMMARY:END -->
