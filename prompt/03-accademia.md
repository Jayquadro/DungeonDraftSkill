# Sprite — Accademia di Magia (`nm_accademia.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce `castle_w_moat`, che è un
castello col fossato e in mezzo a un quartiere sembra una toppa di campagna.

| | |
|---|---|
| nome file | `nm_accademia.png` |
| categoria | C1 — monumenti |
| canvas finale | 1024 × 1024 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **nessun rosso saturo** |
| dove finisce | lotto urbano grande dei preset `quartiere` e `citta` |

Il catalogo segna questa categoria come `rosso: libero` (il post-processing non
tocca il colore). Qui chiediamo comunque di evitare il rosso saturo: così lo
sprite non può cambiare tinta per sbaglio, e l'Accademia resta un monumento
riconoscibile invece che una casa colorata più grande.

Disegnato a ~8,7 × 8,1 quadretti al preset `quartiere`: è uno degli sprite più
grandi della mappa, il dettaglio si vede davvero. La **torre-osservatorio** è
il segno che lo distingue dal palazzo e dal monastero.

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

VIEW: strict orthographic plan view from directly above (90 degrees), like a satellite photo. Only roofs, courtyards and ground-level objects are visible. No facades, no walls seen from the side, no perspective, no isometric angle, no vanishing point.

ISOLATION: one single isolated subject, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. Include only the subject and the ground that strictly belongs to it, up to its own boundary wall. No grass, sea, moat, trees, hills, roads or neighbouring buildings around it. Do not crop the subject: leave a small empty margin on every side, and let the subject fill the rest of the frame.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no compass rose, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the subject itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: earthy natural tones: grey and ochre stone, brown wood, pale plaster, muted greens, with dark slate and verdigris copper on the roofs. Deep blue and gold are allowed as small accents only. No red and no saturated reddish tones anywhere. No neon or acid colours.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof slates, stone, plaster, wood, glass) the same way every time.

SUBJECT: Academy of magic: an L-shaped main building with steep dark slate roofs, and a tall round observatory tower rising at the inner corner, capped by a verdigris copper dome with a shutter slot and a large brass astrolabe mounted beside it on a flat terrace. The two wings enclose a paved courtyard whose flagstones carry a subtle inlaid circular figure. Along one wing runs a glass-roofed hall, its panes catching the light. A low wall with a single arched gate closes the fourth side. The building reads as scholarly and expensive: cut stone, ordered windows, no fortification, no moat.
```

## Variante B — accademia a corte chiusa

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Academy of magic on a U-shaped plan closing around an enclosed courtyard, steep dark slate roofs. Two towers of different heights rise at the outer corners: the taller one is round and ends in a verdigris copper dome with an open shutter, the shorter is square with a flat railed terrace holding an armillary sphere. The courtyard paving carries an inlaid zodiac wheel around a small fountain. A cloister walk runs along the inside of the U, and a low wall with an arched gate closes the open side.
```

## Variante C — accademia a torre centrale

```text
SUBJECT: Academy of magic as a compact square block with steep dark slate roofs, pierced at the centre by a tall octagonal tower that ends in a railed observation terrace with a brass astrolabe. One wing is roofed entirely in glass over a library hall. Part of the flat roof is laid out as a terraced garden of strange plants in stone troughs, with narrow paths between them. A narrow paved service yard with a wellhead sits against one side, closed by a low wall and a gate.
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

- [ ] La torre-osservatorio si vede e si capisce anche a picco
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Nessun fossato, nessun prato, nessuna collina intorno
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Nessun rosso saturo da nessuna parte
- [ ] Non sembra un castello: niente merli, niente torrioni difensivi
- [ ] PNG con alfa, non WebP
