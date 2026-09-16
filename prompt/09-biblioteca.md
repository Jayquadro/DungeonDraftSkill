# Sprite — Biblioteca (`nm_biblioteca.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce `house_05`, che è una casa
qualunque e non dice niente.

| | |
|---|---|
| nome file | `nm_biblioteca.png` |
| categoria | C3 — botteghe e servizi |
| canvas finale | 512 × 512 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **tetto ricolorabile**: i tetti in rosso mattone saturo, nient'altro di rosso |
| dove finisce | lotto urbano dei preset `quartiere` e `citta` |

Disegnato a ~2,4 × 2,4 quadretti al preset `quartiere`, ~0,7 × 0,7 al preset
`citta` (la stessa dimensione di tutte le botteghe ordinarie: qui si
distingue per forma, non per mole). Presenza attesa ~0,60 per mappa
`quartiere`, ~0,45 `citta`. I **lucernari sul tetto** e la **scalinata
d'ingresso** sono il segno che la rende riconoscibile da una casa qualunque.

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

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof tiles, stone, plaster, wood) the same way every time.

SUBJECT: Public library: a compact rectangular building with a row of glazed skylights running along the ridge of its tiled roof, and a short flight of stone steps leading up to a single arched entrance on one side. A narrow paved forecourt with a low iron railing separates the entrance from the street. The roof is otherwise plain, so the skylights are the one detail that marks the building from above.
```

## Variante B — biblioteca a corte interna

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Public library built around a small square light-well at its centre, glazed skylights lining the inner roof slopes so daylight reaches deep into the building. A single arched entrance opens onto the street through a short flight of stone steps, with a narrow paved forecourt in front.
```

## Variante C — biblioteca con ala di lettura

```text
SUBJECT: Public library made of a main block with roof skylights and a lower reading-room wing attached at one end, its own smaller skylights running the length of its roof. A stone entrance staircase climbs to a single door at the corner where the two volumes meet, opening onto a narrow paved forecourt.
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

- [ ] I lucernari sul tetto si vedono chiaramente
- [ ] La scalinata d'ingresso è leggibile
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Niente prato o strada intorno: solo l'edificio e il suo poco spazio
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Tetto rosso saturo uniforme; nessun altro rosso saturo
- [ ] Non si confonde con una casa qualunque: i lucernari sono il segno
- [ ] PNG con alfa, non WebP
