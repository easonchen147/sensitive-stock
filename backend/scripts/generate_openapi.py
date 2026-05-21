from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
backend_root_str = str(BACKEND_ROOT)
if backend_root_str not in sys.path:
    sys.path.insert(0, backend_root_str)

from app.openapi import build_openapi_document  # noqa: E402


def write_openapi_artifact(output_path: Path) -> Path:
    document = build_openapi_document()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the backend OpenAPI artifact.")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "openapi.json",
        help="Output path for the generated OpenAPI JSON document.",
    )
    args = parser.parse_args()

    output_path = write_openapi_artifact(args.output.resolve())
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
