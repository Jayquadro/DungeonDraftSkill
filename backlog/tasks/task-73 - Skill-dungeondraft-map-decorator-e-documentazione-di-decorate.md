---
id: TASK-73
title: Skill dungeondraft-map-decorator e documentazione di decorate
status: To Do
assignee: []
created_date: '2026-10-04 17:31'
updated_date: '2026-10-04 17:43'
labels: []
milestone: m-10
dependencies:
  - TASK-69
references:
  - skills/generator/SKILL.md
  - skills/generator/references/styles.md
  - docs/SPEC.md
  - README.md
documentation:
  - docs/SPEC-decorate.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Seconda skill Claude del progetto, in `skills/decorator/` accanto a `skills/generator/` (la skill di generazione, gia spostata li da `skill/`): traduce una richiesta come "rendi la cripta piu lugubre, abbandonata da secoli" in un'invocazione di `ddforge decorate`, con il workflow "propone, poi applica" di docs/SPEC-decorate.md §9: individua la mappa e verifica il sidecar, guarda (inspect + preview), sceglie tema (sei: abbandonato, abitato, lugubre, naturale, arcano, festivo) e intensita, propone con `--dry-run --json` riassunto per zona in linguaggio naturale, traduce le correzioni dell'utente in override `--zone/--add/...`, applica, legge l'esito senza mai patchare il JSON, consegna con preview prima/dopo (che con TASK-75 mostra anche luci e terreno).

Gestione della mappa ritoccata a mano: decorate rifiuta di default; la skill spiega il motivo e, se l'utente conferma, rilancia con `--allow-modified`.

Include l'allineamento della documentazione: SPEC.md §1.3 oggi esclude l'editing di mappe esistenti e va aggiornata rimandando a docs/SPEC-decorate.md e a decision-3 (da portare ad accepted); README con la sezione `decorate`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Esiste SKILL.md con frontmatter name/description che la attiva su richieste di abbellimento di una mappa esistente e non su richieste di generazione
- [ ] #2 references/themes.md descrive temi, intensita, ruoli di zona e alias utili per --add; references/examples.md ha un esempio per ogni tipo di mappa
- [ ] #3 La skill propone sempre il piano prima di applicarlo e traduce le correzioni in override, mai in modifiche al file
- [ ] #4 La skill gestisce i casi d'errore di decorate (sidecar mancante, mappa modificata, gia abbellita) spiegando all'utente cosa fare
- [ ] #5 SPEC.md §1.3 e README sono aggiornati e decision-3 e in stato accepted
- [ ] #6 Una prova end-to-end della skill su una mappa dungeon e una city e documentata nella nota di chiusura
- [ ] #7 La skill vive in `skills/decorator/` e, su una mappa ritoccata a mano, chiede conferma all'utente prima di usare `--allow-modified`
<!-- AC:END -->
