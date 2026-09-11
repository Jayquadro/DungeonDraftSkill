# Sprite — Faro (`nm_faro.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce
`bb_seasandshores_cliff_lighthouse_color`, che si porta dietro la scogliera e
il mare: piazzato sulla banchina del porto diventa una toppa di costa in mezzo
alla città.

| | |
|---|---|
| nome file | `nm_faro.png` |
| categoria | C2 — edifici pubblici medi |
| canvas finale | 768 × 768 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **nessun rosso**: il faro non deve cambiare tinta con le case |
| dove finisce | sulla banchina del porto, con l'acqua **già disegnata dalla mappa** |

Disegnato a ~3,1 × 3,0 quadretti al preset `quartiere`. È il caso peggiore del
pacchetto per il problema del contorno: un faro visto a picco è quasi un
cerchio, e la tentazione del modello è riempire gli angoli con scogli e
schiuma. **Negli angoli non ci deve essere niente.**

---

## Come usarlo

1. **Allega l'immagine di riferimento** (lo sprite-àncora dello stesso
   pacchetto).
2. Incolla il prompt qui sotto, tutto, in un messaggio solo.
3. Genera 2–3 candidati e scegli. Scarta senza pietà qualunque candidato con
   acqua, scogli o schiuma.
4. Per le varianti B e C: stesso prompt, sostituisci la sola riga `SUBJECT:`.

---

## Prompt — sprite canonico

```text
Asset for a hand-painted fantasy city battlemap, to be placed in Dungeondraft.

REFERENCE: the attached image is another asset from the same set. Match its brushwork, palette, lighting, texture grain and level of detail exactly, but draw a new, different subject as described below. Do not copy its content or its layout.

VIEW: strict orthographic plan view from directly above (90 degrees), like a satellite photo. Only roofs, terraces and ground-level objects are visible. No facades, no walls seen from the side, no perspective, no isometric angle, no vanishing point. Because the tower is seen from straight above, it reads as concentric rings, not as a tall tower.

ISOLATION: one single isolated subject, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. This is critical: there must be NO water, NO sea, NO waves, NO foam, NO rocks, NO cliff, NO beach and NO grass anywhere in the image. The sea will already be painted on the map underneath. Include only the lighthouse and the small patch of quay paving it stands on. Do not crop the subject: leave a small empty margin on every side, and let the subject fill the rest of the frame.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no compass rose, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the subject itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: pale grey and ochre dressed stone, weathered brown wood, dark metal, muted greens. Warm yellow glow allowed only inside the lantern glass. No red and no saturated reddish tones anywhere. No neon or acid colours.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (stone, timber, metal, glass, quay paving) the same way every time.

SUBJECT: Lighthouse seen from directly above: a cylindrical stone tower reading as concentric rings, with a glazed lantern room at the very centre, its metal astragal frame dividing the glass into panes and a faint warm glow inside. Around the lantern runs a narrow railed gallery. The tower widens towards the bottom into a stepped round stone base, and a small square keeper's cottage with a tiled roof is attached to that base. The whole thing stands on a compact patch of stone quay paving cut off cleanly at its edge, with a mooring bollard and a coil of rope on it.
```

## Variante B — faro a torre quadrata

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Lighthouse seen from directly above as a square tapering stone tower: nested squares stepping inwards, with a glazed lantern room and its railed gallery at the centre. An external stone stair spirals around the outside of the tower and reads from above as a stepped band winding down to a small arched doorway at the base. A low keeper's cottage with a tiled roof is attached to one side. It stands on a compact patch of quay paving cut off cleanly at its edge, with a stack of barrels for lamp oil beside it.
```

## Variante C — faro sul bastione

```text
SUBJECT: Lighthouse rising from a small round stone bastion: from above, an outer ring of low parapet wall encloses a paved terrace, and the cylindrical tower stands at its centre with a glazed lantern room and a railed gallery at the top. On the terrace there is a wood store, an iron brazier and two mooring bollards. The bastion's outer edge is cut off cleanly; nothing beyond it.
```

---

## Dopo la generazione

- Scontorna il magenta e ripulisci la frangia colorata sul bordo alfa.
- Rifila, ricentra, margine trasparente del 5% per lato.
- Canvas a **768 × 768 px**.
- Ombra aggiunta in post: offset 4%, sfocatura 2,5%, opacità 45%, colore
  `(22, 16, 10)`, identica su tutto il pacchetto.
- Passa la soppressione del rosso: niente tegole rossastre sul cottage.
- Salva in **PNG con canale alfa**. Mai WebP.

## Checklist

- [ ] **Nessuna acqua, onda, schiuma, scogliera o spiaggia nell'immagine**
- [ ] La lanterna sta al centro e si vede il vetro
- [ ] Il faro si legge come cerchi concentrici, non come una torre in prospettiva
- [ ] Il lastricato della banchina finisce netto, senza sfumare nel vuoto
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Nessun rosso da nessuna parte
- [ ] PNG con alfa, non WebP
