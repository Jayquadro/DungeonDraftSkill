# Sprite — Tempio (`nm_tempio.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce
`bb_city_cathedral_1_color`, che porta con sé il suo prato.

| | |
|---|---|
| nome file | `nm_tempio.png` |
| categoria | C2 — edifici pubblici medi |
| canvas finale | 768 × 768 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **tetto ricolorabile**: tetto in rosso mattone saturo, nient'altro di rosso |
| dove finisce | lotto urbano dei preset `quartiere` e `citta` |

Disegnato a ~4,2 × 3,9 quadretti al preset `quartiere`, ~1,1 × 1,3 al preset
`citta`. Presenza attesa ~0,8 per mappa `quartiere`, ~0,95 `citta`: è uno dei
luoghi più comuni. Deve leggersi come **una versione minore della
cattedrale**: navata unica, senza transetto né abside separata, chiaramente
più piccolo e più semplice.

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

SUBJECT: Temple: a single-nave church under one continuous tiled roof ridge, with a small bell tower rising beside the entrance and a modest paved forecourt in front of the main door. There is no transept and no separate apse wing: the plan is a simple rectangle, unmistakably smaller and plainer than a cathedral.
```

## Variante B — tempio con abside

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Temple with a small semicircular apse at the far end of its single nave, a squat bell tower at the entrance corner, and a narrow cloister-like walk along one side leading to a small walled garden.
```

## Variante C — tempio a due torri

```text
SUBJECT: Temple with twin low bell towers flanking a recessed entrance porch, single-nave roof behind them, a paved forecourt with a stone well or font at its centre.
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

- [ ] Navata unica, senza transetto: si distingue dalla cattedrale
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Niente prato o strada intorno: solo il tempio e il sagrato
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Tetto rosso saturo uniforme; nessun altro rosso saturo
- [ ] PNG con alfa, non WebP
