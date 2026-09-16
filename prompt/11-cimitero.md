# Sprite — Cimitero (`nm_cimitero_*.png`)

Sprite dedicati per Gemini Nano Banana. Sostituiscono i cinque pezzi di
ripiego usati oggi (`gravestone_01`, `gravestone_02`, `grave_01`, `grave_02`,
`grave_08`).

Il cimitero **non è un edificio**: è un luogo all'aperto (docs/sprite-luoghi.md
sez. 4). Il generatore stende un'area erbosa (`chr_grass`, 4,4 × 5,2
quadretti) e ci sparge sopra dei pezzi piccoli senza sovrapporli. Servono
quindi **5 file separati**, non uno sprite di edificio:

| | |
|---|---|
| nomi file | `nm_cimitero_lapide_1.png`, `_2.png`, `_3.png`, `nm_cimitero_croce.png`, `nm_cimitero_fossa.png` |
| categoria | C4 — pezzi dei luoghi all'aperto |
| scala | **`reale`**, non `canvas`: 256 px = 1,5 m |
| dimensione vera | lapide ~1 × 1,5 m; croce ~0,8 × 1,5 m; fossa recintata ~2,2 × 1,5 m |
| canvas finale | lo calcola il programma (dimensione reale + margine + ombra) |
| rosso | libero; evita comunque il rosso saturo |
| dove finisce | sparso dentro l'area del Cimitero, tutti i preset |

**Ogni file è un pezzo singolo, non una scena.** Il generatore lo ripete a
caso dentro l'area, senza sovrapposizioni: un'immagine che contenesse già
erba, altre lapidi o un vialetto produrrebbe un cimitero fatto di cimiteri.
Una lapide, il suo tumulo, e basta — l'erba la stende il generatore sotto.

Le tre varianti di lapide servono perché nell'area se ne vedono diverse
insieme: cambia la forma della pietra in testa, non l'impianto (lastra +
tumulo, vista dall'alto).

---

## Come usarlo

1. **Allega l'immagine di riferimento** (lo sprite-àncora dello stesso
   pacchetto).
2. Incolla il prompt della variante `lapide_1`, tutto, in un messaggio solo.
3. Genera 2–3 candidati e scegli.
4. Per `lapide_2`, `lapide_3`, `croce` e `fossa`: stessa conversazione,
   sostituisci la sola riga `SUBJECT:` con quella indicata più sotto, così la
   mano resta identica su tutti e cinque i pezzi.

---

## Prompt — `nm_cimitero_lapide_1.png` (lastra arcuata)

```text
Asset for a hand-painted fantasy city battlemap, to be placed in Dungeondraft.

REFERENCE: the attached image is another asset from the same set. Match its brushwork, palette, lighting, texture grain and level of detail exactly, but draw a new, different subject as described below. Do not copy its content or its layout.

VIEW: strict orthographic plan view from directly above (90 degrees), like a satellite photo. Only the top surface is visible. No facades, no perspective, no isometric angle, no vanishing point.

ISOLATION: one single isolated object, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. This is a single free-standing grave marker, not a scene: no grass, no other graves, no path, no cemetery ground around it. Do not crop the object: leave a small empty margin on every side.

SCALE: this object is small. Approximate real footprint: 1 x 1.5 m, headstone plus its low earthen mound. Draw it at that true size, with the level of detail of a single piece of churchyard furniture, not of a building.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the object itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: earthy natural tones: grey weathered stone, brown bare earth for the mound. No neon or acid colours, avoid saturated red.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (weathered stone, bare earth) the same way every time.

SUBJECT: A single grave seen from directly above: a narrow rectangular mound of bare earth with a flat stone headstone standing at one end, its top arched into a rounded shape. The stone casts no readable inscription, just weathered grey texture. The mound has a faint ridge down the middle where the earth was piled.
```

## Variante — `nm_cimitero_lapide_2.png` (lastra spezzata)

```text
SUBJECT: A single grave seen from directly above: a narrow rectangular mound of bare earth with a flat stone headstone standing at one end, broken diagonally across its top so that half is missing, tilted slightly to one side as if it has settled. Sparse tufts of weed grow at the base of the stone.
```

## Variante — `nm_cimitero_lapide_3.png` (lastra a losanga)

```text
SUBJECT: A single grave seen from directly above: a narrow rectangular mound of bare earth with a flat stone headstone standing at one end, its top cut into a simple pointed gable shape. A thin stone border edges the mound on both long sides, like a low kerb.
```

## Prompt — `nm_cimitero_croce.png`

```text
SUBJECT: A single grave seen from directly above: a narrow rectangular mound of bare earth with a plain wooden cross planted upright at one end, the crossbar clearly visible from above as a short perpendicular stroke near the top of the vertical post. The mound is slightly narrower and more weathered-looking than the ones marked by a stone headstone.
```

## Prompt — `nm_cimitero_fossa.png` (fossa recintata)

```text
SUBJECT: An open grave plot seen from directly above: a freshly dug rectangular pit of dark turned earth, larger than a single mound, enclosed by a low waist-high fence of wooden pickets on all four sides with a small gap serving as an entrance on one side. A spade stands stuck upright in the earth beside the pit.
```

---

## Dopo la generazione

- Scontorna il magenta e ripulisci la frangia colorata sul bordo alfa.
- **Ridimensiona alla scala reale, non al riquadro**: 256 px = 1,5 m, quindi
  la lapide (1 × 1,5 m) misura circa 170 × 256 px di oggetto, la fossa
  (2,2 × 1,5 m) circa 375 × 256 px. Il canvas finale lo calcola il
  post-processing aggiungendo margine e ombra.
- Ombra aggiunta in post: offset 4%, sfocatura 2,5%, opacità 45%, colore
  `(22, 16, 10)`, identica su tutto il pacchetto.
- Salva in **PNG con canale alfa**. Mai WebP: `read_dungeondraft_pack` legge
  le dimensioni native dall'header IHDR, e per questi sprite la dimensione
  nativa *è* la dimensione reale sulla mappa.
- I cinque file vanno consegnati insieme: il generatore pesca a caso fra i
  pezzi disponibili quando popola l'area.

## Checklist

- [ ] Un solo pezzo per immagine: niente erba, niente altre lapidi, niente vialetto
- [ ] Vista a picco: il tumulo e la pietra si leggono dall'alto, non di lato
- [ ] Le tre lapidi si distinguono per la forma della pietra in testa, non per l'impianto
- [ ] La croce si distingue chiaramente dalle lapidi (palo verticale, non lastra)
- [ ] La fossa recintata è più grande dei singoli tumuli e ha il recinto di pali
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Niente rosso saturo da nessuna parte
- [ ] Dimensioni coerenti con oggetti da 1–2,2 m, non con un edificio
- [ ] PNG con alfa, non WebP
