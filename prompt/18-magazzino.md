# Sprite — Magazzino (`nm_magazzino.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce `shed_01`, un capannone
generico senza dettagli.

| | |
|---|---|
| nome file | `nm_magazzino.png` |
| categoria | C3 — botteghe e servizi |
| canvas finale | 512 × 512 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **tetto ricolorabile**: i tetti in rosso mattone saturo, nient'altro di rosso |
| dove finisce | lotto urbano dei preset `quartiere` e `citta` |

Disegnato a ~2,4 × 2,4 quadretti al preset `quartiere`, ~0,7 × 0,7 al preset
`citta`. Presenza attesa ~4,65 per mappa `quartiere` (dato non misurato a
`citta`): è uno dei luoghi più comuni. Il **portone largo**, le **casse
accatastate** e l'**argano** sono il segno che lo rende riconoscibile.

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

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof tiles, stone, plaster, wood, crates and barrels) the same way every time.

SUBJECT: Warehouse: a large plain shed under a single long tiled roof, with a pair of wide double doors on one side and a wooden hoist crane projecting from the roofline above them. Crates and barrels are stacked in ordered rows against the outside wall, with a cart pulled up near the doors.
```

## Variante B — magazzino a doppio capannone

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Warehouse made of two parallel sheds separated by a narrow loading lane, wide doors facing the lane on both sides, a wooden hoist crane above one set of doors, barrels and sacks stacked along the lane.
```

## Variante C — magazzino con banchina coperta

```text
SUBJECT: Warehouse with a covered loading dock projecting from one long side, wide doors opening onto it, crates stacked under the dock roof and more piled in the open yard beside it, a wooden hoist crane at the corner.
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

- [ ] Portone largo, casse accatastate e argano: si vedono chiaramente
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Niente prato o strada intorno: solo l'edificio
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Tetto rosso saturo uniforme; nessun altro rosso saturo
- [ ] PNG con alfa, non WebP
