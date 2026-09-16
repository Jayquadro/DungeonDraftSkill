# Sprite — Monastero (`nm_monastero.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce
`bb_keepsandcastles_forestkeep_color`, che si porta dietro il bosco intorno.

| | |
|---|---|
| nome file | `nm_monastero.png` |
| categoria | C1 — monumenti |
| canvas finale | 1024 × 1024 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **nessun rosso saturo** |
| dove finisce | lotto urbano grande dei preset `quartiere` e `citta`, ai margini della città |

Il catalogo segna questa categoria come `rosso: libero` (il post-processing
non tocca il colore), ma qui chiediamo comunque di evitare il rosso saturo,
così il monastero non può cambiare tinta per sbaglio e resta un monumento
riconoscibile.

Disegnato a ~8,3 × 7,8 quadretti al preset `quartiere`, ~2,1 × 2,2 al preset
`citta`. Presenza attesa ~0,5 per mappa `quartiere`, ~0,4 `citta`: il
generatore lo tende a piazzare ai margini della città, non nel cuore fitto.
Il **chiostro quadrato**, la **chiesa su un lato** e l'**orto a filari** sono
i segni che lo distinguono dal palazzo e dall'accademia.

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

ISOLATION: one single isolated subject, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. Include only the subject and the ground that strictly belongs to it, up to its own boundary wall. No forest, sea, hills, roads or neighbouring buildings around it. Do not crop the subject: leave a small empty margin on every side, and let the subject fill the rest of the frame.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no compass rose, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the subject itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: earthy natural tones: grey and ochre stone, brown wood, pale plaster, muted greens on the garden and the roofs. No red and no saturated reddish tones anywhere. No neon or acid colours.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof tiles, stone, plaster, wood, cultivated soil) the same way every time.

SUBJECT: Monastery: a square cloister enclosed by a covered stone arcade on all four sides, a church with its own small bell tower occupying one whole side of the square, and a vegetable garden laid out in neat straight rows filling the cloister yard around a central well. A low stone boundary wall closes the rest of the complex, with a single gated entrance.
```

## Variante B — monastero a chiostro irregolare

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Monastery built around an irregular pentagon of cloister walks instead of a square, church with a taller bell tower on the side facing the entrance, the enclosed garden split into terraced beds following the uneven ground, a small orchard of espaliered fruit trees against the boundary wall.
```

## Variante C — monastero a doppio chiostro

```text
SUBJECT: Monastery with two adjoining cloisters of different sizes, the larger for the working garden in neat rows and the smaller, paved one beside the church for quiet walking. A refectory hall with its own roofline closes one side of the smaller cloister, and a low wall with a single gate encloses the whole complex.
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

- [ ] Chiostro quadrato, chiesa su un lato, orto a filari: tutti e tre leggibili
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Nessun bosco, nessun prato aperto, nessuna collina intorno
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Nessun rosso saturo da nessuna parte
- [ ] Non si confonde con l'accademia (niente torre-osservatorio) né col palazzo (niente fortificazione)
- [ ] PNG con alfa, non WebP
