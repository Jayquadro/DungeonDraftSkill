---
id: TASK-42
title: >-
  Bug: Dungeondraft non apre i file generati con oggetti/luci (dungeon_m3,
  building_m4)
status: Done
assignee:
  - '@claude'
created_date: '2026-09-04 08:23'
updated_date: '2026-09-07 09:48'
labels: []
dependencies: []
priority: high
type: bug
ordinal: 42000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Jay riferisce che ne' `generated/dungeon_m3.dungeondraft_map` (gate M3, TASK-26) ne' `generated/building_m4.dungeondraft_map` (gate M4, TASK-30) si aprono in Dungeondraft 1.2.0.1, mentre `generated/demo_m1.dungeondraft_map` (TASK-12) si apre correttamente. Entrambi i file falliti passano `ddforge validate` senza errori, quindi il validatore non intercetta la causa.

Differenza minima fra il file che si apre e quelli che non si aprono: demo_m1 contiene solo 1 pattern, 4 muri e 1 portale, zero `objects` e zero `lights`; entrambi i file falliti contengono centinaia di `objects` e decine di `lights`, e building_m4 e' anche multi-livello (l'unica struttura mai osservata su file reali e' a livello singolo).

Serve la causa reale, non un'ipotesi: il fix va guidato da evidenza.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Individuata e documentata la causa reale per cui Dungeondraft 1.2.0.1 rifiuta/non carica generated/dungeon_m3.dungeondraft_map, con evidenza oggettiva (non ipotesi)
- [x] #2 Individuata la causa per generated/building_m4.dungeondraft_map (stessa causa o causa distinta, esplicitato quale)
- [x] #3 Il fix e applicato in src/ e coperto da test che fallirebbero senza il fix
- [x] #4 Rigenerati i file dei gate umani M3 e M4 e confermati da Jay come apribili in Dungeondraft
- [x] #5 docs/format.md aggiornato con i campi/valori verificati che erano divergenti dalle mappe reali
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. build.add_light: emettere SEMPRE `rotation` e `texture`; default texture = res://textures/lights/soft.png e colore/intensita' = quelli del Light2D.tscn interno di Dungeondraft (efc05c / 0.75), non piu' bianco arbitrario.
2. validate: nuovo codice DDF016 di severita' error per una luce senza `texture` (e' esattamente il difetto che manda DD in hang, e il validatore attuale non lo intercetta). Sganciare la regola sul formato colore dalla presenza di `texture`: m2 dimostra che 6 cifre + texture si apre.
3. Test che fallirebbero senza il fix: add_light emette texture/rotation; validate segnala DDF016; nessun file generato dalla CLI contiene luci senza texture.
4. Rigenerare il golden file di building (cambia: le luci ora hanno campi in piu').
5. Rigenerare i file dei gate M3 e M4 e farli confermare a Jay.
6. Correggere docs/format.md: la 'variante A' non e' la forma normale ma una forma che DD non riapre; le 82 luci che la documentavano vengono tutte da 4 mappe di Jay che non si aprono (2 gia' cancellate da lui).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Audit strutturale gia' eseguito (nessuna causa fatale trovata)

Confronto sistematico fra i file generati, i due template e le 11 mappe reali di Jay in `source/github/NovaMistralis` (che Dungeondraft apre senza problemi).

Verificato IDENTICO/CORRETTO — escluso come causa:
- chiavi di `header`, `world` e di ogni `level` (incluso i livelli extra di building_m4, cloni esatti del livello 0 del template)
- `world.format`/`msi`/`grid`/`embedded`/`next_prefab_id`
- `next_node_id` esadecimale: confermato su mappe reali (es. Carcere_Nova: 153 nodi, max id `99`=153, next `9a`=154)
- node_id globalmente univoci (770 e 317, zero duplicati)
- schema di `object` e `light`: set di chiavi identico a quello delle 176 objects e 82 lights reali
- tutte le texture referenziate esistono in mappe reali che Jay apre (nessun path inventato); dungeon_m3 non referenzia alcun pack
- geometria: zero muri di lunghezza nulla, zero muri con geometria duplicata, zero poligoni degeneri, tutti i pattern sono rettangoli a 4 punti CCW
- portali: ogni `wall_id` punta al muro che li contiene, nessun `(wall_id, wall_distance)` duplicato, nessuna porta che sborda dagli estremi del muro
- codifica: stesso writer, stesso UTF-8/CRLF di demo_m1 che si apre
- nessun `NaN`/`Infinity`/notazione esponenziale nel JSON (che romperebbero il parser JSON di Godot)

## Scostamenti REALI trovati rispetto alle mappe di Jay (nessuno dimostrato fatale)

1. `portal.point_index` — 121/121 portali reali ce l'hanno, i nostri 29 no. NOTA: anche demo_m1 non ce l'ha e si apre, quindi da solo non basta a spiegare.
2. `wall.joint` — 297/297 muri reali usano `1`, noi `0`. Anche demo_m1 usa 0 e si apre.
3. `pattern.layer` — i pattern reali usano `100`, noi `-400`. Anche demo_m1 usa -400 e si apre.
4. `object.rotation` — i valori reali stanno in [-pi, pi], i nostri arrivano a 2pi.
5. Multi-livello: nessuna delle 11 mappe reali ha piu' di un livello. La struttura a 2-3 livelli di building_m4 e' completamente non verificata contro un campione reale.

## Da Dungeondraft.pck (stringhe UTF-16 degli script)

Messaggi d'errore del loader rilevanti: `[Error] Duplicate level id`, `[Error] Invalid level order`, `[Error] Wall <id> has an invalid portal.`, `[Warning] Identical Node ID of type ... detected`, `Erasing object with missing texture:`, `: Invalid JSON at `. Esiste una preferenza `mute_json_errors`, quindi un JSON malformato verrebbe segnalato con posizione.

Da `%AppData%\Roaming\Dungeondraft\config.ini`: `dungeon_m3` COMPARE in `recently_opened_maps` (in prima posizione), `building_m4` NO. Possibile indizio che dungeon_m3 arrivi piu' avanti nel caricamento rispetto a building_m4.

## Prossimo passo: bisezione con Jay

Generati 5 file diagnostici in `generated/diag/` (non committati) per isolare la causa in un solo giro:
- `diag_a_senza_oggetti` — dungeon_m3 senza i 667 objects
- `diag_b_senza_luci` — dungeon_m3 senza le 10 lights
- `diag_c_solo_muri` — dungeon_m3 senza objects ne' lights
- `diag_d_conformato` — dungeon_m3 completo ma con `point_index: 0`, `joint: 1`, `pattern.layer: 100`
- `diag_e_building_1piano` — building_m4 ridotto al solo livello 0

## Bisezione 1 — risultato di Jay (2026-09-04)

- `diag_c_solo_muri` (niente objects ne' lights) -> **si apre**
- `diag_b_senza_luci` (667 objects, niente lights) -> **si apre**
- `diag_a_senza_oggetti` (10 lights, niente objects) -> **NON si apre**
- `diag_d_conformato` (completo + point_index/joint/layer conformati) -> **NON si apre**
- `diag_e_building_1piano` (building_m4 a un solo livello) -> **NON si apre**

**Causa isolata: le `lights`.** Sono necessarie e sufficienti a riprodurre il problema; gli `objects` sono innocenti, e il multi-livello NON e' la causa di building_m4 (anche a un piano solo si blocca, e anche building_m4 ha luci).

Sintomo preciso riferito da Jay: **Dungeondraft resta in caricamento** (hang), non da' errore e non crasha. Questo esclude un JSON malformato: il parser non arriva mai a lamentarsi, il blocco e' successivo, nella costruzione della scena.

I tre scostamenti cosmetici trovati prima (`point_index`, `joint`, `pattern.layer`) sono **esclusi**: `diag_d` li conformava tutti e si blocca lo stesso. Restano difetti minori da sistemare a parte, non la causa.

## Ipotesi gia' escluse per confronto con le mappe reali di Jay

Tutte queste sono presenti in mappe reali che DD apre senza problemi, quindi nessuna e' la causa:
- luci sovrapposte esattamente a un muro: `Carcere_Nova_Mistralis_PianoTerra` ne ha 8 su 21 e si apre
- muri collineari sovrapposti insieme alle luci: la stessa mappa ne ha 13 coppie (fino a 3584 px) e si apre
- numero di luci: `Carcere_Nova` ne ha 20, `PianoTerra` 21 (noi 10) e si aprono
- `range`/`intensity`/`shadows`: i nostri valori (3.0 / 0.7 / true) compaiono identici fra le 82 luci reali
- schema del dizionario `light`: set di chiavi identico alle 82 luci reali (niente `rotation`/`texture`)
- posizioni fuori mappa o duplicate: nessuna

## Differenze residue delle nostre luci rispetto a ogni campione reale

1. `color: "ffffff"` — stesso formato a 6 cifre, ma le 8 tinte reali osservate non sono mai bianco puro
2. dimensione mappa: tutte le mappe reali CON luci sono <= 40x32; la nostra e' 80x80. `rich_reference` e' 80x80 ma ha 1 sola luce, ed e' della variante B (con `texture`)
3. `environment.ambient_light: "ffffffff"` (bianco pieno, ereditato dal template vuoto); le mappe reali con luci hanno ambient scuro (`ff333333`, `ff505048`)

## Bisezione 2 — file generati per Jay (in generated/diag/)

Tutti derivati da `diag_a` (che si blocca), variando una cosa sola:
- `diag_l1_una_luce` — 1 sola luce invece di 10
- `diag_l2_senza_ombre` — 10 luci con `shadows: false`
- `diag_l3_valori_reali` — 10 luci con colore/range/intensity copiati da una luce reale
- `diag_l4_luci_senza_muri` — 10 luci, zero muri (isola l'interazione luce-occlusore)
- `diag_l5_ambient_scuro` — 10 luci con `ambient_light: ff333333`

## Bisezione 2 — risultato di Jay: NESSUNO dei 5 file si apre

`diag_l1` (1 sola luce), `diag_l2` (shadows:false), `diag_l3` (colore/range/intensity copiati da una luce reale), `diag_l4` (10 luci, ZERO muri), `diag_l5` (ambient scuro) -> tutti in hang.

Conseguenze dirette:
- **una sola luce basta** a bloccare il caricamento
- **non e' l'interazione luce-muro** (l4 non ha muri)
- **non sono le ombre** (l2 le disattiva)
- **non sono i valori** (l3 usa valori copiati verbatim da una luce reale di Jay)
- **non e' l'ambient bianco** del template (l5 lo scurisce)

Verificato inoltre che `templates/blank_80x80` e `templates/rich_reference` hanno base IDENTICA per `environment`, `layers`, `shapes`, `tiles`, `cave`, `terrain` (rich ha in piu' solo `water.tree` e `materials`). Quindi non e' il template vuoto: `rich_reference` e' 80x80, ha una luce, e Jay lo apre.

## Unica differenza rimasta

La luce di `rich_reference` (variante B) ha `rotation` e `texture`; le nostre (variante A) no. Le 82 luci reali di variante A stanno tutte su mappe <= 40x32, mai su una 80x80.

Ipotesi da verificare: su questa build, una luce **senza `texture`** manda DD in loop, e i campioni di variante A funzionano solo perche' sono su mappe piccole — oppure la variante A e' proprio incompleta per il loader di questa build.

## Bisezione 3 — file per Jay (generated/diag/)

- `diag_m1_vuoto_1luce_nostra` — blank_80x80 + 1 luce nel formato attuale (repro minimo)
- `diag_m2_vuoto_1luce_texture` — blank_80x80 + 1 luce con `rotation: 0` e `texture: res://textures/lights/fragments.png`
- `diag_m3_rich_piu_luce_nostra` — base rich_reference + 1 nostra luce senza texture

Controllo indispensabile: far aprire a Jay anche `NovaMistralis/Mappe/Carcere_Nova.dungeondraft_map` (40x32, 20 luci di variante A, creata da Dungeondraft stesso). Se si blocca pure quella, il problema non e' nei nostri file ma nello stato di Dungeondraft/asset pack di Jay.

## CAUSA TROVATA (bisezione 3, confermata da Jay)

- `diag_m1_vuoto_1luce_nostra` (template vuoto + 1 luce senza `texture`) -> **NON si apre**
- `diag_m2_vuoto_1luce_texture` (identico, ma con `rotation: 0` e `texture: res://textures/lights/fragments.png`) -> **si apre**

**Una `light` priva del campo `texture` manda Dungeondraft 1.2.0.1 in loop infinito al caricamento.** Non e' un errore di parsing (nessun messaggio, nessun crash): il JSON viene letto, il blocco e' nella costruzione della scena. Basta una sola luce; oggetti, muri, ombre, colori, ambient e multi-livello sono tutti irrilevanti.

## La documentazione di TASK-3 era derivata da file rotti

docs/format.md §4 dichiarava la 'variante A' (senza `rotation`/`texture`) come forma normale, sulla base di **82 campioni** presi da 4 mappe di Jay. Quelle 82 luci vengono tutte e sole da: Carcere_Nova (20), Carcere_Nova_2 (20), Carcere_Nova_Mistralis_PianoTerra (21), ProvaMappa (21). Jay ha confermato che **Carcere_Nova e Carcere_Nova_2 non si aprono** e li ha cancellati. Le altre due sono quasi certamente rotte allo stesso modo e **non vanno piu' usate come evidenza**.

L'unico campione di luce che si apre davvero e' quello di `templates/rich_reference.dungeondraft_map` (la 'variante B'), scritto da Dungeondraft 1.2.0.1: ha `rotation` e `texture`.

## Default reale della luce, dagli asset interni di Dungeondraft

Estratto `Light2D.tscn` da `Dungeondraft.pck`:

```
[ext_resource path="res://textures/lights/soft.png" type="Texture" id=1]
[node name="Light2D" type="Light2D"]
texture = ExtResource( 1 )
texture_scale = 0.75
color = Color( 0.937255, 0.752941, 0.360784, 1 )   # = efc05c
energy = 0.75
```

Le uniche tre texture di luce esistenti sono `soft.png`, `point.png`, `fragments.png`. `soft.png` e' il default del programma; `fragments.png` (usato in rich_reference e in diag_m2) e' una variante decorativa.

## Fix applicato

- `build.add_light` emette sempre `rotation` e `texture`. Nuove costanti `LIGHT_TEXTURE` (`res://textures/lights/soft.png`) e `LIGHT_COLOR` (`efc05c`), con `intensity` 0.75: sono i default del `Light2D.tscn` interno di Dungeondraft, non piu' il bianco `ffffff`/0.7 scelto arbitrariamente da TASK-10.
- `validate`: nuovo **DDF016** (errore) su ogni luce priva di `texture`. Verificato che scatta 10 volte su `diag_a` (il file che si bloccava) e zero volte sui file rigenerati.
- `_check_rgb6_color` -> `_check_light_color`: accetta 6 cifre RGB o 8 cifre ARGB. La regola precedente legava il formato del colore alla presenza di `texture` sulla base di un solo campione; `diag_m2` la smentisce (si apre con 6 cifre + texture).

## Test

Nuovi test che fallirebbero senza il fix:
- `test_build.py::test_add_light_always_emits_rotation_and_texture`
- `test_validate.py::test_light_without_texture_is_an_error`
- `test_validate.py::test_light_color_accepted_both_as_rgb6_and_argb8`
- `test_cli_generate.py::test_generated_lights_always_have_a_texture`
- `test_cli_generate_building.py::test_generated_building_lights_always_have_a_texture`

Gli ultimi due sono al livello a cui il bug era sfuggito: nessun test guardava dentro le luci prodotte dalla CLI, solo il loro numero.

Aggiornati 3 test preesistenti che codificavano l'assunzione sbagliata (`test_add_light_default_variant_has_no_rotation_or_texture` e le due fixture di validate senza `texture`).

Rigenerato il golden file `building_tavern_seed_1337.json`: verificato che il diff e' **solo** nelle luci, tutto il resto identico.

Suite completa: **307 passati**.

## File dei gate rigenerati

`generated/dungeon_m3.dungeondraft_map` (10 luci) e `generated/building_m4.dungeondraft_map` (6 luci su 2 piani), entrambi con 0 errori di validazione e zero luci senza texture. Restano i soli avvisi DDF102 gia' noti e documentati.

## Aggiornata la documentazione

`docs/format.md` §4 riscritta: la sezione dichiarava la variante senza `texture` come forma normale sulla base di 82 campioni presi da file che non si aprono. Ora documenta che `texture` e' obbligatoria, da dove vengono i default reali, e perche' quei campioni non vanno piu' usati come evidenza. `docs/SPEC.md` §: aggiunta la riga DDF016 alla tabella dei codici.

AC4 verificata indirettamente: sia la chiusura di TASK-26 (gate M3, 2026-09-04) sia quella di TASK-30 (gate M4, 2026-09-07) sono avvenute con Jay che apriva e usava dungeon_m3.dungeondraft_map/building_m4.dungeondraft_map DOPO il fix delle luci (commit 41e7ce7 e' antenato di entrambi i commit di chiusura, verificato con `git merge-base --is-ancestor`). Jay ha confermato esplicitamente entrambe le mappe utilizzabili (TASK-26: 'utilizzabile al tavolo senza ritocchi manuali di struttura'; TASK-30: approvazione dopo 3 round di gate, con modifiche a mano dentro il file). Nessuna delle due sarebbe stata possibile se il loop di caricamento fosse ancora presente, quindi l'evidenza soddisfa AC4 senza bisogno di un nuovo giro di conferma dedicato.

Conferma diretta di Jay ricevuta nel corso della finalizzazione: 'i file di m3 e m4 come sono generati attualmente vengono aperti correttamente'. Suite completa rieseguita prima della chiusura: 332 passati, 1 skip, nessuna regressione.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Causa trovata e corretta: una `light` priva del campo `texture` manda Dungeondraft 1.2.0.1 in loop infinito al caricamento (nessun errore, nessun crash — il blocco e' nella costruzione della scena, non nel parsing JSON). Isolata per bisezione con Jay in 3 round su file diagnostici in `generated/diag/`: bastava una sola luce senza texture, indipendentemente da oggetti, muri, ombre, colori, ambient o multi-livello.

La documentazione precedente (docs/format.md §4, da TASK-3) descriveva la variante senza `texture` come forma normale sulla base di 82 campioni presi da 4 mappe di Jay; due di quelle mappe (Carcere_Nova, Carcere_Nova_2) sono risultate anch'esse non apribili e sono state cancellate da Jay. L'unico campione affidabile (`templates/rich_reference`, scritto da Dungeondraft stesso) aveva sempre `rotation`+`texture`.

Fix:
- `build.add_light` emette sempre `rotation` e `texture`, coi default reali estratti da `Light2D.tscn` interno di Dungeondraft (`res://textures/lights/soft.png`, colore `efc05c`, intensity 0.75) al posto del bianco arbitrario precedente.
- Nuovo codice di validazione **DDF016** (errore) su ogni luce priva di `texture`.
- `_check_rgb6_color` generalizzato a `_check_light_color`: accetta sia RGB a 6 cifre sia ARGB a 8, sganciato dalla presenza di `texture`.

Test: 5 nuovi test che fallirebbero senza il fix (build, validate x2, cli_generate, cli_generate_building), 3 test preesistenti aggiornati perche' codificavano l'assunzione sbagliata. Golden file `building_tavern_seed_1337.json` rigenerato (diff solo nelle luci). Suite completa: 332 passati, 1 skip.

Verifica AC4 (Jay apre i file rigenerati): confermato sia per via indiretta (le chiusure di TASK-26 e TASK-30, entrambe discendenti del commit del fix, includono Jay che apre e usa dungeon_m3.dungeondraft_map e building_m4.dungeondraft_map) sia per conferma diretta di Jay durante la finalizzazione di questo task.

docs/format.md §4 riscritto (texture obbligatoria, provenienza dei default reali, perche' i vecchi campioni non sono piu' evidenza valida); docs/SPEC.md aggiornato con la riga DDF016.
<!-- SECTION:FINAL_SUMMARY:END -->
