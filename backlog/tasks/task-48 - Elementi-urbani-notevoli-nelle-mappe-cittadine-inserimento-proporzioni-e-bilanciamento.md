---
id: TASK-48
title: >-
  Elementi urbani notevoli nelle mappe cittadine: inserimento, proporzioni e
  bilanciamento
status: To Do
assignee: []
created_date: '2026-09-09 08:36'
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
- [ ] #1 Un parametro della CLI permette di chiedere esplicitamente uno o piu elementi urbani per la mappa generata
- [ ] #2 Senza richiesta esplicita gli elementi vengono estratti a sorte in modo riproducibile dal seed, e due seed diversi danno citta con luoghi diversi
- [ ] #3 Ogni elemento dichiara a quali preset di scala e ammissibile, e un elemento non ammissibile per il preset scelto non viene mai piazzato
- [ ] #4 Le quantita sono proporzionali alla dimensione della mappa e non a numeri assoluti: gli elementi unici (palazzo del signore, cattedrale, arena) compaiono al piu una volta, quelli comuni (taverne, botteghe) crescono col numero di edifici
- [ ] #5 Gli elementi con una regola di piazzamento la rispettano in modo verificabile: almeno dogana alle porte, mulino e conceria sul fiume con la conceria a valle, cimitero fuori le mura o presso il tempio, mercato e patibolo sulla piazza, cantiere e faro sul porto
- [ ] #6 Gli elementi non si sovrappongono fra loro ne a strade, piazze o edifici esistenti
- [ ] #7 Le proporzioni risultanti sono misurate e documentate su piu seed e per ciascun preset, non solo affermate
- [ ] #8 Il documento generato passa validate() senza errori in tutti i preset e con e senza elementi richiesti
- [ ] #9 Jay apre in Dungeondraft una mappa per preset e conferma che i luoghi si riconoscono e le proporzioni reggono al tavolo
<!-- AC:END -->
