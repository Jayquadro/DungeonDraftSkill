# Dungeondraft Forge (`ddforge`)

Generatore procedurale di mappe `.dungeondraft_map` per Dungeondraft.

Lo stato del progetto e la specifica completa sono in [docs/SPEC.md](docs/SPEC.md).
Il lavoro e tracciato in Backlog.md sotto `backlog/` (milestone M0-M7).

## Stato

Repository in fase di bootstrap (M0). I moduli sotto `src/ddforge/` sono
ancora stub: consultare `docs/SPEC.md` per l'architettura e il piano delle
milestone.

## Installazione (sviluppo)

```bash
pip install -e ".[dev]"
```

## Uso

```bash
ddforge --help
```

I sottocomandi (`generate`, `validate`, `inspect`, `catalog`, `preview`)
sono documentati in `docs/SPEC.md` §8 e vengono implementati milestone per
milestone.

## Test

```bash
pytest -q
```

## Esportare un nuovo template

Documentazione da completare in TASK-39, quando il formato e le procedure
di calibrazione saranno confermate nei gate umani di M1 e M3.
