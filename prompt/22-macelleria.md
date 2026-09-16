# Sprite — Macelleria (`nm_macelleria.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce `house_01`, che è una casa
qualunque e non dice niente.

> **Nota sulla misura.** `macelleria` esiste come `LandmarkKind` solo al
> preset `isolato` (`src/ddforge/generators/landmarks.py`), dove
> `building.py` disegna l'edificio a stanze vero quando il lotto è abbastanza
> grande. Questo sprite serve da **ripiego** per il ~45% dei lotti troppo
> stretti (docs/sprite-luoghi.md sez. 7: "il ripiego è voluto"). Non esiste
> quindi una misura "disegnato a" su `quartiere`/`citta` come per le altre
> botteghe: la macelleria non compare a quelle scale. Canvas e categoria qui
> sotto seguono lo stesso trattamento delle botteghe ordinarie, per coerenza
> col resto del pacchetto.

| | |
|---|---|
| nome file | `nm_macelleria.png` |
| categoria | C3 — botteghe e servizi |
| canvas finale | 512 × 512 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **tetto ricolorabile**: i tetti in rosso mattone saturo, nient'altro di rosso |
| dove finisce | ripiego per i lotti stretti del preset `isolato`, quando l'edificio a stanze non ci sta |

Il **recinto per il bestiame** e l'**area lastricata di macellazione con
canale di scolo** sul retro sono il segno che la rende riconoscibile; va
distinta dal macello (`macello`), che è l'impianto su scala più grande, a
valle del fiume.

---

## Come usarlo

1. **Allega l'immagine di riferimento** (lo sprite-àncora già approvato dello
   stesso pacchetto).
2. Incolla il prompt qui sotto, tutto, in un messaggio solo.
3. Genera 2–3 candidati e scegli.
4. Per le varianti B e C: stesso prompt, sostituisci la sola riga `SUBJECT:`.

---

## Prompt — sprite canonico

```text
Asset for a hand-painted fantasy city battlemap, to be placed in Dungeondraft.

REFERENCE: the attached image is another asset from the same set. Match its brushwork, palette, lighting, texture grain and level of detail exactly, but draw a new, different subject as described below. Do not copy its content or its layout.

VIEW: strict orthographic plan view from directly above (90 degrees), like a satellite photo. Only roofs, courtyards and ground-level objects are visible. No facades, no walls seen from the side, no perspective, no isometric angle, no vanishing point.

ISOLATION: one single isolated subject, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. Include only the subject and the ground that strictly belongs to it, inside its own fence. No grass, sea, trees, hills, roads or neighbouring buildings around it. Do not crop the subject: leave a small empty margin on every side, and let the subject fill the rest of the frame.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no compass rose, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the subject itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: earthy natural tones: grey and ochre stone, brown wood, pale plaster, muted greens. No neon or acid colours.

ROOFS: paint every roof in a uniform, saturated brick red; this colour is a recolour channel. Nothing else in the image may be saturated red.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof tiles, stone, plaster, wood, paving) the same way every time.

SUBJECT: Butcher's shop: a small shopfront building with a fenced rear yard holding a livestock pen and a stone-paved slaughter area with a drainage channel leading to a gutter. Hooks and hanging racks under a lean-to roof at the back are where cuts of meat would be displayed.
```

## Variante B — macelleria con recinto laterale

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Butcher's shop with the livestock pen to one side of the building instead of behind it, a small covered slaughter area with a stone floor and drainage channel tucked into the corner between the shop and the pen fence.
```

## Variante C — macelleria con affumicatoio

```text
SUBJECT: Butcher's shop built around a narrow rear yard shared with a smokehouse with its own small chimney, livestock pen along the back fence, drainage channel running from the paved slaughter area to a street-side gutter.
```

---

## Dopo la generazione

- Scontorna il magenta e ripulisci la frangia colorata sul bordo alfa.
- Rifila, ricentra, margine trasparente del 5% per lato.
- Canvas a **512 × 512 px**.
- Ombra aggiunta in post: offset 4%, sfocatura 2,5%, opacità 45%, colore
  `(22, 16, 10)`, identica su tutto il pacchetto.
- Normalizza i tetti al rosso uniforme.
- Salva in **PNG con canale alfa**. Mai WebP.

## Checklist

- [ ] Recinto per il bestiame e area lastricata con canale di scolo: si vedono chiaramente
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Niente prato o strada intorno: solo la bottega e il suo recinto
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Tetto rosso saturo uniforme; nessun altro rosso saturo
- [ ] PNG con alfa, non WebP
