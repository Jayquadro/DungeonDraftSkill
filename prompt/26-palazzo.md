# Sprite — Palazzo del Signore (`nm_palazzo.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce `bb_keepsandcastles_castle_color`,
un castello col fossato isolato in aperta campagna, che in mezzo a un
quartiere fitto sembra una toppa di campagna.

| | |
|---|---|
| nome file | `nm_palazzo.png` |
| categoria | C1 — monumenti |
| canvas finale | 1024 × 1024 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **nessun rosso saturo** |
| dove finisce | lotto urbano grande dei preset `quartiere` e `citta` |

Il catalogo segna questa categoria come `rosso: libero` (il post-processing
non tocca il colore), ma qui chiediamo comunque di evitare il rosso saturo,
così il palazzo non può cambiare tinta per sbaglio e resta un monumento
riconoscibile.

Disegnato a ~8,4 × 8,1 quadretti al preset `quartiere`, ~2,7 × 2,7 al preset
`citta`: è uno degli sprite più grandi della mappa, il dettaglio si vede
davvero. La **corte interna** e il fatto che sia una residenza dentro il
tessuto abitato, non isolata, sono i segni che lo distinguono da un castello
di campagna e dal monastero.

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

ISOLATION: one single isolated subject, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. Include only the subject and the ground that strictly belongs to it, up to its own boundary wall. No moat, no grass, no fields, no hills, no roads or neighbouring buildings around it. Do not crop the subject: leave a small empty margin on every side, and let the subject fill the rest of the frame.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no compass rose, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the subject itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: earthy natural tones: grey and ochre stone, brown wood, pale plaster, muted greens, with dark slate on the roofs and small accents of deep blue and gold on banners or trim. No red and no saturated reddish tones anywhere. No neon or acid colours.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof slates, stone, plaster, wood, banners) the same way every time.

SUBJECT: Lord's fortified residence built around a rectangular inner courtyard: crenellated curtain walls link corner towers of unequal height around the outer perimeter, while the side facing the courtyard is pierced by tall mullioned windows and a covered gallery, clearly more residential than defensive in character. A gatehouse with a raised portcullis opens directly onto the courtyard, where a stone wellhead and a small formal garden bed sit off-centre. This is the seat of the city's ruler standing inside the settlement, not an isolated country castle: no moat, no drawbridge, no open countryside around it.
```

## Variante B — palazzo a corte a L

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Lord's fortified residence on an L-shaped plan around an irregular courtyard: one wing is a tall crenellated keep with a single square tower at the corner, the other a lower residential range with an arcaded gallery facing the yard. A gatehouse pierces the short outer wall linking the two wings. The courtyard holds a covered well and a mounting block near the gate; a kitchen garden in raised beds fills the remaining corner.
```

## Variante C — palazzo a doppia corte

```text
SUBJECT: Lord's fortified residence built around two adjoining courtyards: an outer service court with stables and a well, reached through a gatehouse with a raised portcullis, and an inner residential court enclosed by a covered gallery with mullioned windows, reached through a second, unfortified archway. Corner towers of unequal height mark the outer perimeter only; the inner court has no fortification at all, just ornamental potted plants along the gallery.
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

- [ ] Corte interna riconoscibile, con residenza (finestre, loggia) distinta dalle mura di cinta
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Nessun fossato, nessun prato o campagna intorno: solo il palazzo e il suo perimetro
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Nessun rosso saturo da nessuna parte
- [ ] Non sembra un castello isolato di campagna (niente fossato, niente ponte levatoio)
- [ ] PNG con alfa, non WebP
