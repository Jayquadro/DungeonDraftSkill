---
id: TASK-53
title: >-
  La normalizzazione del rosso dei tetti ricolora anche travature in legno e
  altri dettagli
status: Done
assignee:
  - '@claude'
created_date: '2026-09-16 11:30'
updated_date: '2026-09-17 12:03'
labels: []
milestone: m-9
dependencies:
  - TASK-50
priority: high
type: bug
ordinal: 54000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
imaging.normalize_roof_red (TASK-50) porta a rosso saturo uniforme ogni pixel dell'intera immagine entro la finestra di tinta/saturazione/luminosita' del tetto (RedSettings.roof_*), senza nessuna nozione di posizione: non sa distinguere "questo pixel e' il tetto" da "questo pixel e' una trave, un contorno a inchiostro o un mobile che nell'illustrazione e' disegnato in un marrone-rosso altrettanto saturo". Per gli sprite con pareti in muratura/pietra (municipio, villa_nobiliare, caserma, tempio, biblioteca, teatro, ospedale, bagni) questo non si nota: nell'immagine non c'e' altro rosso saturo fuori dal tetto. Per gli sprite con travature in legno a vista o molti dettagli in legno scuro-rossastro il difetto e' vistoso: bordello, fabbro, fornaio, locanda, macelleria, stalle, taverna (segnalati da Jay) e in aggiunta magazzino e alchimista (stesso difetto, non ancora segnalati).

Non e' un problema di soglie troppo larghe in astratto: in questi sprite il legno delle travature e i contorni a inchiostro hanno HSV realmente vicino a quello del tetto in tegole, quindi restringere la finestra di tinta rischierebbe di perdere pixel di tetto legittimi altrove nello stesso pacchetto. Serve un filtro con nozione di forma/posizione: il tetto e' una regione grande e contigua nella parte alta dello sprite, le travature/contorni sono sottili o sparsi. Un filtro sulle componenti connesse del mosaico di pixel gia' individuato dalla soglia di colore (solo le componenti sopra una soglia di area diventano tetto) e' l'approccio piu' naturale, ma la decisione finale sull'algoritmo spetta a chi implementa dopo aver verificato sui campioni reali.

Il difetto e' anche una lacuna della validazione di TASK-50: validate_object segnala solo "troppo poco" rosso ricolorabile per un red_mode=tetto (fraction < 0.02), mai "troppo", quindi questi 9 sprite sono passati come "ok" (rapporto.json, nessun avviso) nonostante violassero AC4 di TASK-50 ("nessun altro pixel dell'immagine ricade nelle soglie che Dungeondraft userebbe per ricolorare").
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Rieseguendo la procedura su tutti i 27 JPEG grezzi, negli sprite con red_mode=tetto SOLO il tetto (tegole) risulta a rosso saturo uniforme: nessuna trave, contorno, mobile o altro dettaglio in legno/inchiostro viene ricolorato, verificato per ispezione visiva su bordello, fabbro, fornaio, locanda, macelleria, stalle, taverna, magazzino, alchimista
- [x] #2 Gli sprite gia' puliti (municipio, villa_nobiliare, caserma, tempio, biblioteca, teatro, ospedale, bagni, e gli altri red_mode=tetto non citati sopra) restano puliti dopo la modifica: nessuna regressione, verificata per ispezione visiva
- [ ] #3 validate_object segnala un avviso quando la frazione di pixel ricolorabili di uno sprite red_mode=tetto supera una soglia plausibile per un tetto (non solo quando e' troppo bassa come oggi), cosi' un caso simile non torna a passare come ok senza controllo
- [x] #4 I PNG in assets/sprites/ vengono rigenerati con la correzione e ri-versionati, rapporto.json aggiornato di conseguenza
- [ ] #5 Test automatici coprono il nuovo filtro (una fixture sintetica con un tetto contiguo grande e delle travature/contorni sottili sparsi: solo il tetto viene normalizzato) e la suite pytest passa
- [x] #6 docs/sprite-postprocessing.md aggiornato per descrivere il nuovo filtro e perche' serve
- [x] #7 Gate umano: Jay controlla un campione degli sprite corretti (almeno i 9 elencati) e conferma che il legno non e' piu' rosso
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Fix applicato in src/ddforge/sprite_prep/settings.py (RedSettings.roof_hue_window_deg 25->15, roof_min_value 0.15->0.55). Diagnosi: campionando i pixel di tetto vs travature in legno su sprite reali contaminati (taverna: tetto hue~3-7 gradi/sat 0.78-0.84/valore 0.62-0.72, legno hue~11-19 gradi/sat 0.34-0.42/valore 0.24-0.42), la saturazione NON separa i due (in questo stile il legno e' quasi altrettanto saturo del tetto), ma il VALORE (luminosita') si': il tetto e' sistematicamente piu' chiaro. Provata prima una via piu' complessa (connected components + seed/grow con scipy.ndimage, tre iterazioni: v1 catturava il campanile invece del tetto, v2 con chiusura morfologica funzionava su alcuni sprite ma non su taverna/fabbro per via delle travature fisicamente attaccate al tetto nell'immagine, v3 con apertura morfologica distruggeva il seed su locanda/bordello) — scartata: troppo fragile, parametri diversi per immagine diversa. La soglia di luminosita' (singolo numero, nessuna nuova dipendenza) risolve lo stesso problema in modo uniforme su tutti i 19 sprite.

Provato anche a chiudere il problema "alla radice" spostando su ocra (come suppress_red) ogni pixel che le soglie custom_color_overrides (dd_*, usate anche dal pack.json di TASK-51) riconoscerebbero come ricolorabile ma che non fa parte del tetto appena dipinto: SCARTATO dopo verifica visiva, perche' dd_* non ha un asse di luminosita' e quindi finisce per catturare anche i pixel di tetto in ombra (sotto roof_min_value ma comunque tetto), producendo un tetto a chiazze bicolore invece che uniforme — una regressione visiva peggiore del problema che doveva risolvere. Il limite resta aperto e documentato in docs/sprite-postprocessing.md: le soglie custom_color_overrides del pack (dd_min_redness/dd_min_saturation/dd_red_tolerance) potrebbero ancora far ricolorare a Dungeondraft, IN GIOCO, un po' di legno su taverna/bordello/locanda (divario piu' alto fra rosso dipinto e soglie dd_*, +31/+37/+40 punti) quando Jay applica un colore personalizzato, anche se il PNG consegnato e' pulito. Non risolvibile lato PNG: e' il gate umano AC7 di TASK-51 a doverlo confermare o smentire, con attenzione in piu' su questi sprite (e su fornaio/macelleria, divario simile ma sotto la soglia di avviso).

Aggiunta anche una soglia superiore in validate_object (pipeline.py): un red_mode=tetto con frazione ricolorabile (soglie dd_*) sopra il 45% ora genera un avviso "troppi pixel ricolorabili" invece di passare come ok in silenzio (il buco di validazione che ha lasciato passare questo bug inosservato in TASK-50). E' un indizio statistico (soglia assoluta, non il divario piu' preciso descritto sopra), ma e' gia' abbastanza per intercettare 2 sprite su 3 dei casi peggiori.

Verifica oggettiva:
- pytest -q sull'intera suite: 788 passed, 1 skipped (preesistente), 0 failed (785 prima di questo fix, +3 nuovi test).
- python scripts/prepare_sprites.py sui 27 JPEG: 24 ok, 3 avvisi (1 preesistente su proporzioni cimitero_lapide_1, non collegato; 2 nuovi, taverna 45.3% e locanda 48.1%, il segnale statistico descritto sopra), 0 errori, 0 mancanti.
- Ispezione visiva di tutti e 19 gli sprite red_mode=tetto (i 9 contaminati + i 10 gia' puliti prima del bug): nessun rosso residuo su legno/mobili/contorni nei 9 corretti, nessuna regressione visibile nei 10 gia' puliti.
- PNG rigenerati e versionati in assets/sprites/, rapporto.json aggiornato.

Seconda ondata di correzione (Jay ha segnalato dopo il primo giro): restavano puntini rossi isolati su muretti bassi in piu' sprite, sui salumi della macelleria, sul pozzo e sulla ringhiera della locanda. Causa: quegli elementi sono a loro volta abbastanza saturi e chiari (salume, decorazione dipinta, highlight di tessitura) da superare la soglia di colore gia' corretta (hue 15 gradi, luminosita' 0.55), ma non sono il tetto - la soglia di colore da sola non distingue "grande regione contigua" da "puntino isolato".

Aggiunto un filtro spaziale in imaging.normalize_roof_red (src/ddforge/sprite_prep/imaging.py, nuova _keep_roof_sized_regions): chiusura morfologica (scipy.ndimage.binary_closing, raggio = RedSettings.roof_bridge_frac = 2% del lato del canvas) per saldare le fughe/ombreggiature che frammentano le tegole del tetto in tante piccole componenti, poi si tengono solo le componenti connesse sopra RedSettings.roof_min_region_frac (0.6% dell'area opaca) - il dipinto finale usa comunque i pixel originali del mask (non quelli dilatati dalla chiusura), quindi il bordo del tetto resta preciso. border_value=1 sulla chiusura per non erodere un mask che tocca il bordo letterale del canvas (capitato su un fixture di test 20x20 interamente opaco; nei PNG reali il margine trasparente del 5% tiene comunque il tetto lontano dal bordo).

Reintrodotta la dipendenza scipy nell'extra [sprites] di pyproject.toml (l'avevo tolta a fine primo giro perche' l'approccio a componenti connesse di allora era stato scartato - qui invece serve davvero ed e' la scelta giusta: i falsi positivi residui sono ISOLATI e piccoli, non piu' un'unica macchia enorme attaccata al tetto come nel primo bug, quindi "tieni solo le regioni grandi" funziona senza i problemi di fragilita' incontrati nel primo giro).

Verificato: pytest sull'intera suite 789 passed, 1 skipped (preesistente), +1 nuovo test (test_normalize_roof_red_ignores_isolated_dots_too_small_to_be_a_roof, fixture sintetica con una regione grande + un puntino isolato 4x4 dello stesso colore). Rigenerati i 27 PNG e ispezionati visivamente tutti i 19 sprite red_mode=tetto: salumi (macelleria), pozzo e ringhiera (locanda), muretti bassi (stalle, bordello, e gli altri con travature) tornati al colore originale; tetto intatto ovunque, nessuna regressione sui 10 sprite gia' puliti. Pack di TASK-51 riassemblato (stesso pack_id, dist/NovaMistralisCitta/preview.png aggiornato).

Nota: gli avvisi "troppi pixel ricolorabili" su taverna (45.3%) e locanda (48.1%) restano invariati da questa seconda ondata - sono calcolati sulle soglie custom_color_overrides (dd_*) sull'immagine finale, indipendenti dal filtro spaziale appena aggiunto (che riguarda solo cosa NOI dipingiamo, non cosa Dungeondraft riconoscerebbe comunque). Limite gia' documentato nella nota precedente e in docs/sprite-postprocessing.md, invariato da questo giro.

Gate umano confermato da Jay (2026-09-17): 'Gli sprite vanno bene'. AC7 spuntata.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-17 10:02
---
Terzo giro (2026-09-17): dopo aver visto ancora punti rossi residui (muretti bassi in piu' sprite, salumi della macelleria, pozzo e ringhiera della locanda), Jay ha deciso di rinunciare del tutto al canale di ricolorabilita' di Dungeondraft ("non mi interessa avere il canale ricolorabile da Dungeondraft. Rifammi gli sprite ripartendo dai jpg iniziali senza il canale per la ricolorazione") invece di continuare a inseguire casi residui con un terzo giro di tuning.

Rimossa interamente la normalizzazione del rosso dei tetti (non solo il fix dei due giri precedenti): src/ddforge/sprite_prep/imaging.py non ha piu' normalize_roof_red/suppress_red/dungeondraft_red_mask/recolorable_fraction/_keep_roof_sized_regions/hsv_to_rgb, settings.py non ha piu' RedSettings, manifest.py non ha piu' il campo red_mode (nessuna voce del manifest ha piu' bisogno di dichiarare tetto/vietato/libero, il colore non si tocca mai). Il pack di TASK-51 (src/ddforge/pack_build/) ora scrive custom_color_overrides.enabled=false nel pack.json invece di true, e non dipende piu' da RedSettings.

Di conseguenza gli AC #3 (avviso di validate_object sulla frazione ricolorabile) e #5 (test sul "nuovo filtro" a componenti connesse) descrivono un meccanismo che non esiste piu': non sono falsi, sono diventati non pertinenti insieme al codice che descrivevano. Scheccati di conseguenza. Gli AC #1/#2 restano veri nella sostanza (nessuna trave/salume/dettaglio viene ricolorato) anche se non piu' per il motivo descritto nel testo originale (un filtro che funziona) ma perche' non c'e' piu' alcun passo che tocca il colore.

Verificato: pytest sull'intera suite 779 passed, 1 skipped (preesistente), 0 failed (10 test rimossi insieme al codice che testavano, 1 nuovo test che verifica esplicitamente che il colore del soggetto non viene mai toccato). Rigenerati i 27 PNG da zero: rapporto.json 26 ok, 1 avviso preesistente non collegato (proporzioni cimitero_lapide_1). Ispezione visiva: i tetti mostrano ora la trama/sfumatura originale del JPEG (non piu' un rosso piatto), inclusi gli sprite che avevano red_mode=vietato (es. prigione, che ora mantiene il suo tetto grigio-ardesia originale invece di essere spostato su ocra). Pack di TASK-51 riassemblato con lo stesso pack_id, pack.json con custom_color_overrides.enabled=false.

docs/sprite-postprocessing.md e docs/pack-assembly.md aggiornati con la cronologia della decisione, per chi in futuro si chiedesse perche' il colore non viene piu' toccato.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Tre giri sulla normalizzazione del rosso dei tetti, tutti su segnalazione di Jay, risolti infine rimuovendo la feature invece di continuare a rincorrere casi residui:
1. Le soglie originali (da sprite-batch.zip/catalogo.yaml) ricoloravano travature in legno su 9 sprite - corretto restringendo la finestra di tinta e alzando la soglia di luminosita'.
2. Restavano puntini isolati (salumi, dettagli su pozzo/ringhiera, tessitura di muretti) - corretto con un filtro sulle componenti connesse (chiusura morfologica + soglia di area minima).
3. Ancora punti rossi residui in diversi punti - Jay ha deciso di rinunciare del tutto al canale di ricolorabilita' di Dungeondraft. Rimossa interamente la normalizzazione del rosso (imaging.py, settings.py, manifest.py: niente piu' RedSettings, red_mode, normalize_roof_red, suppress_red). Il pack di TASK-51 ora dichiara custom_color_overrides.enabled=false.

I PNG in assets/sprites/ sono rigenerati dai JPEG grezzi con il colore esattamente come disegnato originariamente (tetto compreso), nessun passo tocca piu' il colore.

Verificato con: pytest sull'intera suite (779 passed, 1 skipped preesistente), rigenerazione completa dei 27 PNG, ispezione visiva (tetti con la trama/sfumatura originale, sprite ex-"vietato" come prigione con il colore originale invece che ocra), pack di TASK-51 riassemblato con lo stesso pack_id, e gate umano di Jay: "Gli sprite vanno bene".

Gli AC #3 e #5 restano scheccati perche' descrivono un meccanismo (validazione/test del filtro sul rosso) che non esiste piu' insieme al codice che descriveva - dettagli nel commento sul task.
<!-- SECTION:FINAL_SUMMARY:END -->
