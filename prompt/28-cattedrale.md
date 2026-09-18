# Sprite — Cattedrale (`nm_cattedrale.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce
`bb_keepsandcastles_cathedral_color`, un monumento fuori scala preso in
prestito da un altro pacchetto.

| | |
|---|---|
| nome file | `nm_cattedrale.png` |
| categoria | C1 — monumenti |
| canvas finale | 1024 × 1024 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **nessun rosso saturo** |
| dove finisce | lotto urbano grande dei preset `quartiere` e `citta` |

Il catalogo segna questa categoria come `rosso: libero` (il post-processing
non tocca il colore), ma qui chiediamo comunque di evitare il rosso saturo,
così la cattedrale non può cambiare tinta per sbaglio e resta un monumento
riconoscibile.

Disegnato a ~8,9 × 7,5 quadretti al preset `quartiere`, ~2,5 × 2,5 al preset
`citta`: è il monumento religioso più grande della città. La pianta a
**navata, transetto e abside**, molto più estesa e articolata di quella del
tempio (chiesa a navata unica, categoria C2, molto più piccola), è il segno
che la distingue.

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

ISOLATION: one single isolated subject, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. Include only the subject and the paved ground that strictly belongs to it, up to its own boundary. No grass, square, trees, roads or neighbouring buildings around it. Do not crop the subject: leave a small empty margin on every side, and let the subject fill the rest of the frame.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no compass rose, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the subject itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: earthy natural tones: pale grey stone, weathered ochre trim, dark slate roofs, with small accents of deep blue and gold on stained-glass hints and finials. No red and no saturated reddish tones anywhere. No neon or acid colours.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof slates, stone, stained glass, plaster) the same way every time.

SUBJECT: A large cathedral on a cruciform plan: a long steep-roofed nave crossed by a shorter transept, meeting at a squat crossing tower, and ending in a rounded apse at the far end. Twin square towers with pointed spires flank the main entrance at the opposite end. Flying buttresses line both sides of the nave, and tall pointed stained-glass windows pierce the walls between them. A paved forecourt with a few stone benches lies in front of the entrance, enclosed by a low balustrade. The whole complex is unmistakably the largest religious building in the city, far larger and more elaborate than a simple parish church.
```

## Variante B — cattedrale a doppio campanile arretrato

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: A large cathedral on a cruciform plan with a long steep-roofed nave, a wide transept, and a polygonal apse with a ring of small radiating chapels at the far end. A single massive crossing tower with a tall spire rises where nave and transept meet, taller than any other point of the building. The main entrance, at the opposite end from the apse, is framed by a shallow porch with three stepped arches. Flying buttresses line the nave, and a cloister with a small garth adjoins one side of the transept.
```

## Variante C — cattedrale a facciata a torre unica

```text
SUBJECT: A large cathedral on a cruciform plan with a long steep-roofed nave, a narrow transept, and a rounded apse. A single tall tower rises directly over the main entrance facade at the opposite end, rather than at the crossing. A round rose-window opening is visible in the roof pitch above the entrance. Flying buttresses line both sides of the nave, and a walled cemetery garden with a few carved headstones occupies the far side beyond the apse.
```

---

## Dopo la generazione

- Scontorna il magenta e ripulisci la frangia colorata sul bordo alfa.
- Rifila, ricentra, margine trasparente del 5% per lato.
- Canvas a **1024 × 1024 px**.
- Ombra aggiunta in post: offset 4%, sfocatura 2,5%, opacità 45%, colore
  `(22, 16, 10)`, identica su tutto il pacchetto.
- Verifica che non resti rosso saturo (altrimenti spostalo su ocra).
- Salva in **PNG con canale alfa**. Mai WebP.

## Checklist

- [ ] Navata, transetto e abside riconoscibili anche a picco
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Nessun prato, piazza o edificio vicino intorno: solo la cattedrale e il suo sagrato
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Nessun rosso saturo da nessuna parte
- [ ] Si distingue dal tempio per dimensione e complessità della pianta (non una semplice chiesa a navata unica)
- [ ] PNG con alfa, non WebP
