"""Configure a vault, discover a catalog, or import a safe immutable snapshot."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from .importer import catalog, import_course
from .source import DEFAULT_SOURCE, open_source
from .storage import CourseError, configure, vault_path
from .validation import load_validator


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("configure", help="Save an explicit external vault path locally")
    setup.add_argument("--vault", required=True)
    for name in ("list", "import"):
        command = commands.add_parser(name)
        command.add_argument("--source", default=DEFAULT_SOURCE, help="GitHub owner/repository")
        command.add_argument("--source-checkout", type=Path, help="Read committed objects in a local Git checkout")
        command.add_argument("--ref", help="Git ref/commit (remote: main; local: HEAD)")
        if name == "import":
            command.add_argument("course_id")
            command.add_argument("--vault", help="Explicit external vault, overriding local configuration")
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        if arguments.command == "configure":
            result = {"status": "configured", "vault": str(configure(arguments.vault))}
        else:
            vault = vault_path(arguments.vault) if arguments.command == "import" else None
            validator = load_validator()
            with open_source(arguments.source, arguments.ref, arguments.source_checkout) as source:
                if arguments.command == "list":
                    with tempfile.TemporaryDirectory(prefix="clew-catalog-") as temporary:
                        result = {"commit": source.commit, **catalog(source, Path(temporary), validator)}
                else:
                    result = import_course(source, arguments.course_id, vault, validator)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (CourseError, OSError, UnicodeError) as exc:
        print(f"Clew: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
