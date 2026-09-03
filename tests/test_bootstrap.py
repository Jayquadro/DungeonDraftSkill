"""Verifica che lo scheletro del pacchetto sia importabile.

Placeholder finche TASK-6..TASK-10 non implementano i moduli veri: da
sostituire con test_godot.py, test_ids.py, ecc. quando quei task partono.
"""

import ddforge
from ddforge.cli import build_parser


def test_package_has_version():
    assert ddforge.__version__


def test_cli_parser_exposes_all_subcommands():
    parser = build_parser()
    assert parser.prog == "ddforge"
    args = parser.parse_args(["validate", "mappa.dungeondraft_map"])
    assert args.command == "validate"
    assert args.file == "mappa.dungeondraft_map"
