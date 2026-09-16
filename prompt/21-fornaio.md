# Sprite — Fornaio (`nm_fornaio.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce `house_10`, che è una casa
qualunque e non dice niente.

> **Nota sulla misura.** `fornaio` esiste come `LandmarkKind` solo al preset
> `isolato` (`src/ddforge/generators/landmarks.py`), dove `building.py`
> disegna l'edificio a stanze vero quando il lotto è abbastanza grande.
> Questo sprite serve da **ripiego** per il ~45% dei lotti troppo stretti
> (docs/sprite-luoghi.md sez. 7: "il ripiego è voluto"). Non esiste quindi
> una misura "disegnato a" su `quartiere`/`citta` come per le altre botteghe:
> il fornaio non compare a quelle scale. Canvas e categoria qui sotto seguono
> lo stesso trattamento delle botteghe ordinarie, per coerenza col resto del
> pacchetto.

| | |
|---|---|
| nome file | `nm_fornaio.png` |
| categoria | C3 — botteghe e servizi |
| canvas finale | 512 × 512 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **tetto ricolorabile**: i tetti in rosso mattone saturo, nient'altro di rosso |
| dove finisce | ripiego per i lotti stretti del preset `isolato`, quando l'edificio a stanze non ci sta |

Il **forno a legna con cupola e comignolo**, visibile dall'alto sul retro, e
l'**insegna appesa** sono il segno che lo rende riconoscibile.

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

ISOLATION: one single isolated subject, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. Include only the subject and the ground that strictly belongs to it. No grass, sea, trees, hills, roads or neighbouring buildings around it. Do not crop the subject: leave a small empty margin on every side, and let the subject fill the rest of the frame.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no compass rose, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the subject itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: earthy natural tones: grey and ochre stone, brown wood, pale plaster, muted greens. No neon or acid colours.

ROOFS: paint every roof in a uniform, saturated brick red; this colour is a recolour channel. Nothing else in the image may be saturated red.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof tiles, stone, plaster, wood, firewood) the same way every time.

SUBJECT: Bakery: a small shopfront with a wood-fired oven built into the rear wall, its low brick dome and chimney visible from above, and a small yard behind stacked with firewood. A wooden pole outside the door carries a hanging sign shaped like a pretzel or a sheaf of wheat.
```

## Variante B — fornaio con forno laterale

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Bakery with the oven dome and chimney set into a side wall instead of the back, a narrow yard beside it stacked with firewood and sacks of flour under a small lean-to roof, a shopfront window facing the street with loaves visible on a sill.
```

## Variante C — fornaio a doppio forno

```text
SUBJECT: Bakery built around a small rear courtyard shared by two wood-fired ovens with separate chimneys, firewood stacked along the courtyard wall, a covered passage connecting the courtyard to the shopfront.
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

- [ ] Forno con cupola e comignolo: si vede chiaramente dall'alto
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Niente prato o strada intorno: solo la bottega
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Tetto rosso saturo uniforme; nessun altro rosso saturo
- [ ] PNG con alfa, non WebP
