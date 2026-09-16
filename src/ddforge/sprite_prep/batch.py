"""Passaggio su una cartella intera: ogni file del manifest -> PNG + rapporto."""

from __future__ import annotations

import json
from pathlib import Path

from . import imaging, pipeline
from .imaging import ProcessingError
from .manifest import BY_SOURCE, MANIFEST
from .settings import RedSettings, ScaleSettings, ShadowSettings

RAW_SUFFIXES = {".jpg", ".jpeg", ".png"}


def run_batch(
    input_dir: Path,
    output_dir: Path,
    only: set[str] | None = None,
    scale: ScaleSettings | None = None,
    shadow: ShadowSettings | None = None,
    red: RedSettings | None = None,
) -> dict:
    scale = scale or ScaleSettings()
    shadow = shadow or ShadowSettings()
    red = red or RedSettings()

    jobs = [j for j in MANIFEST if only is None or j.stem in only]
    entries: list[dict] = []

    for job in jobs:
        raw_path = input_dir / job.source
        entry = {
            "source": job.source,
            "output": job.filename,
            "categoria": job.category,
            "rosso": job.red_mode,
        }
        if not raw_path.exists():
            entry["stato"] = "mancante"
            entry["avvisi"] = [f"file non trovato in {input_dir}"]
            entries.append(entry)
            continue
        try:
            raw = pipeline.load_raw(raw_path)
            result = pipeline.process_job(raw, job, scale, shadow, red)
        except ProcessingError as exc:
            entry["stato"] = "errore"
            entry["avvisi"] = [str(exc)]
            entries.append(entry)
            continue

        out_path = output_dir / job.filename
        imaging.save_png(result.image, out_path)
        entry["stato"] = "avvisi" if result.warnings else "ok"
        entry["avvisi"] = result.warnings
        entry["info"] = result.info
        entries.append(entry)

    ignored = sorted(
        p.name
        for p in input_dir.iterdir()
        if p.is_file()
        and p.suffix.lower() in RAW_SUFFIXES
        and p.name not in BY_SOURCE
        and (only is None)  # con --only non ha senso segnalare tutto il resto come ignorato
    )

    report = {
        "input": str(input_dir),
        "output": str(output_dir),
        "sprite": entries,
        "ignorati": ignored,
        "riepilogo": {
            stato: sum(1 for e in entries if e["stato"] == stato)
            for stato in ("ok", "avvisi", "errore", "mancante")
        },
    }
    return report


def write_report(report: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def format_report_text(report: dict) -> str:
    lines = [f"input:  {report['input']}", f"output: {report['output']}", ""]
    for entry in report["sprite"]:
        marker = {"ok": "OK", "avvisi": "AVVISI", "errore": "ERRORE", "mancante": "MANCANTE"}[entry["stato"]]
        lines.append(f"[{marker:>8}] {entry['source']:<45} -> {entry['output']}")
        for warning in entry.get("avvisi", []):
            lines.append(f"             - {warning}")
    if report["ignorati"]:
        lines.append("")
        lines.append("file in input senza voce nel manifest (non elaborati):")
        for name in report["ignorati"]:
            lines.append(f"  - {name}")
    lines.append("")
    riepilogo = report["riepilogo"]
    lines.append(
        f"totale: {sum(riepilogo.values())}  "
        f"ok={riepilogo['ok']} avvisi={riepilogo['avvisi']} "
        f"errore={riepilogo['errore']} mancante={riepilogo['mancante']}"
    )
    return "\n".join(lines)
