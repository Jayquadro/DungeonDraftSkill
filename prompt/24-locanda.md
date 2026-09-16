# Sprite — Locanda (`nm_locanda.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce `inn_01`.

| | |
|---|---|
| nome file | `nm_locanda.png` |
| categoria | C3 — botteghe e servizi |
| canvas finale | 512 × 512 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **tetto ricolorabile**: i tetti in rosso mattone saturo, nient'altro di rosso |
| dove finisce | lotto urbano dei preset `quartiere` e `citta` |

Disegnato a ~2,4 × 2,4 quadretti al preset `quartiere`, ~0,7 × 0,7 al preset
`citta` — **la stessa dimensione della taverna**: il programma non le
distingue per grandezza, quindi il disegno deve farlo da solo. Presenza
attesa ~3,15 per mappa `quartiere` (dato non misurato a `citta`). La
**stalla annessa** e i **più piani** sono il segno che la distingue dalla
taverna.

---

## Come usarlo

1. **Allega l'immagine di riferimento** (idealmente lo sprite della taverna,
   già approvato, o l'àncora dello stesso pacchetto).
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

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof tiles, stone, plaster, wood, straw) the same way every time.

SUBJECT: Inn: a tall three-storey house, taller than an ordinary tavern, with a hanging sign over its main door and an attached open-sided stable block along one side, facing a small fenced yard where horses can be tied at a rail. A wooden exterior stair on the yard side leads up to the guest rooms.
```

## Variante B — locanda a cortile

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Inn built around a small enclosed courtyard reached through an arched carriage entrance from the street, guest wings rising three storeys on the other sides with wooden galleries overlooking the yard.
```

## Variante C — locanda con scuderia separata

```text
SUBJECT: Inn with the stable and hay loft as a separate taller building facing the main three-storey house across a shared yard, a well at the centre of the yard, hanging sign over the main house's door.
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

- [ ] Stalla annessa e più piani della taverna: si vedono chiaramente
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Niente prato o strada intorno: solo la locanda e il suo cortile
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Tetto rosso saturo uniforme; nessun altro rosso saturo
- [ ] Si distingue dalla taverna anche se della stessa dimensione sulla mappa
- [ ] PNG con alfa, non WebP
