# Sprite — Banco da mercato (`nm_banco_mercato_1..3.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce `canopy_01`, il telo usato
oggi per la Piazza del Mercato.

| | |
|---|---|
| nomi file | `nm_banco_mercato_1.png`, `_2.png`, `_3.png` |
| categoria | C4 — pezzi dei luoghi all'aperto |
| dimensione vera | **2 × 2 m** |
| canvas finale | ~400 × 400 px (lo calcola il programma: 256 px = 1,5 m, quindi 2 m ≈ 341 px di oggetto più margine e ombra) |
| scala | **`reale`**, non `canvas`: questo è l'unico file del gruppo disegnato alla sua dimensione vera |
| rosso | libero; meglio evitare comunque il rosso saturo sulla tenda |
| dove finisce | sparso dentro l'area della Piazza del Mercato (4,7 × 3,8 quadretti), in 4 pezzi per area |

**È un oggetto singolo, non una scena.** Il generatore prende questo sprite e
lo ripete a caso dentro l'area del mercato, senza sovrapposizioni: un'immagine
che contenesse già più banchi, il selciato o della gente produrrebbe una piazza
fatta di piazze. Un banco, la sua merce, e basta.

Le tre varianti servono perché in una piazza si vedono quattro banchi insieme:
se fossero identici si noterebbe subito. Cambiano tenda e merce, non l'impianto.

---

## Come usarlo

1. **Allega l'immagine di riferimento** (lo sprite-àncora dello stesso
   pacchetto).
2. Incolla il prompt della variante 1, tutto, in un messaggio solo.
3. Genera 2–3 candidati e scegli.
4. Per le varianti 2 e 3: stesso prompt, sostituisci la sola riga `SUBJECT:`.
   Restano nella stessa conversazione, così la mano resta la stessa.

---

## Prompt — variante 1 (verdura e frutta)

```text
Asset for a hand-painted fantasy city battlemap, to be placed in Dungeondraft.

REFERENCE: the attached image is another asset from the same set. Match its brushwork, palette, lighting, texture grain and level of detail exactly, but draw a new, different subject as described below. Do not copy its content or its layout.

VIEW: strict orthographic plan view from directly above (90 degrees), like a satellite photo. Only the top surfaces are visible: the awning from above, and the goods spilling out around its edge. No facades, no perspective, no isometric angle, no vanishing point.

ISOLATION: one single isolated object, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. This is a single free-standing market stall, not a scene: no paving, no cobblestones, no ground texture, no people, no other stalls, no square around it. Do not crop the object: leave a small empty margin on every side.

SCALE: this object is small. Approximate real footprint: 2 x 2 m. Draw it at that true size, with the level of detail of a single piece of street furniture, not of a building.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the object itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: earthy natural tones: brown wood, cream and ochre cloth, muted greens. Avoid saturated red. No neon or acid colours.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (cloth, timber, wicker, sacking) the same way every time.

SUBJECT: A market stall seen from directly above: a square striped cloth awning stretched over four wooden corner poles covers most of the object, with a wooden trestle table underneath whose front edge sticks out past the awning. The goods on that visible edge of the table, and a wicker basket and a small crate standing on the ground beside the stall, are what identify it. The awning is striped in green and cream, and the goods are vegetables and fruit: cabbages, roots, apples, a sack of onions.
```

## Variante 2 — stoffe

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: A market stall seen from directly above: a square striped cloth awning stretched over four wooden corner poles covers most of the object, with a wooden trestle table underneath whose front edge sticks out past the awning. The awning is striped in blue and white, and the goods are bolts of cloth: rolls of fabric laid out in rows on the table edge, one bolt leaning against a pole, a basket of yarn on the ground beside the stall.
```

## Variante 3 — ceramiche

```text
SUBJECT: A market stall seen from directly above: a square striped cloth awning stretched over four wooden corner poles covers most of the object, with a wooden trestle table underneath whose front edge sticks out past the awning. The awning is striped in ochre and brown, and the goods are pottery: bowls and jugs arranged on the table edge, two large storage jars standing on the ground beside the stall, a stack of shallow plates.
```

---

## Dopo la generazione

- Scontorna il magenta e ripulisci la frangia colorata sul bordo alfa.
- **Ridimensiona alla scala reale, non al riquadro**: 2 m a 256 px = 1,5 m fa
  circa 341 px di lato per l'oggetto. Il canvas finale (~400 px) lo calcola il
  post-processing aggiungendo margine e ombra.
- Ombra aggiunta in post: offset 4%, sfocatura 2,5%, opacità 45%, colore
  `(22, 16, 10)`, identica su tutto il pacchetto.
- Salva in **PNG con canale alfa**. Mai WebP: `read_dungeondraft_pack` legge
  le dimensioni native dall'header IHDR, e per questo sprite la dimensione
  nativa *è* la dimensione reale sulla mappa.
- I tre file vanno consegnati insieme: il generatore pesca a caso fra le
  varianti.

## Checklist

- [ ] Un solo banco per immagine: niente piazza, niente selciato, niente gente
- [ ] Vista a picco: si vede la tenda dall'alto, non di lato
- [ ] La merce si riconosce: è l'unica cosa che distingue le tre varianti
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Niente rosso saturo sulla tenda
- [ ] Le tre varianti hanno lo stesso impianto e la stessa mano
- [ ] Dimensione coerente con un oggetto da 2 × 2 m, non con un edificio
- [ ] PNG con alfa, non WebP
