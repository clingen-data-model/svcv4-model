"""Export JSON Schemas from the svcv4_model Pydantic classes.

Writes one schema file per top-level public class into ``schemas/json/``.
The committed schemas are the source of truth for downstream
consumers; CI re-runs this script and fails the build if the
generated output differs from the committed copies, forcing
contributors to regenerate when the model changes.

Run from the repo root:

    uv run python scripts/export_schemas.py
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

import svcv4_model

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas" / "json"


def public_model_classes() -> list[type[BaseModel]]:
    """Return the public Pydantic model classes exported by `svcv4_model`.

    Aliases (e.g. `EvidenceData` → `EvidenceItem`) are deduplicated by
    class identity so each class produces exactly one schema file.
    """
    seen: set[type[BaseModel]] = set()
    classes: list[type[BaseModel]] = []
    for name in svcv4_model.__all__:
        obj = getattr(svcv4_model, name)
        if isinstance(obj, type) and issubclass(obj, BaseModel) and obj not in seen:
            classes.append(obj)
            seen.add(obj)
    return classes


def main() -> None:
    SCHEMAS_DIR.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    for cls in public_model_classes():
        schema = cls.model_json_schema()
        path = SCHEMAS_DIR / f"{cls.__name__}.schema.json"
        path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n")
        written.append(path.relative_to(REPO_ROOT).as_posix())

    print(f"Wrote {len(written)} schema file(s) to {SCHEMAS_DIR.relative_to(REPO_ROOT)}/:")
    for rel in written:
        print(f"  - {rel}")


if __name__ == "__main__":
    main()
