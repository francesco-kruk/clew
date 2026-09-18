"""Compatibility entry point for Alexandra's APM-installed image-first engine."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

SCRIPT = (Path(__file__).resolve().parents[2] / ".agents" / "skills" /
          "content-ingest" / "scripts" / "ingest.py")


def main() -> int:
    if not SCRIPT.is_file():
        print(
            "Clew content-ingest is not restored. From the Clew clone run "
            "APM 0.28.0: apm install --frozen",
            file=sys.stderr,
        )
        return 1
    previous_argv = sys.argv[:]
    previous_path = sys.path[:]
    try:
        sys.argv[0] = str(SCRIPT)
        sys.path.insert(0, str(SCRIPT.parent))
        runpy.run_path(str(SCRIPT), run_name="__main__")
    except ModuleNotFoundError as exc:
        print(
            f"Missing PDF ingestion dependency ({exc.name}). Run "
            'python -m pip install -r ".agents\\skills\\content-ingest\\requirements.txt". '
            "Normal student course imports do not need PDF dependencies.",
            file=sys.stderr,
        )
        return 1
    finally:
        sys.argv[:] = previous_argv
        sys.path[:] = previous_path
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
