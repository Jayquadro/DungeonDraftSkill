# Sprite — Armeria (`nm_armeria.png`)

Sprite dedicato per Gemini Nano Banana.

> **⚠️ Attenzione: questo luogo non esiste ancora nel generatore.** Non c'è
> nessun `LandmarkKind` "armeria" in `src/ddforge/generators/landmarks.py`,
> e non compare in `docs/sprite-luoghi.md`. Lo sprite si può generare fin da
> subito, ma finché il tipo non è aggiunto al generatore nessuna mappa lo
> piazza: l'immagine resta senza un posto dove finire. Prima di mettere
> questo sprite in produzione, apri un task per aggiungere il `LandmarkKind`
> corrispondente e per misurare la dimensione disegnata come è stato fatto
> per l'ospedale in TASK-48.1.

| | |
|---|---|
| nome file | `nm_armeria.png` |
| categoria | **proposta, non misurata**: C3 — botteghe e servizi |
| canvas finale | 512 × 512 px |
| scala | `canvas` — lo sprite riempie il riquadro |
| rosso | **tetto ricolorabile**: i tetti in rosso mattone saturo, nient'altro di rosso |
| dove finisce | ancora nessuno: da definire quando il `LandmarkKind` esisterà |

Canvas e categoria proposti sono quelli di una bottega ordinaria, come il
fabbro o il magazzino: nessuna misura reale esiste ancora. Va distinta dal
**fabbro** (che ha una fucina a cielo aperto e lavora il ferro grezzo):
l'armeria è la bottega che rifinisce e vende armi e armature, non la forgia.

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

PALETTE: earthy natural tones: grey and ochre stone, brown wood, pale plaster, dull metal grey. No neon or acid colours.

ROOFS: paint every roof in a uniform, saturated brick red; this colour is a recolour channel. Nothing else in the image may be saturated red.

CONSISTENCY: this is one asset of a large set seen side by side on the same map. Keep brushwork thickness, texture grain and saturation identical across the set, and render recurring materials (roof tiles, stone, plaster, wood, metal) the same way every time.

SUBJECT: Armourer's workshop: a narrow shopfront with a small display rack of shields and helmets set outside the door, and a walled side yard where a suit of half-finished plate armour stands on a wooden mannequin beside a low anvil and a rack of spear shafts. The roof is plain tile; nothing about the building should look like a working forge with an open furnace, that is the blacksmith's shop.
```

## Variante B — armeria con cortile di prova

Stesso prompt, questa riga `SUBJECT:`:

```text
SUBJECT: Armourer's workshop built around a small fenced yard used for fitting and testing armour, racks of swords and polearms along one wall, a shopfront with two barred display windows showing helmets and shields.
```

## Variante C — armeria con galleria appesa

```text
SUBJECT: Armourer's workshop with an upper-floor gallery reached by an external wooden stair, used to hang chainmail shirts to air, a ground-floor shopfront with a heraldic shield-shaped sign, and a small paved yard stacked with round shields.
```

---

## Dopo la generazione

- Scontorna il magenta e ripulisci la frangia colorata sul bordo alfa.
- Rifila, ricentra, margine trasparente del 5% per lato.
- Canvas a **512 × 512 px** (da confermare quando il luogo avrà una misura reale).
- Ombra aggiunta in post: offset 4%, sfocatura 2,5%, opacità 45%, colore
  `(22, 16, 10)`, identica su tutto il pacchetto.
- Normalizza i tetti al rosso uniforme.
- Salva in **PNG con canale alfa**. Mai WebP.

## Checklist

- [ ] Si distingue dal fabbro: niente fucina a cielo aperto, niente forno
- [ ] Armi e armature visibili sono il segno distintivo
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Fondo magenta piatto, senza ombre proiettate sopra
- [ ] Niente prato o strada intorno: solo la bottega
- [ ] Nessuna ombra portata dipinta dal modello
- [ ] Tetto rosso saturo uniforme; nessun altro rosso saturo
- [ ] PNG con alfa, non WebP
- [ ] Prima di produrre in serie: verificato che esista un `LandmarkKind` per questo luogo
