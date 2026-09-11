# Sprite — Bagni Pubblici (`nm_bagni.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce `house_04`, che è una casa
qualunque e non dice niente.

| | |
|---|---|
| nome file | `nm_bagni.png` |
| categoria | C2 — edifici pubblici medi |
| canvas finale | 768 × 768 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **tetto ricolorabile**: i tetti in rosso mattone saturo, nient'altro di rosso |
| dove finisce | lotto urbano dei preset `quartiere` e `citta` |

Disegnato a ~4,0 × 4,4 quadretti al preset `quartiere`. È l'unico edificio del
pacchetto con **acqua dentro il perimetro**: le vasche a cielo aperto sono il
segno che lo rende riconoscibile. L'acqua deve stare solo dentro le vasche, mai
debordare — altrimenti sembra un edificio allagato o uno stagno.

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

VIEW: strict orthographic plan view from directly above (90 degrees), like a satellite photo. Only roofs, courtyards, pools and ground-level objects are visible. No facades, no walls seen from the side, no perspective, no isometric angle, no vanishing point.

ISOLATION: one single isolated subject, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. Include only the bath complex and the ground inside its own outer wall; the water appears only inside the pools and never spills outside them. No grass, sea, trees, hills, roads or neighbouring buildings around it. Do not crop the subject: leave a small empty margin on every side, and let the subject fill the rest of the frame.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no compass rose, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the subject itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: earthy natural tones: pale dressed stone, ochre plaster, brown wood, muted greens, and calm pale blue-green water in the pools only. No neon or acid colours.

ROOFS: paint every roof in a uniform, saturated brick red; this colour is a recolour channel. Nothing else in the image may be saturated red.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof tiles, dressed stone, plaster, wood, still water) the same way every time.

SUBJECT: Public baths: a large rectangular open-air bathing pool of pale dressed stone, filled with calm pale blue-green water, with broad steps entering it at one short end. Two smaller pools sit alongside it, one of them steaming faintly. A roofed portico on a stone colonnade runs along three sides of the pools, reading from above as a covered strip with the columns spaced along its inner edge. The fourth side is closed by a low changing-room block with a tiled roof and a squat furnace chimney. The paving between the pools carries a simple geometric border pattern, and a few benches and folded towels lie under the portico.
```

## Variante B — bagni a vasca ottagonale

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Public baths built around a large octagonal pool of pale dressed stone filled with calm blue-green water, with steps entering it on two opposite faces. An open rotunda of slender columns rings the pool, roofed only as a narrow circular canopy so that the water stays fully visible from above. Two rectangular side pools are set into the surrounding paving, and a changing-room block with a tiled roof and a furnace chimney closes one side of the complex. A low wall encloses the whole thing.
```

## Variante C — bagni caldi e freddi

```text
SUBJECT: Public baths made of two rectangular pools at different levels, joined by a short paved channel with a small stepped cascade: the upper pool steams gently, the lower one is still and clear. A roofed colonnaded portico runs along one long side and wraps one short side. A stone furnace house with a tiled roof and a tall chimney stands at the head of the upper pool, with a stack of firewood beside it. A low wall with a single gated entrance encloses the complex.
```

---

## Dopo la generazione

- Scontorna il magenta e ripulisci la frangia colorata sul bordo alfa.
- Rifila, ricentra, margine trasparente del 5% per lato.
- Canvas a **768 × 768 px**.
- Ombra aggiunta in post: offset 4%, sfocatura 2,5%, opacità 45%, colore
  `(22, 16, 10)`, identica su tutto il pacchetto.
- Normalizza i tetti al rosso uniforme. Controlla che l'acqua non sia finita
  nella maschera del rosso (non dovrebbe: è blu-verde).
- Salva in **PNG con canale alfa**. Mai WebP.

## Checklist

- [ ] Le vasche si vedono a cielo aperto e l'acqua sta solo dentro
- [ ] Il portico si legge come colonnato coperto su tre lati
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Niente prato, stagno o strada intorno: solo il complesso e il suo muro
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Tetti rosso saturo uniforme; nessun altro rosso saturo
- [ ] PNG con alfa, non WebP
