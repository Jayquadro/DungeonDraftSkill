# Assemblaggio del pack Dungeondraft (TASK-51)

I PNG prodotti da `scripts/prepare_sprites.py` (TASK-50,
`docs/sprite-postprocessing.md`) sono file sciolti in `assets/sprites/`:
Dungeondraft non li vede finché non stanno in un pack con i suoi metadati.
Questa procedura li mette nella struttura che il **packer ufficiale** di
Dungeondraft si aspetta in input.

## Comando

```bash
python scripts/build_pack.py                              # assets/sprites/ -> dist/NovaMistralisCitta/
python scripts/build_pack.py --input X --output Y
python scripts/build_pack.py --name "..." --author "..." --version "2.0"
```

Un solo passaggio: legge ogni PNG che ha una voce nel manifest di TASK-50
(`src/ddforge/sprite_prep/manifest.py` — lo stesso usato per generarli), lo
copia nella struttura del pack sotto `--output` e scrive `pack.json` e
`preview.png`. Richiede `pip install -e ".[sprites]"` (Pillow).

Il comando esce con codice diverso da zero se manca in `--input` un PNG che
il manifest si aspetta — non elabora a caso e non finge un pack completo se
uno sprite non è stato ancora generato da `prepare_sprites.py`.

## Struttura prodotta

```
dist/NovaMistralisCitta/
  pack.json
  preview.png
  textures/objects/nm_ospedale.png, nm_teatro.png, ...
  textures/terrain/          (vuota oggi: nessuna texture di terreno nel manifest)
  textures/patterns/normal/  (vuota oggi, stesso motivo)
```

`textures/terrain/` e `textures/patterns/normal/` esistono già nella
struttura anche se oggi non contengono nulla: il manifest di TASK-50 elenca
solo sprite di categoria C1–C4 (edifici e pezzi sparsi), nessuna texture C7
(erba, terra, selciato, ghiaia — proposte in `docs/prompt-sprite-pack.md` ma
mai commissionate). Quando arriverà una voce di terreno nel manifest, andrà
copiata in entrambe le cartelle (compatibilità con la struttura chiesta a
chi disegna in `docs/prompt-sprite-pack.md`), anche se
`docs/sprite-luoghi.md` §6 nota che Dungeondraft accetta una texture
`terrain` anche dentro un `pattern` senza bisogno della doppia copia.

`dist/` è nel `.gitignore` del repository (build artifact, si rigenera in un
comando da `assets/sprites/` già versionato): non serve versionarla.

## `pack.json`

Schema verificato sugli `asset_manifest` di `.dungeondraft_map` reali
(`docs/SPEC.md` §13, `tests/fixtures/*.dungeondraft_map`) — `pack.json`
duplica quella stessa voce (`docs/format.md` §10.2):

```json
{
  "name": "Nova Mistralis Città",
  "id": "d0HrfqNR",
  "version": "1.0",
  "author": "Jay",
  "keywords": null,
  "allow_3rd_party_mapping_software_to_read": false,
  "custom_color_overrides": {
    "enabled": false,
    "min_redness": 0.1,
    "min_saturation": 0.0,
    "red_tolerance": 0.04
  }
}
```

`name`/`author`/`version` vengono da `src/ddforge/pack_build/settings.py`
(default identici a `sprite-batch.zip/catalogo.yaml`, sovrascrivibili da
riga di comando).

`custom_color_overrides.enabled` è `false` (TASK-53): il pack **non offre**
il canale "custom color" di Dungeondraft. Non è la scelta di partenza — vedi
`docs/sprite-postprocessing.md` per la storia (due giri di normalizzazione
del rosso dei tetti insufficienti a renderlo affidabile) — ma quella finale,
decisa da Jay dopo che il rischio residuo di ricolorare un po' di legno
insieme al tetto si è rivelato non chiudibile lato immagine. I tre numeri
restano nel JSON solo perché i pack reali osservati
(`tests/fixtures/*.dungeondraft_map`) portano sempre questi tre campi anche
quando `enabled` è `false`: con `enabled: false` Dungeondraft non li usa per
ricolorare nulla, quindi il loro valore è indifferente.

### L'id resta stabile

`id` non è generato a ogni riassemblata: la prima volta viene creato (8
caratteri alfanumerici, come gli id reali osservati nei pack di Jay — es.
`6VxwaRdj`, `Hk3gdwPN`) e salvato in `--id-file` (default `data/pack_id.txt`,
**tracciato in git**, non nella `dist/` ignorata). Le riassemblate successive
lo rileggono da lì. Questo è ciò che fa restare stabile l'id anche se `dist/`
viene ripulita fra una riassemblata e l'altra (AC2): un id che cambiasse ad
ogni comando farebbe comparire in Dungeondraft un pack nuovo invece di
aggiornare quello già importato da Jay.

## Dal pacchetto al `.dungeondraft_pack`

Il file `.dungeondraft_pack` finale (quello che compare nel menu dei pack di
Dungeondraft) lo produce il **packer ufficiale del programma**, non questo
repository: `assets.read_dungeondraft_pack` (TASK-46) sa solo *leggere* un
pack già impacchettato, non crearne uno.

Il flusso, per come Dungeondraft gestisce i contenuti custom (comportamento
documentato dal programma stesso — **non verificato su questo repository**,
va confermato sulla macchina di Jay, è il gate umano AC6):

1. Copiare la cartella prodotta (`dist/NovaMistralisCitta/`) dentro
   `Documents/Dungeondraft/unpacked_assets/`, così com'è (stesso nome di
   cartella, `pack.json` alla radice).
2. Avviare Dungeondraft: il pack compare come contenuto custom "non
   impacchettato" e Dungeondraft lo può già usare così, senza altro passo —
   utile per verificare gli sprite prima di generare il `.dungeondraft_pack`.
3. Dal pannello dei contenuti custom del programma c'è un'azione per
   compilare il pack in un `.dungeondraft_pack`, che finisce in
   `Documents/Dungeondraft/packs/`. Da lì si importa nel menu dei pack come
   qualunque altro pack scaricato.

**Se il packer non è disponibile o fallisce**: il passo 2 sopra (cartella
"non impacchettata" in `unpacked_assets/`) è comunque sufficiente per Jay per
verificare gli sprite in gioco (AC6) anche senza un `.dungeondraft_pack`
vero e proprio — Dungeondraft legge il contenuto custom non impacchettato
allo stesso modo. Il `.dungeondraft_pack` compilato serve solo per
condividere il pack come singolo file.
