# Sprite — Arena (`nm_arena.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce `tourney_grounds`, un
campo da torneo con tende e steccati che non si legge come un monumento
cittadino. Ammesso solo al preset `citta` (`docs/sprite-luoghi.md` sez.3).

| | |
|---|---|
| nome file | `nm_arena.png` |
| categoria | C1 — monumenti |
| canvas finale | 1024 × 1024 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **nessun rosso saturo** |
| dove finisce | lotto urbano grande del preset `citta` |

Il catalogo segna questa categoria come `rosso: libero` (il post-processing
non tocca il colore), ma qui chiediamo comunque di evitare il rosso saturo,
così l'arena non può cambiare tinta per sbaglio e resta un monumento
riconoscibile.

Disegnato a ~2,6 × 2,6 quadretti al preset `citta` (non ammesso a `quartiere`
né a `isolato`), presenza attesa ~0,4 per mappa. L'**anfiteatro ellittico con
gradinate concentriche**, visto dall'alto, è il segno che lo distingue dal
teatro (pianta semicircolare, categoria C2, molto più piccolo).

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

VIEW: strict orthographic plan view from directly above (90 degrees), like a satellite photo. Only the tiered seating, the arena floor and ground-level structures are visible. No facades, no walls seen from the side, no perspective, no isometric angle, no vanishing point.

ISOLATION: one single isolated subject, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. Include only the subject and the ground that strictly belongs to it, up to its own outer wall. No town square, no streets, no trees or neighbouring buildings around it. Do not crop the subject: leave a small empty margin on every side, and let the subject fill the rest of the frame.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no compass rose, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the subject itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: earthy natural tones: grey and ochre stone, pale sand for the arena floor, weathered wood for the barriers. No red and no saturated reddish tones anywhere. No neon or acid colours.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (stone tiers, sand, timber) the same way every time.

SUBJECT: An elliptical amphitheatre: concentric rings of stone tiered seating surround a flat oval arena floor of pale packed sand, with a low timber barrier separating the seating from the floor. Two opposite arched gateways at the ends of the long axis lead into the arena. A narrow stone ambulatory circles the outermost ring, and the whole structure is closed by a continuous outer wall following the ellipse. No tents, no scaffolding, no roof: a permanent stone structure, not a temporary tournament ground.
```

## Variante B — arena a doppio anello

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: An elliptical amphitheatre with two distinct rings of stone tiered seating separated by a narrow covered gallery running all the way round, a flat oval arena floor of pale packed sand at the centre with a low timber barrier, and four small arched gateways spaced evenly around the ellipse instead of just two at the ends. A continuous outer wall with a single pair of larger gatehouses on the short axis closes the structure.
```

## Variante C — arena con fossa centrale

```text
SUBJECT: An elliptical amphitheatre where the arena floor sits noticeably lower than the surrounding ground, reached by a short stone ramp at one end, with concentric tiers of stone seating rising around it and a low timber barrier at the floor's edge. A single monumental arched gateway on the long axis serves as the main entrance, opposite a smaller service gate. A continuous outer wall follows the ellipse.
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

- [ ] Anfiteatro ellittico con gradinate concentriche riconoscibile dall'alto
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Nessuna piazza, strada o edificio vicino intorno: solo l'arena e il suo perimetro
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Nessun rosso saturo da nessuna parte
- [ ] Non si confonde con il teatro (niente pianta semicircolare, niente tende da torneo)
- [ ] PNG con alfa, non WebP
