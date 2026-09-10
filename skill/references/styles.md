# Stili disponibili e quando usarli

Riferimento per tradurre una richiesta in linguaggio naturale nei parametri
di `ddforge generate`. Niente schema del formato e niente codice di
generazione: quelli stanno in `docs/format.md` e in `src/ddforge/`.

## Algoritmi (`ddforge generate <algoritmo>`)

| Algoritmo | Cosa produce | Quando usarlo |
|---|---|---|
| `dungeon` | stanze e corridoi da partizione BSP, con stanza boss, snodi tattici, corridoi bui e porte segrete | "un dungeon", "una cripta", "sotterranei di N stanze" |
| `building` | un edificio multi-piano con perimetro portante, tramezzi, vano scale e tetto | "una taverna", "una villa", "un magazzino" — un singolo edificio da esplorare |
| `cave` | grotta a contorni irregolari, scritta nel layer cave nativo di Dungeondraft | "una caverna", "una grotta naturale" |
| `sewer` | canali ortogonali, camere di giunzione circolari e acqua | "fognature", "cunicoli sotto la citta" |
| `city` | rete stradale, isolati, lotti con fronte strada, edifici e piazze | "un isolato", "un quartiere", "una citta" — vedi i tre preset di scala qui sotto |

## Palette (`--style`)

Sceglie le texture, non la geometria. Se non viene passata, vale l'algoritmo
stesso (o `--building-type` per `building`).

`dungeon`, `crypt`, `sewer`, `cave`, `tavern`, `manor`, `warehouse`, `city`.

Combinazioni utili: `dungeon --style crypt` (stesse stanze, muri e porte da
cripta), `cave --style cave`, `city --style city`.

## Tipologie di edificio (`--building-type`, solo `building`)

| Tipologia | Piani e ambienti | Ingombro di default |
|---|---|---|
| `tavern` | sala comune, cucina, retro + 3 camere al primo piano | 18×14 quadretti |
| `manor` | 2 sale di rappresentanza, 3 stanze private, 2 ambienti di servitu (3 piani) | 22×18 |
| `warehouse` | magazzino + soppalco | 22×14 |

`--l-shaped` da una pianta a L invece che rettangolare.

## Mappe cittadine: i tre preset di scala (`--scale`)

Un isolato giocabile al tavolo, un quartiere intero e una citta capace di
contenerne una decina non stanno alla stessa scala (decision-2, rivista da
Jay al round 2 del gate umano). Il default e `isolato`.

| | `--scale isolato` (default) | `--scale quartiere` | `--scale citta` |
|---|---|---|---|
| Un quadretto vale | 5 ft / 1,5 m | circa un edificio | circa un edificio, di un quartiere fra una decina |
| Edifici su un canvas 78×78 | ~30 | ~320 | ~3.300 |
| Ingombro di un edificio | ~4,7×5,2 quadretti (~55 m²) | ~2,5×2,4 quadretti | ~0,7×0,7 quadretti |
| Cos'e un edificio | pianta completa: muri, stanze, porte, tetto, con tipologie diverse per lotto | uno sprite `object` del pack "BB 51 Assets Houses1" (33 varianti), scalato dentro il lotto e tinto (`custom_color`) fra 6 toni | come `quartiere`, a scala ridotta |
| Isolati | 13–22 quadretti | 6–11 quadretti | 1,85–3,4 quadretti |

**Come scegliere.** Se la scena si gioca *dentro* gli edifici serve
`isolato`: agli altri due preset un edificio e largo meno di un quadretto e
non ci sta una stanza, quindi non ci si muove dentro. Se serve un quartiere
intero visto dall'alto serve `quartiere`. Se serve un'intera citta, o una
vista d'insieme di piu quartieri, serve `citta`: alla scala `quartiere` gli
stessi ~3.300 edifici richiederebbero un canvas di circa 285×285 quadretti,
e `ddforge` non cambia mai le dimensioni del canvas del template (l'unico
template di produzione e 80×80). `citta` non e pensata per essere giocata al
tavolo: e uno sfondo/riferimento visivo dall'alto.

Solo `isolato` produce una pianta giocabile (TASK-46): `quartiere` e `citta`
sono mappe viste dall'alto senza layout tattico, quindi i loro edifici sono
sprite pescati da un asset pack invece della geometria di
`generators/building.py` — non serve un ingresso, un arretramento o una
stanza per leggersi come casa su una mappa di citta.

In tutti e tre i preset le vie serpeggiano invece di essere rettilinee, e una
via obliqua attraversa la mappa da un bordo all'altro.

Strade, isolati, lotti con fronte strada e piazze ci sono in tutti e tre i
preset: cambia la taratura geometrica e la rappresentazione degli edifici.

## Arredo e luci

- `--furnish none|light|medium|heavy` (default `none`): circa 0,05 / 0,12 /
  0,25 oggetti per quadretto. Non si applica a `cave`, `sewer` e `city`, che
  non hanno stanze nel Blueprint principale.
- `--lights`: una luce al centro di ogni stanza e dei corridoi lunghi. Non
  si applica a `cave`, `sewer` e `city`, per lo stesso motivo.
