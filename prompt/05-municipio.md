# Sprite — Municipio (`nm_municipio.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce `bb_houses1_flag1`, che è
una casa qualunque con una bandiera sopra.

| | |
|---|---|
| nome file | `nm_municipio.png` |
| categoria | C2 — edifici pubblici medi |
| canvas finale | 768 × 768 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **tetto ricolorabile**: i tetti in rosso mattone saturo, nient'altro di rosso |
| dove finisce | quasi sempre sulla piazza principale, circondato da case |

Disegnato a ~4,1 × 4,1 quadretti al preset `quartiere`. Il segno che lo rende
riconoscibile è la coppia **loggia ad archi + torre dell'orologio**: la torre
vista a picco è un quadrato che sporge dal tetto, quindi va resa con il
quadrante dell'orologio o la campana visibili dall'alto, altrimenti sembra un
comignolo.

---

## Come usarlo

1. **Allega l'immagine di riferimento** (lo sprite-àncora dello stesso
   pacchetto).
2. Incolla il prompt qui sotto, tutto, in un messaggio solo.
3. Genera 2–3 candidati e scegli.
4. Per le varianti B e C: stesso prompt, sostituisci la sola riga `SUBJECT:`.

---

## Prompt — sprite canonico

```text
Asset for a hand-painted fantasy city battlemap, to be placed in Dungeondraft.

REFERENCE: the attached image is another asset from the same set. Match its brushwork, palette, lighting, texture grain and level of detail exactly, but draw a new, different subject as described below. Do not copy its content or its layout.

VIEW: strict orthographic plan view from directly above (90 degrees), like a satellite photo. Only roofs, courtyards and ground-level objects are visible. No facades, no walls seen from the side, no perspective, no isometric angle, no vanishing point.

ISOLATION: one single isolated subject, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. Include only the building and the strip of paving that strictly belongs to it. No grass, sea, trees, hills, roads or neighbouring buildings around it. Do not crop the subject: leave a small empty margin on every side, and let the subject fill the rest of the frame.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no compass rose, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the subject itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: earthy natural tones: pale dressed stone, ochre plaster, brown wood, muted greens. Small accents of deep blue and gold are allowed on the clock face and the banner. No neon or acid colours.

ROOFS: paint every roof in a uniform, saturated brick red; this colour is a recolour channel. Nothing else in the image may be saturated red.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof tiles, dressed stone, plaster, wood) the same way every time.

SUBJECT: Town hall: a stately rectangular civic palace of dressed pale stone under a tiled roof, with an open ground-floor loggia of round arches running along its whole front side, so that from above the loggia reads as a covered colonnaded strip with the arcade shadowed underneath. A square clock tower rises at one corner, taller than the roof, ending in a small open belfry with a bell and a round clock face turned upward enough to be visible from directly above. A small paved forecourt runs along the loggia, with a flagpole carrying a hanging civic banner and two stone benches. Everything is well built and symmetric: this is the most orderly building in the city.
```

## Variante B — municipio a corte

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Town hall on an L-shaped plan of dressed pale stone under tiled roofs, the two wings enclosing a small paved inner courtyard with a wellhead. An arcaded loggia runs along the ground floor of both wings facing the courtyard, and an external covered stone staircase climbs from the courtyard to the upper floor. A square clock tower with an open belfry rises where the two wings meet. A low wall with an arched gate closes the courtyard on one side, with a civic banner above the gate.
```

## Variante C — municipio con loggia del mercato

```text
SUBJECT: Town hall as a broad rectangular block of dressed stone under a tiled roof, with a deep covered market loggia occupying the entire ground floor: from above it reads as a colonnaded portico wrapping three sides of the building, with a few stacked crates and empty trestle tables sheltered under it. A slim bell tower with an open belfry and an upward-facing clock face rises from the middle of the roof ridge. Two civic banners hang from poles at the front corners.
```

---

## Dopo la generazione

- Scontorna il magenta e ripulisci la frangia colorata sul bordo alfa.
- Rifila, ricentra, margine trasparente del 5% per lato.
- Canvas a **768 × 768 px**.
- Ombra aggiunta in post: offset 4%, sfocatura 2,5%, opacità 45%, colore
  `(22, 16, 10)`, identica su tutto il pacchetto.
- Normalizza i tetti al rosso uniforme.
- Salva in **PNG con canale alfa**. Mai WebP.

## Checklist

- [ ] La torre dell'orologio si distingue da un comignolo
- [ ] La loggia si legge come portico ad archi, non come muro
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Niente prato o strada intorno: solo l'edificio e il suo sagrato
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Tetti rosso saturo uniforme; nessun altro rosso saturo
- [ ] Non sembra una casa ordinaria ingrandita
- [ ] PNG con alfa, non WebP
