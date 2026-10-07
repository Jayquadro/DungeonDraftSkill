---
id: doc-1
title: Censimento asset e tabelle dei sei temi di abbellimento (TASK-68)
type: specification
created_date: '2026-10-06 15:12'
updated_date: '2026-10-07 06:08'
---
# Censimento asset e tabelle dei sei temi di abbellimento (TASK-68)

Stato: **confermato da Jay** (chat, 2026-10-07): il censimento e sufficiente,
nessun asset mancante da decidere voce per voce (AC2 chiuso).

## Metodo

Il catalogo `data/assets.json` prima di questo task conteneva solo gli
oggetti effettivamente *piazzati* nei due template di riferimento (573
oggetti): non la libreria intera dei 52 pack referenziati nel manifest. Per
un censimento vero ho letto direttamente i 52 file `.dungeondraft_pack` che
Jay possiede in `Documents/Dungeondraft/` (`assets.read_dungeondraft_pack`,
lo stesso meccanismo di TASK-46) — 21.086 texture in tutto — e cercato per
ciascuna delle categorie richieste dai sei temi (§6.2 dello SPEC) le
corrispondenze per nome file, pack per pack.

## Risultato: catalogo rigenerato

Tutti i 52 pack del censimento erano gia nel manifest di
`templates/blank_80x80.dungeondraft_map` (nessun pack nuovo aggiunto,
invariante di SPEC-decorate §1.3 rispettata). Ho rigenerato
`data/assets.json` con:

```
ddforge catalog \
  --from templates/blank_80x80.dungeondraft_map \
  --from templates/rich_reference.dungeondraft_map \
  --from-catalog data/assets.json \
  --pack <52 file .dungeondraft_pack, uno per pack unico> \
  --out data/assets.json
```

| | prima | dopo |
|---|---|---|
| file | 92 KB | 2,7 MB |
| `objects` | 573 | 12.741 |
| `floors` | 9 | 310 |
| `walls` | 9 | 114 |
| `terrain` | 10 | 216 |
| `portals` | 15 | 128 |
| `paths` | 9 | 468 |

Decisione di Jay (chat, 2026-10-06): importare tutto (non solo i pack
specializzati), perche' WFW 5th Anniversary Free Megapack (11.118 texture) e
[DQ] 2Y Anniversary Pack (2.630 texture) da soli coprono la grande
maggioranza delle categorie richieste. La suite di test completa (798 test)
resta verde dopo la rigenerazione.

## Censimento per tema

Per ciascuna categoria: se trovata, pack principali e un paio di alias
rappresentativi (non l'elenco completo — alcune categorie hanno decine o
centinaia di varianti, es. candele 105, cristalli 450+). Gli alias citati
sono le chiavi usate in `src/ddforge/decorate/themes.py`.

### Abbandonato / lugubre (macerie, ossa, ragnatele, candele, catene)

| Categoria | Trovato | Pack principali | Esempi di alias |
|---|---|---|---|
| Ragnatele | si (8) | WFW Megapack, Maelstrom Maps | `web_medium_01_a`, `web_small_01_a`, `web_large_01_a`, `web_spooky_01_a` |
| Macerie/rubble | si (63) | Lost Lands Castles, Skront's Rocks and Bricks, WFW Megapack | `rubble_01`, `stone_block_debris_pile_01_a`, `stone_block_debris_scatter_01_a` |
| Mobili rotti | si (149) | GF Colorable Furniture, Skront's Wooden Stuff, TygerBar, WFW Megapack | `broken_chair_01_ashen`, `broken_table_rectangle_01_ashen`, `tablebroken01` |
| Ossa/lapidi | si (77+75) | WFW Megapack, NovaMistralis (cimitero), template base (`grave_01..11`) | `bone_pile_01_a`, `bone_human_skull_01_a`, `grave_stone_broken_01_a` |
| Candele | si (105) | WFW Megapack, [DQ] 2Y Anniversary, Skront's Books | `candle_single_purple`, `candlestick_1_silver`, `dq_candle_white_07a` |
| Catene | si (35) | Skront's Treasure, WFW Megapack | `chain_pile_messy_01_a`, `ball_and_chain_01_a` |
| Sangue | si (39) | WFW Megapack, FA_Starter_Pack | `blood_stain_01_a`, `blood_puddle_colorable_a1_1x1` |

### Naturale (muschio, radici, funghi, alberi, carretti)

| Categoria | Trovato | Pack principali | Esempi di alias |
|---|---|---|---|
| Funghi | si (285) | GoGots-Mushroom (112 texture dedicate), GoGots-Forest, Expanded Nature, IC_Apothecary | `mushroom_small_a_02`, `forest_mushroom_colorable_05`, `giant_mushroom` |
| Radici | si (68) | GoGots-Forest/Forest Add, WFW Megapack | `forest_root_03`, `tree_roots_piece_01_a_ashen` |
| Muschio | si (68) | GoGots-Forest, WFW Megapack, WFW Sample Pack | `moss_01_a`, `forest_moss` |
| Alberi/cespugli | si (58+ nel catalogo base, migliaia nei pack) | template base, Expanded Nature, Crosshead's Ghibli, WFW Megapack | `oak_02`, `bush_green_simple_03`, `dead_tree_01` |
| Rocce | si | Skront's Rocks and Bricks, template base, WFW Megapack | `rock_04`, `sharp_boulder_01_a` |
| Carretti | si (30) | TygerWagons, Spacious Stable, [DQ] 2Y Anniversary, WFW Megapack | `wheelbarrow_1`, `handcart_01_a_ashen`, `dq_wheelbarrow_pine_03` |

### Arcano (banchi alchemici, alambicchi, cristalli, cerchi rituali, pergamene)

| Categoria | Trovato | Pack principali | Esempi di alias |
|---|---|---|---|
| Banchi alchemici | si (52) | DQ_Pack_Theme_27 Alchemy II, WFW Megapack, DEMO DnDungeon Whimsical | `dq_alchemy_ingredient_prefab_09`, `alchemy_table_a` |
| Alambicchi/calderoni | si (62) | DQ Arcane Laboratory, Skront's Alchemy / Mk2, WFW Megapack | `cauldron_filled_01_a`, `glass_beaker_01`, `vat_01` |
| Cristalli | si (450+) | DQ Arcane Laboratory (`crystal_throne`, `magical_orb_prefab_*`), [DQ] 2Y Anniversary, WFW Megapack | `dq_magical_orb_prefab_small_16`, `dq_crystal_throne_01_white` |
| Cerchi rituali | si (233, molti dalla stessa famiglia) | DQ Arcane Laboratory (`magical_circle_*`, `magical_glyph_gold_*`), WFW Megapack | `dq_magical_circle_advanced_red_01`, `dq_magical_glyph_gold_03` |
| Pergamene | si (52) | TygerLibrary (solo libri, niente scroll), Skront's Books, DEMO DnDungeon, WFW Megapack | `scroll_fancy_01_a`, `scroll_magic_01_a` |

Nota: TygerLibrary (51 texture) ha solo libri/scaffali, nessun rotolo — le
pergamene arrivano da Skront's Books e WFW Megapack, non da TygerLibrary.
Non e' un problema (il tema arcano non dipende da un solo pack), ma vale la
pena saperlo se in futuro si cerca "pergamena" dentro TygerLibrary.

### Festivo (tavolate, stendardi, fiori, bancarelle, strumenti musicali)

| Categoria | Trovato | Pack principali | Esempi di alias |
|---|---|---|---|
| Tavolate | si (indiretto: nessun asset "feast/banquet" letterale, ma tavoli + portate coprono il bisogno) | GW Inn tables and kitchens, TygerBar, WFW Megapack (`food_platter_*`, `*_roast_*`) | `gw_pub_table_1`, `food_platter_overlay_meats_oval_01_a` |
| Stendardi | si (93) | [DQ] 2Y Anniversary (`banner_*` in 9 colori), WFW Megapack, Unofficial Jonathan Roberts | `flag_blowing_01_a`, `tapestry_01_a`, `dq_banner_red_wall_02a` |
| Fiori | si (264) | template base, WFW Megapack, Benthic Botany | `bush_flower_02`, `tree_flower_01` |
| Bancarelle | si (33) | WFW Megapack, [DQ] 2Y Anniversary, NovaMistralis (`nm_stalle`) | `readymade_market_stall_01_a`, `dq_market_stall_pine_02` |
| Strumenti musicali | si (56) | TygerMusic (pack dedicato: tamburi, arpa, flauti, clavicembalo), WFW Megapack | `drum01`, `harp01`, `string_instrument_01_a` |

### Abitato (nessuna categoria nuova, solo arredo completo)

Gia ampiamente coperto dal catalogo pre-esistente (sedie, tavoli, letti,
librerie, tappeti) e dai pack GW Inn tables, 5 wood Furniture Pack, T23's
Royal Furniture, GF Colorable Furniture, Hooded Wood Table and Chair Pack.
Nessuna lacuna.

## Conclusione: nessun asset mancante

Per nessuna delle categorie elencate nello SPEC (§6.2, tabella "bozza di
carattere dei sei temi") ho trovato una lacuna reale: ogni voce ha almeno
una famiglia di texture dedicata in uno o piu pack gia nel manifest. Le due
"stranezze" degne di nota (non lacune):

1. **Tavolate**: nessun oggetto si chiama letteralmente "banchetto" o
   "tavola imbandita", ma tavoli (GW Inn, TygerBar) + portate (`*_roast_*`,
   `food_platter_*` di WFW Megapack) coprono lo stesso effetto visivo.
2. **TygerLibrary senza rotoli**: le pergamene del tema arcano vengono da
   Skront's Books e WFW Megapack, non da TygerLibrary (solo libri).

**Decisione di Jay** (chat, 2026-10-07): censimento confermato sufficiente,
nessuna voce da decidere caso per caso (AC2 chiuso). Se emergono lacune
reali una volta viste le mappe abbellite (TASK-74, gate umano), si apriranno
task figli mirati invece di bloccare TASK-69.

## `decorate/themes.py`

Le tabelle sono scritte in `src/ddforge/decorate/themes.py`: sei temi ×
cinque tipi di mappa (`dungeon`, `building`, `cave`, `sewer`, `city`), con
un ruolo `_default` per ogni combinazione (AC4). Verificato da
`tests/test_decorate_themes.py`:

- ogni chiave citata (floor/wall/terrain/oggetto) risolve su una texture di
  `data/assets.json` (AC5);
- ogni texture risolta appartiene a un pack del manifest del template di
  produzione (AC6);
- `ambient` e i colori delle luci sono ARGB a 8 cifre (AC7).

Nessuna nuova chiave semantica e stata necessaria in `OBJECT_ALIASES`
(AC3): le chiavi "raw" generate automaticamente dal nome file (es.
`web_medium_01_a`, `rubble_01`) bastano, perche' `themes.py` le referenzia
direttamente. Resta un miglioramento possibile per TASK-69/73: alias piu
leggibili (es. `ragnatela` invece di `web_medium_01_a`) per l'override
`--add zona:alias` della CLI — non necessario ora, solo piu comodo da
digitare.
