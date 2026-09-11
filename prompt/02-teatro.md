# Sprite — Teatro (`nm_teatro.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce
`bb_keepsandcastles_amphitheatre_color`, che si porta dietro il prato intorno.

| | |
|---|---|
| nome file | `nm_teatro.png` |
| categoria | C2 — edifici pubblici medi |
| canvas finale | 768 × 768 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **tetto ricolorabile**: tettoie e coperture in rosso mattone saturo |
| dove finisce | lotto urbano dei preset `quartiere` e `citta` |

Disegnato a ~4,9 × 3,4 quadretti al preset `quartiere`. È l'unico edificio del
pacchetto con pianta **semicircolare**: è quello il segno che lo rende
riconoscibile a colpo d'occhio, più di qualunque dettaglio.

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

ISOLATION: one single isolated subject, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. Include only the subject and the ground that strictly belongs to it, up to its outer wall. No grass, sea, trees, hills, roads or neighbouring buildings around it. Do not crop the subject: leave a small empty margin on every side, and let the subject fill the rest of the frame.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no compass rose, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the subject itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: earthy natural tones: grey and ochre stone, brown wood, pale plaster, muted greens. No neon or acid colours.

ROOFS: paint every roof and awning in a uniform, saturated brick red; this colour is a recolour channel. Nothing else in the image may be saturated red.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof tiles, stone, plaster, wood, canvas) the same way every time.

SUBJECT: Open-air theatre with a strictly semicircular plan: concentric tiers of stone seating step down towards a flat half-round orchestra floor of pale paving. Along the straight side stands a rectangular stage building with a roof, its stage platform facing the tiers. Two narrow stepped aisles cut radially through the seating, and two vaulted entrance passages open at the ends of the straight side. A roofed awning strip runs along the outer rim of the top tier. The seating is open to the sky, so the tiers are fully visible from above.
```

## Variante B — teatro di legno coperto

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Wooden playhouse on a polygonal plan: a ring of three roofed timber galleries encloses an open unroofed yard of packed earth at the centre. A rectangular stage with its own small roof projects into the yard from one side, with a tiring-house block behind it. A single gated entrance breaks the ring on the opposite side. The roofs are the only covered parts; the yard in the middle stays open and clearly visible from above.
```

## Variante C — teatro con velario

```text
SUBJECT: Half-round theatre cut against a straight rectangular back wall: concentric stone seating tiers face a paved half-round orchestra, with a long stage building closing the straight side. A canvas velarium is stretched only over the upper half of the tiers, held by a row of tall wooden poles fixed along the outer rim, so that part of the seating shows through and part is covered. Two side passages run in at ground level.
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

- [ ] Pianta semicircolare leggibile: è il segno distintivo del teatro
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Niente prato o strada intorno: solo il teatro
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Tetti e tettoie rosso saturo uniforme; nessun altro rosso saturo
- [ ] Le gradinate si leggono come gradini concentrici, non come una macchia
- [ ] PNG con alfa, non WebP
