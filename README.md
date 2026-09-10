# Dungeondraft Forge (`ddforge`)

Generatore procedurale di mappe `.dungeondraft_map` per Dungeondraft.

Lo stato del progetto e la specifica completa sono in [docs/SPEC.md](docs/SPEC.md).
Il lavoro e tracciato in Backlog.md sotto `backlog/` (milestone M0-M7).

## Stato

Repository in fase di bootstrap (M0). I moduli sotto `src/ddforge/` sono
ancora stub: consultare `docs/SPEC.md` per l'architettura e il piano delle
milestone.

## Installazione (sviluppo)

```bash
pip install -e ".[dev]"
```

## Uso

```bash
ddforge --help
```

I sottocomandi (`generate`, `validate`, `inspect`, `catalog`, `preview`)
sono documentati in `docs/SPEC.md` §8 e vengono implementati milestone per
milestone.

### Mappe cittadine: i tre preset di scala

`ddforge generate city` ha un parametro `--scale` con tre preset, perche un
isolato giocabile al tavolo, un quartiere intero e una citta capace di
contenerne una decina non stanno alla stessa scala
(`backlog/decisions/decision-2`, rivista da Jay al round 2 del gate umano).
Il default e `isolato`.

Misure su un canvas 78×78 (`templates/blank_80x80.dungeondraft_map`, seed
1337; il template di riferimento pesa 1,68 MB senza nulla disegnato sopra):

| | `--scale isolato` (default) | `--scale quartiere` | `--scale citta` |
|---|---|---|---|
| Un quadretto vale | 5 ft / 1,5 m | circa un edificio | circa un edificio, ma di un quartiere fra una decina |
| Edifici sul canvas | 30 | 322 | 3.325 |
| Ingombro medio di un edificio | 4,7×5,2 quadretti (~55 m²) | 2,5×2,4 quadretti (~13 m²) | 0,7×0,7 quadretti (~1 m²) |
| Cos'e un edificio | pianta completa: muri portanti, tramezzi, stanze, porte, tetto (riusa `generators/building.py`, con tipologie diverse per lotto) | uno sprite `object` del pack "BB 51 Assets Houses1" (BluBerrey, 33 varianti), scalato per riempire il lotto e con una tinta (`custom_color`) variata fra 6 toni — non piu un ingombro astratto | come `quartiere`, a scala ridotta |
| Dimensione del file | 1,87 MB (~6,4 KB/edificio) | 1,92 MB (~768 B/edificio) | 3,71 MB (~613 B/edificio) |
| A cosa serve | far muovere le miniature dentro e fuori dagli edifici di una via | inquadrare un quartiere esteso, decidere dove si va | orientarsi in una citta intera; non e pensata per essere giocata al tavolo |

Solo il preset `isolato` produce una geometria giocabile al tavolo (muri,
stanze, porte a scala 5 ft). `quartiere` e `citta` sono mappe di citta viste
dall'alto — uno sfondo/riferimento visivo, non un layout tattico — ed e per
questo che dal TASK-46 i loro edifici sono sprite del pack scelto da Jay
invece della geometria di `generators/building.py` (vedi `docs/format.md`
§10.2 per la provenienza del pack e il calcolo della scala di piazzamento).

I tempi di apertura in Dungeondraft per i tre preset non sono ancora stati
misurati: solo Jay puo darli, aprendo i file a mano.

Strade, isolati, lotti con fronte strada e piazze ci sono in tutti e tre:
cambia solo la taratura geometrica (`SCALE_PRESETS` in
`generators/city.py`) e la rappresentazione degli edifici.

In tutti e tre i preset la rete stradale non e una griglia: la centro-linea
di ogni via serpeggia dentro l'ingombro che le e riservato, e una via
obliqua attraversa la mappa da un bordo all'altro togliendo gli edifici che
incontra. Gli isolati profondi ricevono due file di lotti schiena contro
schiena, con il cortile in mezzo, cosi le case si affacciano su entrambe le
vie che bordano l'isolato.

**Come scegliere.** Se la scena si gioca *dentro* gli edifici, serve
`isolato`: agli altri due preset un edificio e largo meno di un quadretto e
non ci sta una stanza. Se serve un quartiere intero visto dall'alto, serve
`quartiere`. Se serve un'intera citta o una vista d'insieme di piu quartieri,
serve `citta`: alla scala `quartiere` gli stessi 3.325 edifici
richiederebbero un canvas di circa 285×285 quadretti, mentre l'unico
template di produzione e 80×80 e `ddforge` non cambia mai le dimensioni del
canvas del template.

```bash
# un isolato, giocabile al tavolo
ddforge generate city --template templates/blank_80x80.dungeondraft_map \
    --out isolato.dungeondraft_map --width 78 --height 78 --seed 1337

# un quartiere intero visto dall'alto
ddforge generate city --template templates/blank_80x80.dungeondraft_map \
    --out quartiere.dungeondraft_map --width 78 --height 78 --seed 1337 --scale quartiere

# una citta intera, per orientarsi
ddforge generate city --template templates/blank_80x80.dungeondraft_map \
    --out citta.dungeondraft_map --width 78 --height 78 --seed 1337 --scale citta
```

## Test

```bash
pytest -q
```

## Esportare un nuovo template

Documentazione da completare in TASK-39, quando il formato e le procedure
di calibrazione saranno confermate nei gate umani di M1 e M3.
