# Sprite — Caserma della Guardia (`nm_caserma.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce `bb_city_fort_1_color`,
che è un forte e sembra una toppa fuori posto in mezzo a un quartiere.

| | |
|---|---|
| nome file | `nm_caserma.png` |
| categoria | C2 — edifici pubblici medi |
| canvas finale | 768 × 768 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **tetto ricolorabile**: tetto in rosso mattone saturo, nient'altro di rosso |
| dove finisce | lotto urbano dei preset `quartiere` e `citta` |

Disegnato a ~4,4 × 3,5 quadretti al preset `quartiere`, ~1,3 × 1,2 al preset
`citta`. Presenza attesa ~0,75 per mappa `quartiere`, ~0,9 `citta`. È un
**corpo di guardia**, non una fortezza: il **cortile d'armi recintato con le
rastrelliere** è il segno distintivo, niente merli né torri difensive.

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

SUBJECT: Guard barracks: a U-shaped building of tiled-roof wings wrapping three sides of a drill yard, the fourth side closed by a low wooden fence with a single gate. Weapon racks holding spears and shields stand along the inner wall of one wing, and a small stable lean-to occupies a corner of the yard. It should read as a working garrison, not a fortress: no crenellations, no moat.
```

## Variante B — caserma a cortile chiuso

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Guard barracks built around a rectangular drill yard enclosed on all four sides, one side a low wooden fence with a gatehouse, the other three tiled-roof ranges. A raised wooden watch platform stands in one corner of the yard, and weapon racks line the wall beneath it.
```

## Variante C — caserma con scuderia

```text
SUBJECT: Guard barracks with an L-shaped main building and a separate small stable block facing it across a fenced drill yard, a mounting block and a water trough between them, weapon racks fixed along the barracks wall.
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

- [ ] Cortile d'armi recintato con rastrelliere: si vede chiaramente
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Niente prato o strada intorno: solo la caserma e il suo cortile
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Tetto rosso saturo uniforme; nessun altro rosso saturo
- [ ] Non sembra un forte o un castello: niente merli, niente torri difensive
- [ ] PNG con alfa, non WebP
