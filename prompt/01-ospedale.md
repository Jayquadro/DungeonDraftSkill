# Sprite — Ospedale (`nm_ospedale.png`)

Sprite dedicato per Gemini Nano Banana. Soggetto **nuovo**: nel catalogo non
esisteva, c'era solo `lazzaretto` (edificio d'isolamento fuori le mura). Questo
è invece l'ospedale cittadino, dentro le mura, in mezzo al tessuto abitato.

| | |
|---|---|
| nome file | `nm_ospedale.png` |
| categoria | C2 — edifici pubblici medi |
| canvas finale | 768 × 768 px |
| scala | `canvas` — lo sprite riempie il riquadro, la dimensione sulla mappa la decide il generatore |
| rosso | **tetto ricolorabile**: i tetti in rosso mattone saturo, nient'altro di rosso |
| dove finisce | lotto urbano dei preset `quartiere` e `citta`, circondato da case |

Disegnato a ~4 × 4 quadretti al preset `quartiere`, ~1,2 × 1,2 al preset
`citta`: a quella scala si legge la **sagoma**, non il dettaglio fine. La
corsia lunga e il chiostro devono essere riconoscibili a 200 px.

---

## Come usarlo

1. **Allega l'immagine di riferimento** (lo sprite-àncora già approvato dello
   stesso pacchetto). Senza riferimento il prompt funziona lo stesso, ma la
   coerenza di tratto con gli altri sprite va verificata a occhio.
2. Incolla il prompt qui sotto, **tutto**, in un messaggio solo.
3. Genera 2–3 candidati e scegli.
4. Per le varianti B e C: nella stessa conversazione, riparti dal prompt
   canonico e sostituisci la sola riga `SUBJECT:`.

---

## Prompt — sprite canonico

```text
Asset for a hand-painted fantasy city battlemap, to be placed in Dungeondraft.

REFERENCE: the attached image is another asset from the same set. Match its brushwork, palette, lighting, texture grain and level of detail exactly, but draw a new, different subject as described below. Do not copy its content or its layout.

VIEW: strict orthographic plan view from directly above (90 degrees), like a satellite photo. Only roofs, courtyards and ground-level objects are visible. No facades, no walls seen from the side, no perspective, no isometric angle, no vanishing point.

ISOLATION: one single isolated subject, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. Include only the subject and the ground that strictly belongs to it, inside its own boundary wall. No grass, sea, trees, hills, roads or neighbouring buildings around it. Do not crop the subject: leave a small empty margin on every side, and let the subject fill the rest of the frame.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no compass rose, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the subject itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: earthy natural tones: grey and ochre stone, brown wood, pale plaster, muted greens. No neon or acid colours.

ROOFS: paint every roof in a uniform, saturated brick red; this colour is a recolour channel. Nothing else in the image may be saturated red.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof tiles, stone, plaster, wood, water) the same way every time.

SUBJECT: City hospital: a long single-hall infirmary ward under a pitched tiled roof, with a small chapel attached at one end so that the plan forms an L. An arcaded cloister runs along the inner side and encloses a physic garden of medicinal herbs laid out in neat rectangular beds with a wellhead at the centre. A low stone boundary wall closes the complex, with one gated entrance and a covered porch beside it where two wooden stretchers are leaning. The whole thing reads as calm and orderly, not as a ruin or a prison.
```

## Variante B — ospedale a chiostro

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: City hospital built around a square cloister: infirmary wards under pitched tiled roofs occupy two adjacent sides, a small chapel with a bell-cote occupies the third, and an arcaded walkway runs all the way round the inner courtyard. The courtyard holds a wellhead and four square beds of medicinal herbs. A low stone wall with a single gate closes the remaining side.
```

## Variante C — ospedale a due corsie

```text
SUBJECT: City hospital made of two parallel infirmary halls under pitched tiled roofs, joined at one end by a covered walkway. The narrow courtyard between them holds a stone water cistern and a few benches. A chapel with a bell-cote stands at the entrance, and a low wall with a gate encloses a small paved forecourt where a cart is unloading bundles of straw.
```

---

## Dopo la generazione

- Scontorna il magenta e ripulisci la frangia colorata sul bordo alfa
  (`spritebatch elabora` lo fa con rembg; il fondo piatto gli semplifica il
  lavoro).
- Rifila, ricentra, margine trasparente del 5% per lato.
- Canvas a **768 × 768 px**.
- Ombra aggiunta in post: offset 4%, sfocatura 2,5%, opacità 45%, colore
  `(22, 16, 10)` — gli stessi numeri di `sprite-batch/catalogo.yaml`, così
  l'ombra è identica su tutto il pacchetto.
- Normalizza i tetti al rosso uniforme (ricolorabilità Dungeondraft).
- Salva in **PNG con canale alfa**. Mai WebP: il catalogo legge le dimensioni
  dall'header IHDR e con un WebP resta cieco.

## Checklist

- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Niente prato, strada o case intorno: solo l'ospedale e il suo recinto
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Tetti rosso saturo uniforme; nessun altro rosso saturo nell'immagine
- [ ] Nessuna scritta, cifra o cornice
- [ ] La sagoma si riconosce rimpicciolita a 200 px
- [ ] PNG con alfa, non WebP
