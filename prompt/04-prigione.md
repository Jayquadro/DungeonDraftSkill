# Sprite — Prigione (`nm_prigione.png`)

Sprite dedicato per Gemini Nano Banana. Sostituisce `cage_04`, che è una gabbia
singola e alla dimensione di un edificio non si legge.

| | |
|---|---|
| nome file | `nm_prigione.png` |
| categoria | C2 — edifici pubblici medi |
| canvas finale | 768 × 768 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **nessun rosso**: la prigione non deve cambiare tinta con le case |
| dove finisce | lotto urbano dei preset `quartiere` e `citta` |

Disegnato a ~2,3 × 2,3 quadretti al preset `quartiere`: è uno degli sprite
**più piccoli** fra i luoghi notevoli. A quella dimensione conta solo la
sagoma: blocco massiccio + cortile chiuso da mura alte. Niente dettaglio
minuto, che sparirebbe.

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

ISOLATION: one single isolated subject, centred in the frame, on a flat uniform pure magenta background (#FF00FF). That background is a chroma key: keep it perfectly flat, with no gradient, no texture, no vignette and no shadow falling onto it. Include only the subject and the ground inside its own enclosing wall. No grass, sea, trees, hills, roads or neighbouring buildings around it. Do not crop the subject: leave a small empty margin on every side, and let the subject fill the rest of the frame.

STYLE: warm hand-painted illustration, like a medieval European city map in a tabletop RPG sourcebook. Soft brushwork, subtle texture. Not pixel art, not flat vector, not photorealistic. No text, no labels, no letters, no numbers, no scale bar, no compass rose, no frame or border.

LIGHT: soft light from the top-left, used only for volume shading on the subject itself. Do NOT paint any cast shadow on the ground or on the background.

PALETTE: cold grey stone, dark weathered timber, ochre and brown earth, muted and desaturated throughout. No red and no saturated reddish tones anywhere. No neon or acid colours.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof slates, rough stone, timber, packed earth) the same way every time.

SUBJECT: Prison: a massive rectangular block of rough grey stone with heavy buttressed corners and a steep unbroken slate roof with no skylights and no roof openings at all. It stands inside a high stone perimeter wall with a narrow walkway along its top, enclosing a bare yard of packed earth and gravel with nothing in it but a wellhead. A single narrow gate with a portcullis breaks the wall, with a small guard box beside it, and one squat square tower rises at a corner of the wall to overlook the yard. The whole thing reads as heavy, closed and grim: no windows, no decoration, no greenery.
```

## Variante B — prigione a L

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Prison built as two windowless stone blocks meeting at a right angle, steep slate roofs without openings, enclosing an L-shaped bare yard on two sides. A high stone wall with a parapet walkway closes the other two sides, and an inner cross wall splits the yard into two separate pens of packed earth. One narrow gate with a guard box, one squat corner tower. Nothing green, nothing decorated.
```

## Variante C — prigione bassa e interrata

```text
SUBJECT: Prison as a long, low, half-sunken stone block under a barrel-vaulted roof of grey slabs, with only a line of narrow grated vents along its ridge. A thick stone wall encloses a bare gravel yard around it, with a wellhead, a whipping post and a stack of firewood against the wall. A single heavy gate with an iron grille, flanked by two short squat towers. Everything grey, weathered and bare.
```

---

## Dopo la generazione

- Scontorna il magenta e ripulisci la frangia colorata sul bordo alfa.
- Rifila, ricentra, margine trasparente del 5% per lato.
- Canvas a **768 × 768 px**.
- Ombra aggiunta in post: offset 4%, sfocatura 2,5%, opacità 45%, colore
  `(22, 16, 10)`, identica su tutto il pacchetto.
- Passa la soppressione del rosso: se il modello ha lasciato tegole rossastre,
  vanno spostate su ocra, altrimenti la prigione si ricolora insieme alle case.
- Salva in **PNG con canale alfa**. Mai WebP.

## Checklist

- [ ] Il tetto non ha nessuna apertura, nessun lucernario, nessun cortile interno
- [ ] Il cortile è chiuso da mura alte su tutti i lati
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Nessun rosso da nessuna parte, tetto compreso
- [ ] La sagoma si riconosce rimpicciolita a 120 px (è uno sprite piccolo)
- [ ] PNG con alfa, non WebP
