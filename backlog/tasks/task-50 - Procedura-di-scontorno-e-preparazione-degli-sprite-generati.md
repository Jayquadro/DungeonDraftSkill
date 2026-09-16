---
id: TASK-50
title: Procedura di scontorno e preparazione degli sprite generati
status: Done
assignee:
  - '@claude'
created_date: '2026-09-15 07:16'
updated_date: '2026-09-16 06:15'
labels: []
milestone: m-9
dependencies: []
references:
  - sprite-batch.zip
documentation:
  - docs/sprite-luoghi.md
priority: high
type: feature
ordinal: 51000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Gli sprite generati da Jay arrivano oggi in assets/ come JPEG con il fondo magenta piatto (#FF00FF) chiesto dal prompt: ospedale.jpg, teatro.jpg, accademia.jpg, prigione.jpg, municipio.jpg, faro.jpg, bagni_termali.jpg. In quella forma non sono usabili: niente canale alfa, frangia magenta sul bordo, nessuna ombra coerente, tetti di rosso disomogeneo, canvas e centratura casuali.

Serve una procedura ripetibile che porti un'immagine grezza appena generata fino al PNG pronto per il pack, con gli stessi numeri per tutto il pacchetto: scontorno del magenta e pulizia della frangia colorata sull'alfa, rifilo e ricentratura del soggetto, margine trasparente del 5% per lato, canvas portato alla misura della categoria (C1 1024, C2 768, C3 512), normalizzazione dei tetti al rosso saturo uniforme per la ricolorabilita' di Dungeondraft, ombra aggiunta in post con offset 4%, sfocatura 2,5%, opacita' 45%, colore (22,16,10), salvataggio in PNG con alfa. Sono i numeri gia' scritti nelle sezioni 'Dopo la generazione' delle schede in prompt/ e in sprite-batch.zip/catalogo.yaml: la procedura deve rispettarli, non inventarne di nuovi.

Materiale di partenza: sprite-batch.zip alla radice del repo contiene un pacchetto Python 'spritebatch' che fa gia' questo lavoro (modulo postprocess.py, catalogo.yaml con scala/ombra/rosso, comando 'spritebatch elabora'). Oggi e' solo uno zip: non e' estratto nel repo, non e' installato, non gira nella suite. Prima decisione da prendere nel piano: recuperarlo dentro il repo oppure scrivere uno strumento nuovo piu' piccolo che faccia la sola post-elaborazione (la generazione via API non serve, le immagini le produce Jay a mano).

Il risultato deve essere usabile da Jay senza rileggere il codice: un comando, una cartella di input, una cartella di output, un rapporto che dica quali sprite sono passati e quali vanno rifatti.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Esiste una procedura documentata (comando + doc in docs/) che porta un'immagine grezza con fondo magenta al PNG finale pronto per il pack, in un solo passaggio per cartella
- [x] #2 Lo scontorno rimuove il fondo magenta e la frangia colorata sul bordo alfa: sul bordo del soggetto non restano pixel magenta residui
- [x] #3 Ogni PNG in uscita ha canale alfa reale, soggetto centrato, margine trasparente del 5% per lato e canvas alla misura della categoria (1024 C1 / 768 C2 / 512 C3)
- [x] #4 I tetti sono normalizzati a rosso saturo uniforme e nessun altro pixel dell'immagine ricade nelle soglie che Dungeondraft userebbe per ricolorare
- [x] #5 L'ombra e' aggiunta dalla procedura con gli stessi parametri per tutti gli sprite (offset 4%, sfocatura 2,5%, opacita' 45%, colore 22/16/10) e non dal modello che ha generato l'immagine
- [x] #6 La procedura produce un rapporto che elenca per ogni sprite l'esito dei controlli (alfa, margine, proporzioni, pixel ricolorabili, soggetto che tocca il bordo) e segnala quelli da rigenerare
- [x] #7 I 7 JPEG gia' presenti in assets/ sono passati nella procedura e i PNG risultanti sono versionati nel repo
- [x] #8 L'uscita e' PNG, mai WebP: assets.read_dungeondraft_pack legge le dimensioni dall'header IHDR
- [x] #9 Ci sono test automatici sui passi deterministici della procedura e la suite passa
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Decisione: NON estrarre sprite-batch.zip cosi' com'e' (backend openai/comfyui/rembg/pack.py non servono, aggiungono dipendenze pesanti - rembg scarica ~1GB e non e' deterministico). Portiamo dentro il repo solo i passi di post-processing puri (crop/scala/centratura/ombra/rosso/validazione), riscritti in src/ddforge/sprite_prep/ con gli stessi numeri di sprite-batch.zip/catalogo.yaml (margine 0.05, ombra offset 0.04/blur 0.025/opacita 0.45/colore 22,16,10, soglie rosso), verificati per confronto diretto con i default di spritebatch/catalog.py. Lo scontorno diventa uno chroma-key deterministico sul magenta puro (#FF00FF) con despill sulla frangia, al posto di rembg: e' l'algoritmo giusto per uno sfondo sintetico piatto (non una foto) ed e' testabile senza rete/modelli.
2. Moduli nuovi: settings.py (ScaleSettings/ShadowSettings/RedSettings), imaging.py (chroma-key+despill, conversioni hsv, normalizzazione/soppressione rosso, geometria canvas/ombra, validazione), manifest.py (tabella nome-file-grezzo -> categoria/canvas/scala/rosso, presa da prompt/*.md e sprite-batch.zip/catalogo.yaml), pipeline.py (elabora un file, produce PNG + esito), cli.py (comando singolo: cartella input -> cartella output + rapporto.json).
3. scripts/prepare_sprites.py come entry point sottile (stesso pattern degli altri script in scripts/).
4. Manifest per i 27 JPEG oggi in assets/ (esclude template.png su richiesta esplicita, ed esclude di norma qualunque file non registrato nel manifest, riportandolo come 'ignorato'): 7 luoghi chiusi originari + 17 nuovi da TASK-49 + il market-stall generato come Gemini_Generated_Image_*.jpg (mappato su nm_banco_mercato_1, C4) + i 3 pezzi del cimitero (croce/fossa/lapide, C4 scala reale).
5. Esegue la procedura su tutti i 27 file, versiona i PNG in assets/sprites/, versiona il rapporto in assets/sprites/rapporto.json.
6. Documentazione in docs/sprite-postprocessing.md: comando, un passaggio per cartella, numeri usati, formato del rapporto, come aggiungere una voce al manifest.
7. Test in tests/test_sprite_prep.py sui passi deterministici (chroma-key+despill su fixture sintetica, geometria canvas/ombra, normalizzazione/soppressione rosso, validazione, manifest coerente con le categorie C1/C2/C3), pytest completo verde.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementata in src/ddforge/sprite_prep/ (settings.py, imaging.py, manifest.py, pipeline.py, batch.py, cli.py) + entry point scripts/prepare_sprites.py + doc docs/sprite-postprocessing.md + test tests/test_sprite_prep.py (25 test).

Decisione presa (AC libero nel brief): NON estratto sprite-batch.zip cosi' com'e'. Portati nel repo solo i passi puri di post-processing (geometria canvas/ombra, normalizzazione/soppressione rosso), stessa matematica di spritebatch/postprocess.py, stessi numeri di default di spritebatch/catalog.py (margine 0.05, ombra 0.04/0.025/0.45/22,16,10, soglie rosso 0.1/0.0/0.04, tetto 25deg/0.35/0.15/0.85, vietato 26deg/1.5). Lo scontorno rimpiazza rembg con uno chroma-key deterministico sul magenta: prima versione su distanza RGB dal magenta puro falliva sui JPEG reali (vignettatura agli angoli, es. corner (204,0,198) vs (251,0,240)) producendo falsi "soggetto tocca il bordo" su 8/27 sprite; riscritto su tinta+saturazione (magentaness = vicinanza a 300 gradi * saturazione), robusto alla vignettatura perche' tinta e saturazione non cambiano con la sola luminosita'. Verificato rieseguendo il batch: 8 avvisi spuri spariti.

Verifica oggettiva:
- pytest -q sull'intera suite: 774 passed, 1 skipped (preesistente, non collegato), 0 failed.
- python scripts/prepare_sprites.py --input assets --output assets/sprites sui 27 JPEG oggi in assets/ (7 originari + 17 da TASK-49 + market-stall Gemini_Generated_Image_*.jpg + 3 pezzi cimitero): 26 ok, 1 avviso legittimo (nm_cimitero_lapide_1: proporzioni 2.37:1 vs 1.50:1 attese, segnalato per Jay), 0 errori, 0 mancanti. template.png esplicitamente escluso (in "ignorati" del rapporto, nessuna voce nel manifest) come richiesto.
- Ispezione visiva di un campione di PNG risultanti (ospedale, alchimista, faro, prigione, banco_mercato, cimitero_lapide_1): sfondo trasparente pulito, ombra in basso a destra, tetti rosso saturo uniforme dove "tetto", nessun rosso residuo dove "vietato".
- assets/sprites/nm_ospedale.png verificato con Pillow: mode RGBA, size 768x768, firma PNG valida (89 50 4E 47 0D 0A 1A 0A).

Manifest (src/ddforge/sprite_prep/manifest.py) copre tutti i 27 file oggi in assets/: ogni file senza voce (compreso template.png) e' riportato come "ignorato", non elaborato silenziosamente. Due categorie non misurate (villa_nobiliare, armeria) usano la proposta scritta in prompt/10 e prompt/12, segnalato nella doc.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Aggiunta una procedura di post-processing deterministica (src/ddforge/sprite_prep/ + scripts/prepare_sprites.py) che porta i JPEG grezzi con fondo magenta a PNG pronti per il pack: scontorno del magenta via chroma-key tinta/saturazione (non rembg, per determinismo e robustezza alla vignettatura reale), ritaglio/centratura/canvas per categoria, normalizzazione o soppressione del rosso, ombra in post con i numeri di sprite-batch.zip/catalogo.yaml, validazione e rapporto.json. Eseguita sui 27 JPEG oggi in assets/ (esclude template.png su richiesta): 26 ok, 1 avviso legittimo, PNG versionati in assets/sprites/. Documentata in docs/sprite-postprocessing.md. Verificato con: suite pytest completa verde (774 passed), batch reale su assets/, ispezione visiva di un campione di output, controllo del PNG risultante con Pillow.
<!-- SECTION:FINAL_SUMMARY:END -->
