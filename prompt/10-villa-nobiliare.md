# Sprite — Villa Nobiliare (`nm_villa_nobiliare.png`)

Sprite dedicato per Gemini Nano Banana.

> **⚠️ Attenzione: questo luogo non esiste ancora nel generatore.** Non c'è
> nessun `LandmarkKind` "villa nobiliare" (o simile) in
> `src/ddforge/generators/landmarks.py`, e non compare in
> `docs/sprite-luoghi.md`. Lo sprite si può generare fin da subito — non ha
> bisogno del codice per esistere — ma finché il tipo non è aggiunto al
> generatore nessuna mappa lo piazza: l'immagine resta senza un posto dove
> finire. Prima di mettere questo sprite in produzione, apri un task per
> aggiungere il `LandmarkKind` corrispondente (categoria, `scales`, `rule`,
> dimensione dei lotti) e per misurare la dimensione disegnata come è stato
> fatto per l'ospedale in TASK-48.1.

| | |
|---|---|
| nome file | `nm_villa_nobiliare.png` |
| categoria | **proposta, non misurata**: C2 — edifici pubblici medi |
| canvas finale | 768 × 768 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **tetto ricolorabile**: i tetti in rosso mattone saturo, nient'altro di rosso |
| dove finisce | ancora nessuno: da definire quando il `LandmarkKind` esisterà |

Canvas e categoria qui sopra sono una proposta ragionata per coerenza col
resto del pacchetto (residenza signorile, più grande di una bottega ma non un
monumento cittadino unico come il Palazzo del Signore), **non** una misura
presa sul generatore. La caratteristica che la distingue da una casa
qualunque è la **corte privata recintata** con ingresso ornato.

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

ISOLATION: one single isolated subject, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. Include only the subject and the ground that strictly belongs to it, inside its own boundary wall or fence. No grass, sea, trees, hills, roads or neighbouring buildings around it. Do not crop the subject: leave a small empty margin on every side, and let the subject fill the rest of the frame.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no compass rose, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the subject itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: earthy natural tones: grey and ochre stone, brown wood, pale plaster, muted greens. No neon or acid colours.

ROOFS: paint every roof in a uniform, saturated brick red; this colour is a recolour channel. Nothing else in the image may be saturated red.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof tiles, stone, plaster, wood, wrought iron) the same way every time.

SUBJECT: Noble townhouse: a stately two- or three-storey residence built around a small private courtyard, with an ornamented main entrance reached by a short flight of steps and a low wrought-iron fence enclosing a narrow front garden. The roof is steep and tiled, with a pair of tall chimneys and a small decorative balcony overlooking the courtyard. It should read as clearly grander than an ordinary house, but still a private residence, not a public building.
```

## Variante B — villa a corte e giardino murato

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Noble townhouse on an L-shaped plan wrapping a walled garden with a fountain at its centre, ornamented entrance on the street side reached by shallow steps, tall chimneys and a small corner turret with a conical roof marking the residence as aristocratic.
```

## Variante C — villa con corte d'onore

```text
SUBJECT: Noble townhouse with a formal front courtyard closed by a low wall and a wrought-iron gate flanked by two stone piers, the house itself set back with a columned entrance porch, steep tiled roof and dormer windows.
```

---

## Dopo la generazione

- Scontorna il magenta e ripulisci la frangia colorata sul bordo alfa.
- Rifila, ricentra, margine trasparente del 5% per lato.
- Canvas a **768 × 768 px** (da confermare quando il luogo avrà una misura reale).
- Ombra aggiunta in post: offset 4%, sfocatura 2,5%, opacità 45%, colore
  `(22, 16, 10)`, identica su tutto il pacchetto.
- Normalizza i tetti al rosso uniforme.
- Salva in **PNG con canale alfa**. Mai WebP.

## Checklist

- [ ] La corte privata recintata si vede ed è il segno distintivo
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Niente prato, strada o case intorno: solo la villa e il suo recinto
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Tetti rosso saturo uniforme; nessun altro rosso saturo
- [ ] Non sembra un palazzo pubblico né un monumento: resta una residenza privata
- [ ] PNG con alfa, non WebP
- [ ] Prima di produrre in serie: verificato che esista un `LandmarkKind` per questo luogo
