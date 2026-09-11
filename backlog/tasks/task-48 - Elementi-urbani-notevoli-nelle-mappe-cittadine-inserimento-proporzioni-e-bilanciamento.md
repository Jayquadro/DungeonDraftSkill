---
id: TASK-48
title: >-
  Elementi urbani notevoli nelle mappe cittadine: inserimento, proporzioni e
  bilanciamento
status: In Progress
assignee:
  - '@claude'
created_date: '2026-09-09 08:36'
updated_date: '2026-09-11 13:25'
labels: []
milestone: m-8
dependencies:
  - TASK-41
documentation:
  - docs/SPEC.md
type: feature
ordinal: 48000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Oggi generators/city.py produce una citta di soli edifici anonimi, strade e 1-2 piazze con una fontana. Una citta giocabile ha invece dei luoghi: e da quelli che il tavolo si orienta, ed e per quelli che i giocatori ci vanno. Questo task introduce gli elementi urbani notevoli, richiedibili esplicitamente oppure estratti a sorte quando non sono richiesti, e ne bilancia le proporzioni.

ELENCO DI PARTENZA (Jay). Luoghi di culto e potere: templi; monasteri e conventi; palazzo del signore/governatore; caserma della guardia cittadina. Commercio: mercato principale (piazza del mercato); mercati specializzati (pesce, bestiame, spezie, mercato nero); banche o case di cambio; magazzini e depositi; porto/molo (se citta costiera o fluviale). Sapere: biblioteca cittadina o arcana; accademia/collegio di magia; bottega di alchimista. Svago e servizi: taverne e locande; bordelli/case di piacere; bagni pubblici/terme; arena o anfiteatro; teatro. Artigianato: fabbro/armeria; bottega dell'incantatore (oggetti magici); stalle e maniscalco; fornaio, macellaio e altre botteghe alimentari. Struttura urbana: mura cittadine con porte fortificate; torri di guardia; fiumi e ponti (levatoi o fissi); pozzi pubblici; statue o monumenti; fontana centrale; giardini pubblici; cimitero.

AGGIUNTE PROPOSTE, con il motivo per cui valgono la pena (sono quasi tutte elementi che portano con se una REGOLA DI PIAZZAMENTO, cioe rendono la citta leggibile invece di aggiungere solo varieta): municipio o sala del consiglio, e sedi di gilda (mercanti, artigiani, ladri) - il potere civile accanto a quello del signore; dogana o ufficio del dazio, che va alle porte; conceria e tintoria, che vanno a valle del fiume e ai margini (i mestieri che puzzano stanno sottovento: e una regola di zonizzazione storica che si legge sulla mappa); macello, per lo stesso motivo; mulino ad acqua sul fiume o a vento su un'altura; prigione o torre di detenzione, distinta dalla caserma; lazzaretto/ospizio e orfanotrofio; cantiere navale e faro, solo se c'e il porto; acquedotto o cisterna; chiusini/grate delle fognature sulle strade principali, che sono anche l'aggancio naturale a generators/sewer.py; quartiere povero o baraccopoli ai margini o fuori le mura; fiera o campo fuori le mura; cappelle minori ed edicole votive; torre dell'orologio o campanile; quartiere straniero/ghetto e ambasciate; patibolo o gogna sulla piazza principale; fossato, bastioni, barbacane e postierla come corredo delle mura; guado e ponte coperto come varianti dell'attraversamento; catacombe o ipogei (il solo accesso), altro aggancio a sewer/cave.

IL PUNTO DIFFICILE E' LA PROPORZIONE, non l'inventario. Tre assi da bilanciare, ed e per questo che il task chiede esplicitamente di testarli e non solo di implementarli:
1. QUANTI. Una citta ha UN palazzo del signore e UNA cattedrale, ma dieci taverne e trenta botteghe. Le quantita vanno legate alla dimensione della mappa (o al numero di edifici generati), non fissate a un numero assoluto, altrimenti un quartiere piccolo si ritrova tre arene.
2. A QUALE SCALA. Dopo TASK-41 i preset sono tre (isolato, quartiere, citta): un fornaio ha senso al preset isolato, dove si vede la bottega; su una mappa di citta intera si segnano la cattedrale, il palazzo, le mura, il porto e i mercati, non le panetterie. Ogni elemento va quindi dichiarato per quali preset e ammissibile.
3. DOVE. Gli elementi con una regola di piazzamento valgono molto piu di quelli sparsi a caso: dogana alle porte, mulino e conceria sul fiume (la conceria a valle), cimitero fuori le mura o presso il tempio, mercato sulla piazza, patibolo sulla piazza principale, cantiere e faro sul porto, quartiere povero ai margini.

Da decidere in fase di piano, non qui: se un elemento sia un edificio con una tipologia propria (come le tipologie di building.py), un object da asset pack (come fara TASK-46 per le case), un isolato intero dedicato (un monastero o un'arena occupano un isolato, non un lotto), o un elemento strutturale che rimodella la mappa. Gli ultimi due casi non sono decorazioni: mura, fiumi e ponti cambiano la partizione degli isolati e la rete stradale, quindi potrebbero meritare un task separato - valutarlo al piano ed eventualmente proporre lo scorporo.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Un parametro della CLI permette di chiedere esplicitamente uno o piu elementi urbani per la mappa generata
- [x] #2 Senza richiesta esplicita gli elementi vengono estratti a sorte in modo riproducibile dal seed, e due seed diversi danno citta con luoghi diversi
- [x] #3 Ogni elemento dichiara a quali preset di scala e ammissibile, e un elemento non ammissibile per il preset scelto non viene mai piazzato
- [x] #4 Le quantita sono proporzionali alla dimensione della mappa e non a numeri assoluti: gli elementi unici (palazzo del signore, cattedrale, arena) compaiono al piu una volta, quelli comuni (taverne, botteghe) crescono col numero di edifici
- [x] #5 Gli elementi con una regola di piazzamento la rispettano in modo verificabile: almeno dogana alle porte, mulino e conceria sul fiume con la conceria a valle, cimitero fuori le mura o presso il tempio, mercato e patibolo sulla piazza, cantiere e faro sul porto
- [x] #6 Gli elementi non si sovrappongono fra loro ne a strade, piazze o edifici esistenti
- [x] #7 Le proporzioni risultanti sono misurate e documentate su piu seed e per ciascun preset, non solo affermate
- [x] #8 Il documento generato passa validate() senza errori in tutti i preset e con e senza elementi richiesti
- [ ] #9 Jay apre in Dungeondraft una mappa per preset e conferma che i luoghi si riconoscono e le proporzioni reggono al tavolo
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
DECISIONI DI PIANO (le due che il task lascia esplicitamente qui, confermate da Jay il 2026-09-10):
A. NIENTE SCORPORO: mura+porte, fiume+ponti e porto stanno in TASK-48. Senza di loro AC5 (dogana alle porte, mulino/conceria sul fiume, cimitero fuori le mura, cantiere/faro sul porto) non e' verificabile: sono la precondizione delle regole di piazzamento, non un abbellimento separabile.
B. RAPPRESENTAZIONE: ogni luogo = ingombro + sprite dal pack + etichetta 'text' col nome. L'etichetta e' cio' che rende il luogo riconoscibile (AC9) anche dove nessuno sprite del catalogo e' calzante, in tutti e tre i preset (i kind ammessi alla scala 'citta' sono pochi e quasi tutti unici, quindi le etichette non affollano).

1. model.py — nuovi dataclass Landmark(kind,label,rect,site), CityWalls(ring,thickness,gates), Gate(x,y,side), River(points,width), Bridge(rect,horizontal), Port(water,quay,side). Nuovi campi opzionali su Blueprint: landmarks, walls, river, bridges, port. Stesso trattamento gia' dato a streets/plazas/buildings: campi dedicati al generatore cittadino, vuoti/None per gli altri generatori.

2. src/ddforge/generators/landmarks.py — catalogo dati LANDMARK_KINDS: per ogni luogo (key, label, scales ammesse [AC3], unique/rate+max [AC4], site in {lot,block,plaza,band}, rule in {any,gate,river,river_downstream,outside_walls_or_temple,plaza,main_plaza,port,edge} [AC5], marker sprite, ingombro-bersaglio). Piu' select(): estrazione riproducibile dal seed (AC2) unita alle richieste esplicite (AC1), con le quantita' derivate dal numero di edifici generati e mai da costanti assolute (AC4).

3. generators/city.py — riordino di generate():
   a. features strutturali PRIMA della partizione: porto (fascia d'acqua su un bordo) e mura (anello inset) riducono il rect radice, cosi' edifici e strade nascono gia' dentro le mura per costruzione;
   b. partizione/lotti/edifici invariati, ma i lotti vengono conservati (lot, front, indice edificio) invece di essere consumati inline: servono come siti candidati per i luoghi;
   c. fiume: polilinea da bordo a bordo (stessa meccanica di _avenue), gli edifici attraversati vengono tolti; verso di scorrimento = points[0]->points[-1];
   d. porte: dove l'ingombro di una via tocca l'anello delle mura; ponti: intersezione fra la polilinea di una via e quella del fiume;
   e. luoghi: ogni kind selezionato cerca un sito che soddisfa la sua regola, occupa il lotto/isolato/fascia (rimuovendo l'edificio che c'era) e viene registrato in blueprint.landmarks. Un kind con regola che non trova sito NON viene piazzato altrove: e' cosi' che AC5 resta un invariante e non una tendenza. Occupazione tracciata in una lista, cosi' nessun luogo si sovrappone a un altro, a un edificio, a una strada (AC6).

4. assets.py — Palette.landmark_markers (sprite per kind, chiavi letterali dal catalogo come gia' fatto per building_variants), piu' le texture strutturali gia' in catalogo: bb_wall_path (mura), bb_river_path (fiume), bb_shore_path (porto).

5. compose.py — draw_landmark (pattern+sprite+add_text), draw_city_walls, draw_river (path + add_water_polygon), draw_port, draw_bridge; integrazione in render_city_blueprint. font_size dell'etichetta tarato per preset.

6. cli.py — --landmark KIND ripetibile (AC1) e --no-landmarks; --landmark accetta anche porto/mura/fiume, cosi' anche le strutture si chiedono con lo stesso parametro.

7. Test: nuovo tests/test_city_landmarks.py (una classe di test per AC, con AC5 verificata come invariante geometrico su piu' seed x preset) piu' estensioni a test_generators_city.py e test_cli_generate.py. Golden file del preset isolato da rigenerare (i luoghi cambiano il documento): differenza motivata nelle note.

8. AC7 — scripts/city_landmarks_census.py: genera N seed x 3 preset, misura quantita' per kind, rapporto luoghi/edifici e rispetto delle regole, stampa la tabella. Tabella COMMITTATA in docs/SPEC.md §9.4 (misurata, non affermata).

9. Documentazione: docs/SPEC.md §9.4, README.md, skill/references/styles.md, docs/format.md (se serve per water/text).

10. AC9 (gate umano) — generare i tre file reali (uno per preset) in generated/ e chiedere a Jay di aprirli in Dungeondraft. Il task resta In Progress finche' non risponde.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
IMPLEMENTAZIONE COMPLETA (2026-09-10). Suite: 733 passed, 1 skipped, zero regressioni.

DECISIONI DI PIANO PRESE (quelle che il task lasciava esplicitamente all'implementazione), confermate da Jay:
1. NIENTE SCORPORO delle strutture urbane. Mura+porte, fiume+ponti e porto stanno qui: senza di loro AC5 non e' verificabile (dogana alle porte, mulino/conceria sul fiume, cimitero fuori le mura, cantiere/faro sul porto). Sono la precondizione delle regole, non un abbellimento separabile.
2. RAPPRESENTAZIONE: ingombro + sprite dal pack + ETICHETTA 'text' col nome. L'etichetta e' cio' che rende il luogo riconoscibile dove nessuno sprite del catalogo e' calzante (municipio, casa di cambio, dogana...). Primo uso in produzione di build.add_text in tutto il progetto.
3. Un luogo NON e' un edificio con un cartello sopra: al preset isolato viene RIGENERATO con building.generate sulla tipologia della sua destinazione d'uso (landmarks.BUILDING_TYPE: taverna->tavern, tempio/palazzo->manor, conceria/magazzino->warehouse, resto->house), sull'ingombro complessivo dei lotti che occupa.

COSA E' STATO SCRITTO
- src/ddforge/generators/landmarks.py (nuovo): catalogo di 40 luoghi come dati. Ogni voce dichiara scales (AC3), unique/rate+max_count (AC4), site (lot/block/plaza/band) e rule (AC5), sprite e ingombro in lotti. Piu' STRUCTURE_SCALES/STRUCTURE_CHANCE per mura/fiume/porto, select()/select_structures() (estrazione dal seed + richieste esplicite) e check_requested().
- model.py: Gate, CityWalls, River, Bridge, Port, Landmark; nuovi campi Blueprint landmarks/walls/river/bridges/port.
- generators/city.py: generate() riordinata. Le strutture si decidono PRIMA di strade ed edifici e riducono l'area edificabile (il porto sottrae una fascia di canvas, le mura un anello), cosi' 'dentro le mura' e 'sul mare' sono veri per costruzione. I lotti non vengono piu' consumati e buttati: restano come siti su cui un luogo prende il posto di una casa. Piu' _make_port, _make_river, _river_bridges, _wall_gates, il motore di piazzamento (_lot/_block/_plaza/_band_candidates, _rule_ok, _claim, _place_landmarks).
- assets.py: Palette.paths (mura/fiume/banchina, dalle 6 texture path del pack 6VxwaRdj gia' in catalogo) e Palette.landmark_markers (18 sprite, chiavi letterali). Nuovi floors sintetici: luogo, banchina, ponte.
- compose.py: draw_city_walls (anello SPEZZATO a ogni porta, riusando _subtract_intervals), draw_river, draw_bridge, draw_port (poligono d'acqua nativo + banchina + riva), draw_landmark + _draw_markers + _label_font_size. Agganciate in render_city_blueprint nell'ordine giusto (acqua sotto, mura sopra i tetti, etichette per ultime).
- cli.py: --landmark ELEMENTO ripetibile (accetta anche mura/fiume/porto) e --no-landmarks; elemento non ammissibile per il --scale = errore esplicito su stderr, exit 1, nessun file scritto, nessun traceback.

TRE DIFETTI TROVATI E CORRETTI DURANTE IL LAVORO, tutti reali:
a) Riproducibilita' rotta fra processi: il seed dell'edificio di un luogo usava hash(kind.key), e l'hash delle stringhe di Python e' randomizzato per processo. Due esecuzioni della stessa riga di comando davano due mappe diverse. Sostituito con zlib.crc32. Trovato dal test di riproducibilita' della CLI (gira in sottoprocesso): dai test in-process non si vedeva.
b) Due regole di AC5 non vincolavano nulla: municipio/banca ('sulla piazza') e monastero ('ai margini') stanno su siti lot/block, ma _rule_ok si fidava del tipo di sito e rispondeva True. Finivano dove capitava. Ora OGNI regola e' verificata geometricamente, anche quelle che il sito garantirebbe.
c) Sulla banchina nessun luogo largo piu' di una cella trovava posto: e' una striscia stretta e lunga, la sua griglia viene di 1 colonna x 25 righe, e _cell_runs cercava finestre solo per riga. Il porto restava senza cantiere navale. Ora si cerca per riga E per colonna. Trovato disegnando il Blueprint, non da un test.

TARATURA (misurata, non scelta a occhio): la fascia di margine al 9% del lato mangiava un terzo della mappa al preset citta (8 lotti di profondita'); ridotta al 6% con un tetto di 2,5 lotti. Il porto con la sola frazione dava una banchina piu' stretta di un lotto e restava deserto; ora la profondita' ha un minimo che garantisce una banchina di almeno un lotto. Il budget dei luoghi comuni era 'primo arrivato primo servito' e azzerava gli ultimi del catalogo (statue 0,03 e giardini 0,00 per mappa al preset quartiere); ora si applica in proporzione fra i kind.

NON REGRESSIONE VERIFICATA: con --no-landmarks l'output e' BYTE-IDENTICO a prima del task. Il golden file di TASK-46 (tests/fixtures/golden/city_seed_1337.json) NON e' stato rigenerato e ora fa da garanzia: la rete stradale, gli isolati, i lotti e gli edifici approvati al gate M5 non si sono spostati di un pixel. Il documento completo ha un secondo golden (city_seed_1337_landmarks.json), rigenerabile con scripts/regen_city_golden.py.

TEST: nuovo tests/test_city_landmarks.py, 96 test, una sezione per AC. Le regole di AC5 sono verificate con geometria scritta nel test, non richiamando city._rule_ok (dal modulo si prende solo la tolleranza dichiarata). Ogni test di regola fallisce se non ha incontrato nemmeno un luogo da verificare. Aggiornati test_generators_city.py (i due test di taratura dei preset girano con landmarks=False: misurano la scala, e i luoghi la sporcherebbero in modo asimmetrico) e test_cli_generate.py (3 test nuovi).

AC7: scripts/city_landmarks_census.py, misura su 30 seed x 3 preset. Tabelle committate in docs/SPEC.md 9.4.1. Sintesi: luoghi per mappa 9,4 (isolato) / 43,6 (quartiere) / 28,6 (citta); quota sul totale 32% / 22% / 1%; porte 2,80 per mappa quando ci sono mura; ponti 1,77 / 1,80 / 7,13.

DOCUMENTAZIONE: docs/SPEC.md nuova 9.4.1 (regole, proporzioni misurate, cosa e' fuori dall'inventario e perche'), README.md (tabella preset aggiornata + sezione sui luoghi), skill/references/styles.md, docs/format.md (nota sul primo uso di 'text' e sull'ancoraggio di position, ancora non verificato).

FUORI DALL'INVENTARIO DELLA DESCRIZIONE, per scelta e non per dimenticanza: chiusini delle fognature sulle strade, edicole votive, fossato/bastioni/barbacane, ponte coperto e guado. Non sono un ingombro con un nome e chiederebbero un tipo di sito proprio; sono un'aggiunta incrementale al catalogo, non una riprogettazione.

SECONDO GIRO (2026-09-10, dopo il primo riscontro di Jay sulla mappa vera). Suite: 736 passed, 1 skipped.

IL DIFETTO SEGNALATO: 'gli elementi importanti sono tutti bianchi, nella resa della mappa e' molto brutta'. Diagnosi: un luogo notevole era l'UNICO elemento della mappa non disegnato come sprite - una chiazza di pavimento (pattern con tileset_cobble) piu' un'iconcina. In mezzo a case che dal TASK-46 sono sprite colorati, leggeva come un rettangolo bianco.

COSA E' CAMBIATO
1. CATALOGO. Nuovo flag 'ddforge catalog --from-catalog': il catalogo esistente viene innestato per primo e le sue chiavi vincono. Serviva perche' le undici mappe della campagna da cui era nato il catalogo di TASK-45/46 non sono piu' sul disco, e rigenerare dai soli template avrebbe perso ~90 chiavi usate dalle palette (con loro gli stili tavern/manor/warehouse). Il vincolo sul pack orfano vale identico per il catalogo di partenza. Letti 8 pack: objects 106->440, object_sizes 57->396, paths/walls/floors 6->9. Zero chiavi perse o modificate, verificato chiave per chiave.
2. SPRITE PER OGNI LUOGO. Nuova Palette.landmark_sprites, indicizzata per chiave di luogo e non per nome di icona: 39 luoghi su 39 hanno il loro sprite. Piu' Palette.structure_sprites (torre sulla porta delle mura, impalcato del ponte). Rimossi Palette.landmark_markers, LandmarkKind.marker e Landmark.marker: lo sprite e' una scelta di catalogo asset, non di geometria.
3. REGOLA IMPARATA GUARDANDO IL RENDER: gli sprite BB ritraggono un complesso CON LE SUE PERTINENZE (l'abbazia su un'isola si porta dietro il mare, il maschio il fossato) e in mezzo a un quartiere fitto sono toppe di campagna. Sostituiti quasi tutti con edifici singoli su sfondo trasparente da CHR Town Maps, City Terrain e Lost Lands Hamlets; i BB restano solo dove il contorno e' giusto (faro sulla costa, anfiteatro con i suoi spalti).
4. SPIAZZI APERTI. Nuovo LandmarkKind.paved: mercato, patibolo e banchina hanno il selciato sotto gli sprite sparsi; cimitero, fiera, baraccopoli e giardino restano sul terreno, dove un selciato sarebbe sbagliato.
5. ETICHETTE. Scoperto misurando: text.font_size e' in PIXEL DI MONDO (256 per quadretto), quindi il 32 del solo campione osservato vale un ottavo di quadretto e a mappa intera non si vede. Ora il corpo si ricava dall'ingombro, chiedendo che il nome sia largo ~1,4 volte il luogo che nomina: un monumento ha un nome grande, una bottega un nome piccolo. L'etichetta sta sotto l'ingombro e non al centro (al centro copriva lo sprite). Nuovo compose._place_label: due nomi non si sovrappongono mai, la seconda etichetta va sopra invece che sotto e se non c'e' posto viene omessa - al preset quartiere i quaranta nomi si accavallavano fino a non leggersene nessuno.

MONUMENTI PIU' GRANDI: PROVATO E TOLTO. Jay aveva chiesto che cattedrale, palazzo, arena e monastero occupassero piu' isolati. Implementato (crescita golosa su isolati adiacenti, tetto al 12% del lato della mappa, controllo che il gruppo non inghiottisse lotti altrui) e poi rimosso: l'ingombro di un luogo e' un RETTANGOLO e fra due isolati la partizione mette sempre una via, quindi il monumento si portava dentro la strada - esattamente cio' che AC6 vieta. Il test test_landmarks_do_not_sit_on_a_street lo ha colto. Per farlo davvero servirebbe spezzare la via in due tronconi dove il monumento la ingloba: e' un lavoro sul modello delle strade, non un parametro in piu'. Il rilievo dei monumenti viene ora dallo sprite dedicato e dal corpo dell'etichetta.

GOLDEN FILE. Tutti e cinque rigenerati, e NON per una modifica al generatore: il commit 306f14f di Jay ha tolto il pack 2fXlBwjR dal manifest dei template. Confronto strutturale fatto prima di sovrascrivere su tutti e cinque: le uniche differenze erano header.asset_manifest e tiles.lookup, due campi che arrivano dal template e che il generatore non tocca; walls, objects, paths, patterns, roofs e texts identici elemento per elemento.

VERIFICA VISIVA. Scritto un renderer diagnostico usa-e-getta (fuori dal repo) che estrae gli sprite dai .dungeondraft_pack e compone il PNG, per guardare la mappa senza aprire Dungeondraft. E' cosi' che sono venuti fuori tre difetti che nessun test avrebbe preso: gli sprite BB con le pertinenze, le etichette invisibili e i nomi accavallati.

NUOVI TEST: test_two_labels_never_overlap (l'invariante dietro le etichette omesse) e test_landmarks_get_their_name_on_the_map (ogni testo scritto e' il nome di un luogo che c'e' davvero, e almeno il 90% dei luoghi ha il suo nome). test_a_multi_cell_landmark_fits_on_the_narrow_quay dal giro precedente.

RESTA APERTO PER JAY: le case ordinarie usano ancora gli sprite BB Houses1 scelti e approvati in TASK-46, che sono icone piatte colorabili, mentre i luoghi ora usano edifici dipinti di CHR Town Maps. I due registri grafici non combaciano. L'alternativa (case CHR house_01..12 + strawhouse, stesso pack dei luoghi) e' pronta e provata ma cambia una scelta che Jay aveva gia' approvato, quindi non e' stata applicata: decide lui.

TERZO GIRO (riscontro di Jay sulla mappa renderizzata). Quattro punti aperti, uno chiuso.

CHIUSO - PONTI SENZA SPRITE. compose.draw_bridge torna a disegnare il solo impalcato come pavimento, e 'bridge' esce da _CITY_STRUCTURE_SPRITES (resta la sola 'gate'). Motivo tecnico dietro la scelta di Jay: uno sprite di ponte e' UNA campata di dimensione fissa, mentre qui l'attraversamento e' lungo quanto il fiume e' largo e orientato come la via che lo incrocia - scalarlo per coprire l'attraversamento lo deformava, lasciarlo alla sua dimensione lasciava scoperta l'acqua ai lati. Nuovo test test_bridges_are_a_deck_and_not_a_sprite (un impalcato per ponte, nessuno sprite di ponte in palette) perche' la decisione non rientri per distrazione. Golden invariati: il seed 1337 a 70x70 non estrae il fiume. Suite completa 739 passed, 1 skipped.

APERTI, in ordine di dipendenza:
1. ETICHETTE: dimensione sbagliata e sovrapposte in Dungeondraft. La mia deduzione che font_size sia in pixel di mondo (256 per quadretto) e' smentita dal riscontro. Non tocco altro codice finche' non so come si comporta davvero: serve una striscia di calibrazione (stesso testo a corpo 32/64/128/256/384 accanto a un quadretto di riferimento) da far guardare a Jay, altrimenti e' il secondo tentativo a indovinare.
2. AREE COLORATE per i luoghi all'aperto (parchi, cimiteri): fatta solo meta'. _classify ha un bucket 'terrain' nuovo e il catalogo ha le dieci texture di terreno (chr_grass, chr_dirt, chr_cobblestones, bb_grass_terrain...), ma il rendering non le usa ancora. Resta da sostituire LandmarkKind.paved con un campo 'ground' a tre valori (selciato/verde/terra) e da verificare se Dungeondraft accetta una texture di categoria terrain dentro un elemento pattern - non e' verificato, ed e' il motivo per cui le ho tenute in un bucket separato da floors.
3. SPRITE BRUTTI: superato dalla richiesta successiva di Jay. Invece della mappa-campionario ha chiesto due documenti per commissionare un pacchetto dedicato, consegnati: docs/sprite-luoghi.md (54 pezzi con le misure vere a cui vengono disegnati, misurate su 20 seed per preset) e docs/prompt-sprite-pack.md (brief pronto). La mappa-campionario non e' stata fatta.

DIFETTO TROVATO MISURANDO PER IL BRIEF, non ancora corretto: compose._draw_landmark_sprites scala ogni pezzo sparso al 45% del lato dell'AREA invece che alla sua dimensione reale. Su un cimitero grande esce una lapide da 4,5 quadretti, cioe' alta quasi sette metri. Va corretto prima che arrivi un pacchetto disegnato alla scala giusta, altrimenti il pacchetto nuovo eredita il difetto.

QUARTO GIRO: le tre attivita' chieste da Jay. Suite 745 passed, 1 skipped.

1. AREE COLORATE (fatta). LandmarkKind.paved (booleano) diventa , chiave di Palette.floors: 'selciato' per mercato, patibolo, cantiere e mercato del pesce; 'verde' per giardino e cimitero; 'terra' per fiera e baraccopoli; None per la statua, che sta gia' su una piazza pavimentata e non ha bisogno di una seconda toppa sopra. Erba e terra battuta vengono dal bucket  del catalogo (chr_grass, chr_dirt): nei pattern non ci sono, i pack le mettono sotto /terrain/. NON e' verificato che Dungeondraft accetti una texture terrain dentro un elemento pattern - l'indizio a favore e' che il template ricco disegnato a mano da Jay usa come pattern texture di tilesets/simple/, quindi lo strumento non si limita a patterns/normal/. La conferma sta nel foglio di calibrazione.

2. DIFETTO DELLA SCALA DEGLI SPRITE SPARSI (corretto). Ogni pezzo si disegna alla sua dimensione NATIVA, che e' la sua dimensione reale perche' un pack e' disegnato a 256 px per quadretto, e si rimpicciolisce solo se lo spiazzo e' piu' piccolo del pezzo. Il numero di pezzi cresce con l'area a densita' costante (_SCATTER_SPACING) invece di essere un conteggio fisso, e i pezzi non si sovrappongono piu' fra loro (rejection sampling, 8 tentativi). Prima ogni pezzo era scalato al 45% del lato dell'area: su un cimitero grande usciva una lapide da 4,5 quadretti, alta quasi sette metri. Due test nuovi, uno geometrico e uno sul documento scritto (test_a_gravestone_is_the_same_size_in_a_big_and_a_small_cemetery: due cimiteri di dimensione molto diversa hanno lapidi UGUALI e il grande ne ha di piu').

3. CALIBRAZIONE ETICHETTE (strumento pronto, risposta da Jay). scripts/label_calibration.py genera un foglio che MISURA le tre cose che finora avevo dedotto e su cui ho sbagliato: quanto vale un corpo di font (dieci righe, corpi 16-384, ognuna ancorata al centro di un quadrato rosa di esattamente 1x1 quadretto), dove cade  rispetto al punto passato (l'ancoraggio, ignoto: un solo campione in tutto il progetto) e quanto e' largo un testo (righello di quadretti alternati sotto ogni riga). In fondo, una toppa per ogni texture di terreno candidata, che risponde anche alla domanda aperta del punto 1. Il calcolo del corpo NON e' stato toccato: cambiarlo ora sarebbe indovinare una seconda volta.

DIFETTO TROVATO GUARDANDO IL RENDER, corretto: al preset isolato l'83% dei luoghi chiusi ripiegava sullo sprite invece di ricevere un edificio a stanze, perche' il lotto era piu' stretto dei 6 quadretti che building.generate pretende - cioe' alla scala giocabile la taverna era una taverna in cui non si entra. _lot_candidates ora preferisce i lotti in cui l'edificio ci sta davvero: dal 17% al 55% di luoghi con geometria vera, misurato su 30 seed. Il ripiego resta per il resto, ed e' voluto.

DIFETTO NEL MIO RENDERER DIAGNOSTICO (fuori dal repo), che mi aveva fatto leggere male i giri precedenti: la regex dei numeri catturava il '2' dentro 'PoolVector2Array(', sfasando di uno tutte le coppie di coordinate. Ogni poligono usciva a cuneo e l'acqua del porto finiva dal lato sbagliato. Le posizioni degli sprite erano giuste (usano Vector2 con fullmatch), la geometria di aree, strade e mura no.

FILE PER JAY in generated/: calibrazione_etichette.dungeondraft_map (da guardare per primo, sblocca il resto) piu' i quattro city_*_task48 rigenerati.

Rettifica alla nota qui sopra: tre parole erano fra apici inversi e la shell le ha mangiate. Per esteso: (1) LandmarkKind.paved diventa il campo ground; (2) erba e terra battuta vengono dal bucket terrain del catalogo; (3) il foglio di calibrazione misura anche dove cade il campo position del testo rispetto al punto passato.

QUINTO GIRO: mappa campionario degli sprite. scripts/landmark_sprite_sheet.py, due modi in un solo file.

--write genera TRE fogli su templates/blank_160x160 (canvas 128x128): una riga per luogo, col nome a sinistra e tutti i candidati plausibili del catalogo affiancati in celle. Bande alternate per separare le righe. 40 righe in tutto (39 luoghi piu' la porta delle mura, che non e' un luogo ma ha lo stesso bisogno), 296 candidati, distribuite 14+14+12 invece di riempire un foglio alla volta - altrimenti il terzo foglio sarebbe stato di 4 righe su 18 e sarebbe sembrato rotto.

--read rilegge i fogli potati e stampa la tabella gia' pronta da incollare in assets._CITY_LANDMARK_SPRITES. L'appartenenza di uno sprite si ricava dalla RIGA (dalla sua y), non dalla texture: la stessa texture e' candidata per piu' luoghi, quindi per texture sarebbe ambiguo. Conseguenza per chi usa il foglio: cancellare quanto si vuole, ma non spostare uno sprite da una riga all'altra.

Verificato il giro completo: rilettura dei fogli intatti che riproduce tutti i 39 kind, e una potatura simulata (tengo solo il primo sprite di ogni riga) che produce esattamente la tabella attesa.

Due cose imparate generando il foglio:
- Il nome del luogo va al CENTRO della colonna di sinistra, non al suo bordo. Al bordo, se l'ancoraggio di text.position fosse il centro, meta' nome finirebbe fuori dal canvas - e infatti nel primo tentativo le etichette erano tagliate. Al centro della colonna il nome sta dentro se l'ancoraggio e' il centro e sconfina al piu' su una cella se e' l'angolo: leggibile in entrambi i casi. E' un altro punto che la calibrazione chiudera'.
- 11 candidati sono texture BASE del programma (cage_04, magic_circle_01, fountain_stone_01, skeleton_grave_02...) e non di un pack: Dungeondraft le disegna, ma un'anteprima esterna che legge solo i .dungeondraft_pack no. Lo script lo dice in fondo all'output, cosi' non sembrano rotte.

Il campionario e' alternativo al pacchetto commissionato, non in conflitto: serve a tirare fuori il meglio dai 440 object gia' disponibili mentre il pacchetto nuovo non c'e'.

SESTO GIRO: applicata la scelta di Jay sul campionario. Suite 745 passed, 1 skipped.

SCELTA RILETTA DAL CAMPIONARIO e applicata a assets._CITY_LANDMARK_SPRITES: 33 luoghi con lo sprite indicato da Jay, uno per riga. La rilettura e' avvenuta con lo script, non a mano: --read ha prodotto la tabella e l'ho incollata.

TRE ELEMENTI TOLTI su sua richiesta, e tolti da TUTTI i posti rilevanti, non solo dal campionario: cantiere navale, mercato del pesce (chiesto conferma: era una riga vuota non elencata fra le eccezioni, Jay ha confermato di toglierlo) e quartiere povero escono da generators/landmarks.py; la torre sulla porta delle mura esce da compose.draw_city_walls e con lei sparisce Palette.structure_sprites, che restava senza voci. Il varco nella cinta resta comunque un'apertura, ed e' ancora il punto a cui dogana e torre di guardia si agganciano.

CONSEGUENZA SU AC5, da segnalare: la AC nomina 'cantiere e faro sul porto'. Il cantiere non esiste piu', quindi sulla banchina resta il solo faro. La regola di piazzamento del porto continua a essere verificabile (test_the_lighthouse_stands_on_the_quay) ma copre un luogo invece di due.

DIFETTO TROVATO GENERANDO IL FOGLIO DELLE AREE, e corretto: 'dimensione nativa = dimensione reale' NON regge. I pack sono disegnati a scale incompatibili fra loro - tree1 di City Terrain e' nativo 0,3 quadretti perche' quel pack e' fatto per mappe di regione, mentre una chioma vera ne misura tre. Disegnati a dimensione nativa gli alberi di un parco venivano puntini. Nuovo campo LandmarkKind.piece_size: il lato lungo di un pezzo sparso in quadretti, dichiarato dal generatore (albero 3 q = 4,5 m, lapide e statua 1,5 q, banco e forca 2 q, tendone 3 q). E' il secondo giro su questa taratura: prima i pezzi erano scalati a una frazione dell'AREA e una lapide veniva alta sette metri, poi a dimensione nativa e diventavano puntini. Ora la dimensione e' una scelta esplicita, che e' l'unica che regge con pack di provenienza diversa.

Ritarato anche _SCATTER_SPACING da 3.0 a 1.2 guardando il foglio: a 3.0 un parco da 12x12 metri riceveva due alberi e sembrava un prato incolto.

NUOVO STRUMENTO: landmark_sprite_sheet.py --areas genera generated/aree.dungeondraft_map, sei varianti di giardino e cinque di cimitero, ognuna disegnata due volte (grande come al preset quartiere, piccola come al preset citta). Passa da compose.draw_landmark, quindi quel che si vede e' quel che le mappe produrranno davvero. Serve perche' un'area con sprite multipli e' una scena e non si giudica vedendo i pezzi in fila.

LIMITE NOTO del foglio delle aree: piece_size e' uno per luogo, quindi nella variante 'giardino E - con panchine e recinto' le panchine vengono disegnate grandi come alberi (4,5 m). Se Jay sceglie quella variante serve una dimensione per sprite e non per luogo - una riga in piu' nella tabella, ma solo se serve davvero.

DUE TEST RISCRITTI perche' la loro premessa era superata, non perche' fallivano per un bug:
- test_a_gravestone_is_the_same_size_in_a_big_and_a_small_cemetery pretendeva scala 1.0 (dimensione nativa); ora verifica che il LATO DISEGNATO sia esattamente piece_size, che e' l'invariante vero.
- test_requesting_an_element_does_not_reshuffle_the_rest confrontava la lista degli edifici, ma un luogo in piu' occupa per forza qualche lotto: il confronto giusto e' sulla rete stradale e sulle piazze, decise prima che i luoghi entrino in gioco.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-10 10:12
---
GATE UMANO (AC9) — cosa guardare in Dungeondraft, in ordine di rischio.

File pronti in generated/ (canvas 78x78, seed 1337):
- city_isolato_task48.dungeondraft_map — 23 edifici, 10 luoghi. Nessuna mura/porto (non ammissibili a questa scala). C'e' tempio, biblioteca, fornaio, macelleria, taverna, locanda, magazzino, mercato+patibolo sulla piazza, cimitero presso il tempio.
- city_quartiere_task48.dungeondraft_map — 143 edifici, 42 luoghi, mura con 4 porte, fiume con 6 ponti.
- city_citta_task48.dungeondraft_map — 2.745 edifici, 29 luoghi, mura, fiume con 19 ponti.
- city_porto_task48.dungeondraft_map — quartiere con --landmark porto/faro/cantiere: il seed 1337 non estrae il porto da solo, e senza questo file cantiere, faro e mercato del pesce non si vedrebbero affatto.

1. ETICHETTE (il punto piu' incerto). 'text.position' e' l'unico campo dello schema di docs/format.md 4 di cui non si conosce l'ancoraggio: un solo campione in tutto il progetto, e non si sa se il Vector2 sia il centro del testo, l'angolo in alto a sinistra o la baseline. Qui e' trattato come CENTRO dell'ingombro del luogo. Se le etichette risultassero spostate tutte nella stessa direzione, e' esattamente questo: dimmi in che direzione e di quanto e la correggo in una riga (piu' l'aggiornamento della nota in format.md, cosi' l'ancoraggio vero finisce finalmente scritto). Guarda anche se la dimensione del testo regge alle tre scale: e' calcolata dall'ingombro del luogo (12-44 px di font), non fissa.

2. PROPORZIONI, che sono il vero contenuto del task. Al preset isolato un edificio su tre e' un luogo con un nome (32%): e' voluto — la mappa e' una via sola, e una via ha le botteghe — ma e' la scelta su cui vale la pena il tuo parere. Al preset citta la quota e' l'1%: le 2.745 case restano case e si segnano solo le tre decine di luoghi che orientano. La domanda secca: al tavolo sono troppi o troppo pochi, e a quale scala?

3. GRANDEZZA DEI LUOGHI AL PRESET CITTA. Un isolato a quella scala vale 1,85-3,4 quadretti, quindi cattedrale, palazzo e arena (che occupano un isolato intero) risultano grandi come tre case. Si leggono come monumenti o si perdono nel tessuto? Se si perdono, la strada e' farli occupare piu' isolati adiacenti — e' un lavoro vero, non una riga.

4. DUE COSE CHE SO GIA' E CHE HO LASCIATO STARE, dimmi se ti danno fastidio: il fiume attraversa le mura senza un varco d'acqua (il muro gli passa sopra), e la via obliqua esce dalla citta' attraversando le mura senza una porta. Entrambe si sistemano allo stesso modo delle porte (spezzando l'anello), ma volevo un tuo riscontro prima di aggiungere altri buchi nel muro.

5. SPRITE DEI LUOGHI. Ogni luogo ha uno sprite dal catalogo scelto per somiglianza (tende da mercato per il mercato, tombe per il cimitero, torre per faro/torri di guardia, forgia per il fabbro, forno per il fornaio, gabbia per patibolo e prigione, bandiera per gilde e municipio). Dove non c'era niente di calzante non ho messo niente: un'icona che non c'entra confonde piu' del nome scritto. Se qualcuno stona, e' una voce del dizionario in assets.py.
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Le mappe cittadine hanno luoghi, non piu' solo edifici anonimi: quaranta elementi urbani notevoli piu' le tre strutture che li ancorano (mura con porte, fiume con ponti, porto), estratti dal seed o chiesti esplicitamente, con quantita' proporzionali alla mappa e regole di piazzamento verificabili.

DOVE STA L'IDEA. Un luogo non viene mai disegnato in uno spazio libero trovato a occhio: prende il posto di qualcosa che la partizione aveva gia' riservato (un lotto, un isolato, una porzione di piazza, una cella della fascia extramurale o della banchina). Cosi' la garanzia di TASK-35 'nessun edificio in mezzo alla strada' si estende gratis ai luoghi e AC6 e' un invariante di costruzione, non un controllo a posteriori. Allo stesso modo le strutture urbane vengono decise PRIMA di strade ed edifici e riducono l'area edificabile, cosi' 'dentro le mura' e 'sul mare' sono veri per costruzione.

E il contrario vale per le regole: un luogo la cui regola non trova un sito NON viene piazzato altrove, viene saltato. Su una mappa senza fiume non c'e' nessuna conceria. E' quella riga a rendere AC5 un invariante ('se e' sulla mappa, la regola vale') invece di una tendenza statistica.

SCORPORO VALUTATO E RESPINTO (la decisione che il task lasciava al piano): mura, fiume e porto restano qui, perche' senza di loro meta' di AC5 non sarebbe verificabile. Sono la precondizione delle regole, non un abbellimento separabile.

VERIFICA. Suite completa 733 passed, 1 skipped. Nuovo tests/test_city_landmarks.py (96 test, una sezione per AC): le regole di AC5 sono verificate con geometria scritta nel test e non richiamando city._rule_ok, e ogni test di regola fallisce se non ha incontrato nemmeno un luogo da verificare. AC7 misurata con scripts/city_landmarks_census.py su 30 seed x 3 preset, tabelle committate in docs/SPEC.md 9.4.1 (9,4 / 43,6 / 28,6 luoghi per mappa; 32% / 22% / 1% del totale). AC8 verificata anche nel caso peggiore: tutte le strutture insieme e tutti i luoghi ammissibili chiesti esplicitamente.

NON REGRESSIONE. Con --no-landmarks l'output e' byte-identico a prima del task: il golden file di TASK-46 non e' stato rigenerato e ora fa da garanzia che la rete stradale, gli isolati, i lotti e gli edifici approvati al gate M5 non si sono spostati di un pixel. Il documento completo ha un secondo golden.

TRE DIFETTI REALI TROVATI STRADA FACENDO, tutti corretti: riproducibilita' rotta fra processi (hash() di Python e' randomizzato per processo, sostituito con crc32 - lo ha trovato il test CLI, che gira in sottoprocesso); due regole di AC5 che non vincolavano nulla perche' si fidavano del tipo di sito (municipio/banca 'sulla piazza', monastero 'ai margini'); e nessun luogo largo piu' di una cella riusciva a stare sulla banchina, che e' una striscia di una colonna sola, quindi il porto restava senza cantiere navale.

AC9 (gate umano) RESTA APERTA: Jay deve aprire in Dungeondraft generated/city_isolato_task48, city_quartiere_task48, city_citta_task48 e city_porto_task48 (quest'ultimo con --landmark porto, perche' il seed 1337 non estrae il porto da solo) e confermare che i luoghi si riconoscono e le proporzioni reggono al tavolo. Da guardare in particolare: l'ancoraggio delle etichette 'text', l'unico campo dello schema di docs/format.md 4 di cui non si conosce la semantica (un solo campione in tutto il progetto) - draw_landmark lo tratta come centro dell'ingombro, e se le etichette risultassero spostate in modo sistematico la correzione e' una riga.
<!-- SECTION:FINAL_SUMMARY:END -->
