---
id: TASK-49
title: Prompt Nano Banana per i 17 sprite mancanti dei luoghi urbani
status: Done
assignee:
  - '@claude'
created_date: '2026-09-15 07:15'
updated_date: '2026-09-15 07:53'
labels: []
milestone: m-9
dependencies: []
references:
  - prompt/01-ospedale.md
documentation:
  - docs/sprite-luoghi.md
  - docs/prompt-sprite-pack.md
priority: high
type: feature
ordinal: 50000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
La cartella prompt/ contiene oggi 8 schede pronte da incollare in Gemini Nano Banana (01-ospedale .. 08-banco-mercato), una per sprite, tutte con la stessa struttura: intestazione con nome file, categoria, canvas, regola del rosso e contesto d'uso; prompt canonico completo; due varianti B e C che cambiano la sola riga SUBJECT; sezione 'Dopo la generazione' e checklist finale. Mancano le schede per i restanti luoghi che il generatore sa gia' piazzare sulle mappe cittadine.

Servono le schede per questi 17 soggetti chiesti da Jay: biblioteca, villa nobiliare, cimitero, armeria, tempio, monastero, caserma, banca, alchimista, magazzino, fabbro, stalle, fornaio, macelleria, taverna, locanda, bordello.

Attenzione a tre casi che non sono un edificio singolo come l'ospedale:
- cimitero e' un luogo all'aperto (docs/sprite-luoghi.md sez. 4): non un unico sprite ma piu' pezzi sparsi da 512x512 che il generatore ripete dentro un'area erbosa (lapide x3, croce, fossa recintata). La scheda deve produrre i pezzi, non un edificio.
- villa nobiliare e armeria non esistono come LandmarkKind in src/ddforge/generators/landmarks.py ne' come riga in docs/sprite-luoghi.md: la scheda va scritta lo stesso, ma va annotato che il luogo corrispondente non e' ancora generabile, cosi' chi riprende il lavoro sa che manca il pezzo a monte.
- gli altri 14 sono gia' LandmarkKind esistenti: canvas, scala e regola del rosso vanno presi dalla categoria giusta di sprite-batch.zip/catalogo.yaml (C1 1024 monumenti, C2 768 pubblici medi, C3 512 botteghe) e dalle misure gia' rilevate in docs/sprite-luoghi.md.

Le schede servono a Jay per generare gli sprite a mano, una conversazione per scheda: devono essere autosufficienti, senza rimandi a contesto che chi incolla non ha.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 prompt/ contiene una scheda per ciascuno dei 17 soggetti, numerata in continuita' con le 8 esistenti (09-.. in avanti) e con lo stesso nome-file in kebab-case
- [x] #2 Ogni scheda ha la stessa struttura di prompt/01-ospedale.md: tabella di intestazione (nome file nm_*.png, categoria, canvas, scala, regola del rosso, dove finisce sulla mappa), sezione 'Come usarlo', prompt canonico completo e autosufficiente, varianti B e C con la sola riga SUBJECT sostituita, sezione 'Dopo la generazione', checklist finale
- [x] #3 Canvas e regola del rosso di ogni scheda corrispondono alla categoria dello sprite (C1 1024, C2 768, C3 512) e non si contraddicono con docs/sprite-luoghi.md
- [x] #4 La scheda del cimitero produce i pezzi sparsi previsti da docs/sprite-luoghi.md sez. 4 (lapide x3, croce, fossa recintata) a 512x512, non un edificio unico
- [x] #5 Le schede di villa nobiliare e armeria dichiarano esplicitamente che il LandmarkKind corrispondente non esiste ancora in generators/landmarks.py
- [x] #6 Il file 'prompt/altri asset di cui chiedere il prompt.txt' non elenca piu' soggetti gia' coperti da una scheda
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Numerare le 17 nuove schede 09..25 in prompt/, kebab-case, nello stesso ordine chiesto da Jay: 09-biblioteca, 10-villa-nobiliare, 11-cimitero, 12-armeria, 13-tempio, 14-monastero, 15-caserma, 16-banca, 17-alchimista, 18-magazzino, 19-fabbro, 20-stalle, 21-fornaio, 22-macelleria, 23-taverna, 24-locanda, 25-bordello.
2. Ogni scheda replica la struttura di 01-ospedale.md/02-teatro.md/03-accademia.md: tabella header (nome file nm_*.png, categoria, canvas, scala, rosso, dove finisce), paragrafo su 'disegnato a' e segno distintivo, sezione Come usarlo, prompt canonico (REFERENCE/VIEW/ISOLATION/STYLE/LIGHT/PALETTE/ROOFS/CONSISTENCY/SUBJECT), varianti B e C (sola riga SUBJECT), Dopo la generazione, Checklist.
3. Per i 14 soggetti gia' LandmarkKind (biblioteca, tempio, monastero, caserma, banca, alchimista, magazzino, fabbro, stalle, taverna, locanda, bordello, fornaio, macelleria): categoria/canvas/regola del rosso da sprite-batch.zip/catalogo.yaml (C1 1024 monastero; C2 768 tempio/caserma; C3 512 gli altri); 'disegnato a' e frequenza da docs/sprite-luoghi.md sez.3 dove misurati. Per fornaio e macelleria (isolato-only, fuori dalla tabella misurata) dichiarare esplicitamente l'assenza di misura quartiere/citta e trattarli come bottega C3 512 alla pari dei coetanei (building_type warehouse).
4. cimitero e' un luogo all'aperto (sez.4): una sola scheda in stile 08-banco-mercato.md che copre 5 file a scala reale (256px=1,5m): nm_cimitero_lapide_1/2/3.png, nm_cimitero_croce.png, nm_cimitero_fossa.png, lato pezzo ~1,5 q = 2,2 m, nessun terreno nell'immagine (lo stende il generatore).
5. villa nobiliare e armeria: scheda scritta lo stesso con box di avviso esplicito 'LandmarkKind non esiste ancora in generators/landmarks.py', canvas/categoria proposti come bozza non misurata (villa nobiliare come C1/monumento residenziale, armeria come C3/bottega specializzata).
6. Aggiornare 'prompt/altri asset di cui chiedere il prompt.txt' rimuovendo i 4 soggetti ora coperti da scheda.
7. Verifica finale: contare i file, controllare canvas/rosso non contraddicono docs/sprite-luoghi.md, controllare che cimitero produca pezzi non un edificio, controllare i due avvisi villa/armeria.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Create 17 nuove schede prompt/09..25, stessa struttura di 01-ospedale.md. Canvas/rosso presi da sprite-batch.zip/catalogo.yaml (monastero C1 1024 rosso libero; tempio/caserma C2 768 rosso tetto; gli altri 11 C3 512 rosso tetto). Misure disegnato-a e frequenza per mappa da docs/sprite-luoghi.md sez.3 dove disponibili; per fornaio/macelleria (isolato-only, fuori tabella) aggiunta nota esplicita di assenza misura quartiere/citta. cimitero trattato come scheda multi-pezzo a scala reale (5 file: lapide_1/2/3, croce, fossa) invece di un edificio, seguendo sez.4. villa-nobiliare e armeria scritte con box di avviso esplicito: LandmarkKind non esiste in generators/landmarks.py (verificato via grep, nessun risultato), canvas/categoria segnati come proposta non misurata. Svuotato prompt/'altri asset di cui chiedere il prompt.txt' (i 4 soggetti elencati sono ora coperti).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Create 17 nuove schede in prompt/ (09-biblioteca .. 25-bordello), stessa struttura delle 8 esistenti (header, Come usarlo, prompt canonico REFERENCE/VIEW/ISOLATION/STYLE/LIGHT/PALETTE/ROOFS/CONSISTENCY/SUBJECT, varianti B/C, Dopo la generazione, Checklist). Canvas e regola del rosso presi da sprite-batch.zip/catalogo.yaml per categoria (monastero C1/1024/libero; tempio+caserma C2/768/tetto; le 11 botteghe C3/512/tetto); misure 'disegnato a' e frequenza da docs/sprite-luoghi.md sez.3 dove disponibili. cimitero e' una scheda multi-pezzo a scala reale (5 file: lapide_1/2/3, croce, fossa) invece di un edificio, coerente con sez.4. villa-nobiliare e armeria portano un box di avviso esplicito (verificato: grep -i su generators/landmarks.py non trova ne' 'villa' ne' 'armeria' come LandmarkKind) e canvas/categoria segnati come proposta non misurata. fornaio/macelleria (isolato-only, fuori dalla tabella misurata) dichiarano esplicitamente l'assenza di misura quartiere/citta. Il file 'altri asset di cui chiedere il prompt.txt' e' stato svuotato. Verificato con script: tutti i 17 file hanno le 7 sezioni strutturali attese e la riga 'Mai WebP'; canvas/categoria di ogni file corrispondono alla categoria dichiarata; le due schede senza LandmarkKind portano l'avviso; cimitero elenca tutti e 5 i nomi file richiesti.
<!-- SECTION:FINAL_SUMMARY:END -->
