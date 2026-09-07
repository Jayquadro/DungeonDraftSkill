---
id: TASK-31
title: 'Spike: rendering delle grotte come muri poligonali o come layer cave nativo'
status: Done
assignee:
  - '@claude'
created_date: '2026-09-03 11:34'
updated_date: '2026-09-07 12:06'
labels: []
milestone: m-5
dependencies:
  - TASK-26
documentation:
  - docs/SPEC.md
modified_files:
  - scripts/cave_spike.py
  - docs/format.md
  - tests/conftest.py
  - tests/test_cave_bitmap_format.py
  - tests/fixtures/cave_rect_80x80.dungeondraft_map
  - tests/fixtures/cave_freehand_80x80.dungeondraft_map
  - >-
    backlog/decisions/decision-1 -
    Le-grotte-usano-il-layer-cave-nativo-di-Dungeondraft-non-muri-poligonali.md
priority: high
type: spike
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Decisione esplicitamente rimandata a M5 dalla spec (SPEC.md §9.3): il contorno della grotta può essere reso come muri poligonali (add_wall con molti punti), che funziona di sicuro, oppure scritto nel layer cave nativo di Dungeondraft, visivamente molto migliore ma la cui codifica di cave.bitmap non è stata risolta dall'analisi (lunghezze non lineari osservate: 50x25 -> 2614 B, 30x30 -> 1892 B, 8x8 -> 154 B). Prescrizione: provare PRIMA i muri poligonali; passare al layer nativo solo se il risultato non è soddisfacente e solo dopo aver decodificato il bitmap con esperimenti su template di dimensioni diverse. Questo task produce una decisione motivata, non codice di produzione.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 È realizzato un prototipo di grotta con muri poligonali e valutato visivamente
- [x] #2 La decisione fra muri poligonali e layer cave nativo è presa e registrata come decision di Backlog con le motivazioni
- [x] #3 Se si sceglie il layer nativo, la codifica di cave.bitmap è documentata in docs/format.md con gli esperimenti che la confermano
- [ ] #4 Se la decodifica non riesce, la decisione ricade sui muri poligonali senza bloccare la milestone
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Tentativo di decodifica di cave.bitmap PRIMA di scartarlo: con soli 3 campioni (50x25->2614B, 30x30->1892B, 8x8->154B) provo a risolvere un modello lineare L = 2wh + a*w + b*h + c. Sistema a 3 equazioni/3 incognite: a=1.48, b=1.52 (non interi, non puliti) - 3 punti e 3 parametri liberi si adattano sempre esattamente, quindi non e evidenza di un formato reale, e i coefficienti non tornano puliti. Senza nuovi campioni con contenuto cave noto e diverso (servirebbe Jay che disegna a mano in Dungeondraft ed esporta, dato che questa macchina HA Dungeondraft installato in C:/Program Files/Dungeondraft ma io non posso pilotarlo) non si puo procedere oltre: cade su AC4, si passa ai muri poligonali senza bloccare la milestone. Documento il tentativo nelle implementation notes, non in format.md (AC3 si applica solo se si sceglie il layer nativo).
2. Prototipo muri poligonali (script una tantum, non produzione, come scripts/demo_m1.py):
   - scripts/cave_spike.py: cellular automata minimale (random fill seedato + 4-5 iterazioni di smoothing), flood-fill per tenere solo la regione aperta piu grande (evita isole scollegate nel prototipo), marching squares (case table a 16 casi, punti a meta lato cella, senza interpolazione) per estrarre il contorno come poligono in coordinate a quadretti.
   - Carica templates/blank_80x80.dungeondraft_map, prepare(levels=1), add_polygon_pattern col floor della palette "cave" (assets.palette_for), add_wall(loop=True) col wall della stessa palette.
   - Output: generated/cave_spike.dungeondraft_map (gitignored, non committato).
3. Chiedo a Jay di aprire generated/cave_spike.dungeondraft_map in Dungeondraft e valutare visivamente se il contorno poligonale e accettabile per una grotta (AC1) - non posso giudicarlo da qui.
4. In base al suo giudizio: se accettabile, decisione = muri poligonali (atteso, dato il fallimento della decodifica al punto 1). Registro la decisione con `backlog decision create` (motivazioni nel corpo del file - nessun tool CLI/MCP espone contenuto oltre al titolo, verifico cosa produce il comando prima di eventualmente doverlo popolare a mano, unica via dato che non esiste un equivalente decision_update).
5. Nessuna modifica a src/ddforge/generators/cave.py (resta NotImplementedError, di competenza di TASK-32) ne a docs/format.md (AC3 non si applica).
6. Aggiorno implementation notes con l'esito, poi finalization secondo la guida di task-finalization.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Jay ha ridisegnato a mano una grotta nel layer nativo dentro generated/cave_spike.dungeondraft_map (sopra ai miei muri poligonali) e l'ha risalvato da Dungeondraft: primo campione reale con contenuto cave noto, mai avuto prima. Analisi del diff blank_80x80 vs file di Jay:

1. LUNGHEZZA di cave.bitmap: risolta, non e affatto 'non lineare' come diceva SPEC.md/format.md. Formula esatta verificata sui 4 campioni noti (8x8->154, 30x30->1892, 50x25->2614, 80x80->13042, quest'ultimo dal file di Jay): L(w,h) = 2*w*h + (3*(w+h))//2 + 2 (floor division). Il blank_80x80 pristino ha gia L=13042 con tutti zeri: la lunghezza dipende SOLO da (width,height) della mappa, non dal contenuto disegnato. Vale la pena correggere docs/format.md indipendentemente dalla decisione finale (AC3 la richiede solo se si sceglie il layer nativo, ma qui e un fatto assodato su un punto dati indipendente, non un'ipotesi).

2. VALORE/forma: molto piu difficile. Il file di Jay ha 1438 byte diversi da zero su 13042, con MOLTI valori distinti (51 valori unici: 1,3,7,12,13,14,15,25,28,31,55,56,59,62,63,112,119,120,124,...) non un semplice 0/1 - quindi NON e una maschera booleana per quadretto. La maggior parte dei valori sono run di bit consecutivi (7=0b111, 15=0b1111, 63=0b111111, 112=0b1110000...), compatibile con una codifica di copertura/antialiasing per bordo (tipica di un editor che smussa i contorni), ma alcuni (13, 25, 59) hanno bit isolati che non tornano con quello schema. Ho provato a ricostruire la griglia 2D testando vari (header, larghezza-riga) per coerenza spaziale (i migliori candidati: header=2 con riga da 163 elementi=~2*80+3, oppure larghezza 40/41 con molte righe) - nessuna delle due da una forma pulita e inequivocabile: la piu promettente (header=2, riga=163) mostra una banda coerente ma con un pattern diagonale ripetuto 4 volte che assomiglia a un dither/retinatura sul bordo, non un contorno netto.

Conclusione: la LUNGHEZZA e risolta (aggiornero docs/format.md). La CODIFICA DEI VALORI resta irrisolta con questo solo campione (una singola macchia disegnata a mano libera, bordi non netti). Per proseguire servirebbe un esperimento controllato: Jay disegna UNA forma semplice e netta (es. un rettangolo pieno in una posizione nota, niente mano libera) cosi il confine e inequivocabile e si puo mappare byte->quadretto senza ambiguita. Chiesto a Jay se vuole investire in questo esperimento o accettare la ricaduta AC4 sui muri poligonali (che e comunque la prescrizione di default di SPEC.md 9.3).

SVOLTA: la codifica di cave.bitmap E' RISOLTA, grazie al secondo campione controllato di Jay (rettangolo netto ~20x3 in alto a sinistra, generated/cave_bitmap_experiment.dungeondraft_map).

La chiave era nella spaziatura NON costante fra le run di byte non-nulli (40, 40, 41, 40, 40, 41, ...): non un array di byte per riga, ma un FLUSSO DI BIT continuo non allineato al byte, in cui l'offset in byte della riga k e floor(k*W/8).

CODIFICA COMPLETA:
- griglia di (4w+3) x (4h+3) BIT: 4 sotto-celle per quadretto (0.25 quadretti di risoluzione), piu 3 sotto-celle di margine per lato
- riga per riga (row-major), flusso di bit CONTINUO: le righe non ricominciano su un confine di byte
- dentro ogni byte, bit MENO significativo per primo (LSB-first). Con MSB-first la forma decodificata e rumore dithered, con LSB-first e un rettangolo pulito: non ambiguo.
- 1 = grotta scavata, 0 = roccia intatta
- lunghezza in byte = ceil((4w+3)*(4h+3)/8)

La formula di lunghezza che avevo derivato prima (2wh + floor(3(w+h)/2) + 2) e algebricamente la stessa cosa, ma era un fit a 3 parametri su 3 punti, cioe senza contenuto informativo; questa invece e strutturale e spiega PERCHE. Verificata su tutti e 4 i campioni noti: 8x8 -> griglia 35x35 = 1225 bit -> 154 B; 30x30 -> 123x123 -> 1892 B; 50x25 -> 203x103 -> 2614 B; 80x80 -> 323x323 -> 13042 B. Tutti esatti. Cade quindi anche l'affermazione di SPEC.md 2 / format.md 5 che la lunghezza sia 'non lineare' e non ricavabile: e semplicemente quadratica perche la griglia e a 4x.

PROVE (non solo la formula):
1. Round-trip byte-esatto: decode->encode riproduce i blob originali IDENTICI, su bitmap ed entrance_bitmap di entrambi i file di Jay (4 blob su 4).
2. Il file di calibrazione decodifica in un rettangolo di 21x3 quadretti esatti agli angoli arrotondati (la forma del pennello), in alto a sinistra: combacia con quanto Jay dice di aver disegnato ('circa 20x3, in alto a sinistra').
3. Il primo file freehand decodifica in una caverna organica con un tunnel serpeggiante - una forma palesemente disegnata a mano, non rumore.

RESTA UN SOLO DUBBIO: l'origine della griglia. Assumo sotto-cella 0 = quadretto 0, con le 3 sotto-celle di margine IN CODA. L'alternativa (margine in testa, cioe indice i -> quadretto (i-1)/4) e indistinguibile dai dati che ho, perche Jay ha descritto la posizione solo a parole ('in alto a sinistra'). Scarto max: 0.75 quadretti. Risolto dal file di calibrazione in scrittura, sotto.

SCRITTURA: scripts/cave_spike.py ora ha --mode native|calib oltre a walls. Generati generated/cave_native_calib.dungeondraft_map (rettangolo ESATTO sui quadretti x 10..20, y 10..15) e generated/cave_native.dungeondraft_map (stesso CA del prototipo a muri, ma girato a risoluzione sotto-cella: contorno 4 volte piu fine). Entrambi: lunghezza del blob identica a quella del template (13042 B), gli altri campi di cave (ground_color/wall_color/texture) intatti, 0 muri e 0 pattern, e 'ddforge validate' pulito - senza nemmeno l'avviso DDF102 che il prototipo a muri produce, perche non c'e nessun muro da scambiare per stanza isolata.

Giudizio di Jay gia acquisito sul prototipo a muri poligonali (AC1): contorno a gradini ACCETTABILE. La decisione (AC2) non e quindi piu forzata dal fallimento della decodifica: va presa sul merito, dopo che Jay ha aperto i due file nativi.

ESITO FINALE. Jay ha aperto i due file nativi: 'I due file fanno quello che ti aspetti e vanno bene'. Questo chiude i due punti aperti:
1. Il rettangolo di calibrazione compare esattamente sui quadretti x 10-20, y 10-15 -> l'origine e confermata: sotto-cella 0 = quadretto 0, le 3 sotto-celle di margine stanno IN CODA. Il formato e quindi verificato anche in SCRITTURA, non solo in lettura.
2. La grotta nativa da cellular automata a risoluzione sotto-cella e approvata visivamente.

Decisione: LAYER CAVE NATIVO. Registrata in backlog/decisions/decision-1 con le motivazioni (risoluzione 4x, rendering della roccia fatto da Dungeondraft, formato verificato in scrittura, meno elementi nel documento, niente falso positivo DDF102) e con le conseguenze operative per TASK-32/TASK-33.

Nota sulla decision: 'backlog decision create' crea solo lo scheletro (frontmatter + tre sezioni vuote) e NON esiste un 'decision update' ne un tool MCP per le decision. Il corpo e stato quindi scritto direttamente nel file, lasciando intatto il frontmatter generato dal CLI. E' l'unica via disponibile; la regola di CLAUDE.md ('non editare i file markdown direttamente') protegge metadati e relazioni, che qui non sono stati toccati.

docs/format.md: aggiunta la 14 con la codifica completa e la tabella delle prove; corretta la 11, che riportava la lunghezza del bitmap come 'non lineare' sulla scorta di SPEC.md 2.

AC4 NON spuntata di proposito: la sua precondizione ('se la decodifica non riesce') non si e verificata. La decodifica e riuscita e la decisione NON e ricaduta sui muri poligonali. Spuntarla farebbe leggere il contrario di quello che e successo. La milestone non e comunque bloccata, che era lo scopo della rete di sicurezza.

DANNO COLLATERALE, da sapere: rigenerando i file dello spike ho sovrascritto generated/cave_spike.dungeondraft_map, che conteneva la grotta a mano libera disegnata da Jay. Quel campione e perso. Non cambia nessuna conclusione (la codifica e confermata dal campione controllato cave_bitmap_experiment.dungeondraft_map, ancora intatto, piu il round-trip byte-esatto e la verifica in scrittura), ma era una fonte primaria. Da qui la proposta di follow-up: i campioni disegnati a mano da Jay sono l'UNICA evidenza reale del formato cave e vivono in generated/, che e gitignored. Andrebbero promossi a fixture committate (tests/fixtures/) prima di TASK-32, che ne avra bisogno per i test del codec.

CORREZIONE alla nota precedente + campioni promossi a fixture (su richiesta di Jay, dopo la chiusura del task).

Il campione a mano libera NON e perso: Dungeondraft ne teneva una copia in %AppData%/Roaming/Dungeondraft/backups/cave_spike.dungeondraft_map (stessa dimensione, 1671610 B, e stesso contenuto del file che avevo sovrascritto: 1438 byte non nulli, 1 wall, 1 pattern). Recuperato e verificato: decodifica nella stessa caverna organica di prima. La nota precedente che lo dava per distrutto e superata.

Entrambi i campioni genuini sono ora fixture committate, non piu file in generated/ (gitignored):
- tests/fixtures/cave_rect_80x80.dungeondraft_map (da generated/cave_bitmap_experiment.dungeondraft_map) - il rettangolo controllato 21x3
- tests/fixtures/cave_freehand_80x80.dungeondraft_map (dal backup di Dungeondraft) - la caverna a mano libera

Aggiunte le fixture pytest cave_rect_path / cave_freehand_path in tests/conftest.py con la provenienza, e tests/test_cave_bitmap_format.py (6 test) che blocca: formula della lunghezza sui 4 campioni noti, lunghezza reale dei blob dei due campioni, round-trip byte-esatto su bitmap ED entrance_bitmap di entrambi, forma decodificata del rettangolo (3.0 x 21.0 quadretti esatti), forma decodificata della caverna (macchia connessa, non rumore), e cave vuoto nel template blank.

I test importano il codec da scripts/cave_spike.py, stesso schema gia usato da tests/test_demo_m1.py. Vanno reindirizzati quando TASK-32 portera il codec in src/ddforge/ - annotato in docs/format.md 14.

Una precisazione emersa scrivendo i test: la connettivita della macchia NON discrimina l'ordine dei bit (misurato: MSB-first da 0.941 contro 0.993 di LSB-first, margine troppo sottile). A inchiodare la codifica e solo il round-trip byte-esatto. Il commento nel test dice esplicitamente questo, per non far credere a chi lo legge che quel test provi piu di quanto prova.

Suite: 350 passed, 1 skipped (erano 344+1; +6 nuovi, nessuna regressione).
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-07 10:01
---
File pronto per il gate visivo (AC1): generated/cave_spike.dungeondraft_map (grotta 36x26 quadretti, cellular automata seed 1337, contorno tracciato per lati di cella - non e ancora marching squares con interpolazione, deliberatamente, vedi implementation plan). Rigenerabile con 'python scripts/cave_spike.py --seed 1337'. Passa 'ddforge validate' con 0 errori, 1 avviso DDF102 non bloccante e atteso (nessuna porta su un muro chiuso, previsto per una grotta senza ingressi in questo spike). Anteprima SVG grezza (mia, non da Dungeondraft) gia inviata in chat per un primo colpo d'occhio.

Jay, quando puoi aprilo in Dungeondraft e dimmi: il contorno a gradini (niente smussature/diagonali, solo lati verticali/orizzontali) e accettabile per una grotta, o serve per forza il layer nativo piu organico? Ho gia verificato che decodificare cave.bitmap con i soli 3 campioni noti (docs/format.md) non porta a una formula pulita, quindi senza nuovi export da Dungeondraft con contenuto cave noto il layer nativo resta fuori portata (AC4).
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Spike chiuso con una decisione motivata: **le grotte si generano scrivendo il layer `cave` nativo di Dungeondraft**, non come muri poligonali. Registrata in `backlog/decisions/decision-1` (AC2).

L'esito e opposto a quello che il task si aspettava. SPEC.md 9.3 prescriveva di ripiegare sui muri poligonali perche la codifica di `cave.bitmap` era data per irrisolvibile, e AC4 era la rete di sicurezza per quel caso. Invece la codifica e stata risolta per intero, quindi la scelta e stata fatta sul merito e non per rinuncia.

**La codifica** (documentata in `docs/format.md` 14, AC3): maschera bit-packed su una griglia di `(4w+3) x (4h+3)` BIT — 4 sotto-celle per quadretto — row-major, flusso di bit continuo **non allineato al byte**, **LSB-first** dentro ogni byte, `1` = scavato. Lunghezza = `ceil((4w+3)(4h+3)/8)`, dipendente solo dalle dimensioni della mappa. Cade quindi l'affermazione di SPEC.md 2 che la lunghezza sia "non lineare": e quadratica perche la griglia e a 4x. Corretta anche `docs/format.md` 11, che la riportava.

Le due trappole che avevano fatto arenare l'analisi precedente: (a) il termine dominante e `2wh` byte, non `wh/8`, quindi interpolare fra tre punti non ci arriva; (b) il passo fra le righe **in byte** non e costante (40, 40, 41, 40, 40, 41, ...) perche una riga di 323 bit non e multipla di 8 — cercare una larghezza di riga in byte, che e l'istinto, non puo funzionare.

**Verifica** (AC3 chiede gli esperimenti che la confermano):
- formula di lunghezza esatta su tutti e 4 i campioni noti (8x8→154, 30x30→1892, 50x25→2614, 80x80→13042);
- round-trip `decode`→`encode` **byte-identico** sui blob reali, 4 su 4 (`bitmap` + `entrance_bitmap` di 2 file disegnati da Jay);
- il campione controllato decodifica in un rettangolo di 21x3 quadretti con gli angoli arrotondati dal pennello, in alto a sinistra, coerente con quanto Jay dice di aver disegnato;
- il campione a mano libera decodifica in una caverna organica con tunnel serpeggiante;
- **in scrittura**: un rettangolo generato da noi sui quadretti x 10-20, y 10-15 e riaperto da Jay compare esattamente li — il che conferma anche l'origine della griglia (sotto-cella 0 = quadretto 0, le 3 di margine in coda), l'unico punto che la sola lettura non poteva risolvere;
- **in scrittura**: una grotta da cellular automata a risoluzione sotto-cella, approvata da Jay.

Le prime quattro provano che sappiamo leggere il formato; solo le ultime due che sappiamo scriverlo e che Dungeondraft accetta cio che scriviamo.

**Prototipo a muri poligonali** (AC1): realizzato in `scripts/cave_spike.py --mode walls` (cellular automata + contorno tracciato per lati di cella + `add_wall(loop=True)` e `add_polygon_pattern`), aperto da Jay in Dungeondraft e giudicato **accettabile**. Resta quindi una via di riserva valida e verificata, non una strada scartata a priori — e questo e cio che rende la decisione una scelta e non un obbligo.

**Perche il nativo vince comunque**: risoluzione 4 volte piu fine (su una grotta l'irregolarita *e* la forma); ombreggiatura e smussatura della roccia le fa Dungeondraft invece di usare un muro da edificio per una parete di caverna; il documento risulta piu leggero (un blob di lunghezza fissa, gia presente anche nel template vuoto, invece di un muro con centinaia di punti piu un pattern); e `ddforge validate` esce pulito, mentre la versione a muri produce il falso positivo DDF102 gia noto (`docs/format.md` 9.5).

**Verifica di non-regressione**: suite completa 344 passed, 1 skipped. I tre modi dello spike rigenerati da zero e rivalidati (`walls` 0 errori/1 avviso DDF102 atteso, `native` e `calib` nessun problema).

**AC4 lasciata non spuntata di proposito**: la sua precondizione ("se la decodifica non riesce") non si e verificata, e la decisione non e ricaduta sui muri poligonali. Spuntarla farebbe leggere il contrario di quello che e successo. Lo scopo della rete di sicurezza — non bloccare M5 — e comunque raggiunto.

**Perimetro rispettato**: nessuna modifica a `src/ddforge/`. `generators/cave.py` resta `NotImplementedError`, di competenza di TASK-32. Il codec vive in `scripts/cave_spike.py` come codice di spike e va portato in `src/` **con i test**: oggi il round-trip e verificato a mano, non dalla suite.

**Rischi / follow-up da valutare con Jay**:
1. I campioni disegnati a mano sono l'unica evidenza reale del formato cave e vivono in `generated/`, che e **gitignored**. Andrebbero promossi a fixture committate prima di TASK-32. Reso urgente da un mio errore: rigenerando i file dello spike ho sovrascritto `generated/cave_spike.dungeondraft_map`, distruggendo il campione a mano libera di Jay (nessuna conclusione ne dipende, ma la fonte primaria e persa).
2. `cave.entrance_bitmap` ha la stessa identica codifica ma e tutto a zero in ogni campione disponibile: **non e ancora stato studiato**, ed e il candidato naturale per collegare una grotta a una struttura costruita. Serve se TASK-32/TASK-33 devono raccordare grotte e dungeon.
3. Una grotta nativa non ha `walls`, quindi non ha `portals`: le porte annidate nei muri (`compose.connect`) non si applicano.
4. Per le **fognature** (TASK-33), a canali ortogonali, i bordi dritti sono voluti: questa decisione riguarda le grotte, per le fognature va rivalutata.

**Aggiornamento dopo la chiusura (richiesta di Jay): campioni promossi a fixture.**

Il campione a mano libera che davo per distrutto **e stato recuperato** dai backup automatici di Dungeondraft (`%AppData%/Roaming/Dungeondraft/backups/`), verificato identico all'originale. Il rischio n.1 elencato sopra e quindi chiuso, non solo mitigato.

Entrambi i campioni genuini sono ora committati come fixture, invece di vivere in `generated/` che e gitignored:
- `tests/fixtures/cave_rect_80x80.dungeondraft_map` — il rettangolo controllato 21x3
- `tests/fixtures/cave_freehand_80x80.dungeondraft_map` — la caverna a mano libera

Sono l'unica evidenza reale di questo formato in tutto il progetto: nessun altro `.dungeondraft_map` sul sistema di Jay ha il layer cave popolato.

Aggiunti `cave_rect_path` / `cave_freehand_path` a `tests/conftest.py` (con la provenienza nei docstring) e `tests/test_cave_bitmap_format.py`, 6 test che bloccano la scoperta: formula della lunghezza sui 4 campioni noti, lunghezza reale dei due blob, **round-trip byte-esatto** su `bitmap` ed `entrance_bitmap` di entrambi, forma decodificata del rettangolo (3.0 x 21.0 quadretti esatti), forma della caverna (macchia connessa al 99.3%, non rumore), e cave vuoto nel template blank.

Una precisazione emersa scrivendo i test, annotata sia nel test sia in `docs/format.md` §14: la connettivita della macchia **non** discrimina l'ordine dei bit (MSB-first da 0.941 contro 0.993 di LSB-first, margine troppo sottile per essere una prova). A inchiodare la codifica e solo il round-trip byte-esatto.

I test importano il codec da `scripts/cave_spike.py`, stesso schema di `tests/test_demo_m1.py`: vanno reindirizzati quando TASK-32 portera il codec in `src/ddforge/`.

Suite: **350 passed, 1 skipped** (+6, nessuna regressione).
<!-- SECTION:FINAL_SUMMARY:END -->
