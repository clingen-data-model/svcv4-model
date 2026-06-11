"""Loader for the Case applicability matrix.

The matrix (``schemas/applicability/case_applicability.yaml``) is the single
source of truth for which Case attributes are required/optional/conditional/
not-applicable per CLN workflow, plus the conditional rules. This module reads
it; it deliberately exposes no Pydantic models and is NOT exported from the
package root, so the schema exporter does not pick it up.

This phase loads and serves the matrix as data. Rule *enforcement*
(``validate_case``) is a later phase.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from svcv4_model.case import Workflow

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MATRIX_PATH = REPO_ROOT / "schemas" / "applicability" / "case_applicability.yaml"

#: Legal applicability codes. The token set is {r, o, c, x}; ``c*`` from the
#: source sheet has been collapsed into ``c``.
VALID_CODES: frozenset[str] = frozenset({"r", "o", "c", "x"})


@lru_cache(maxsize=1)
def load_matrix() -> dict[str, dict[str, Any]]:
    """Load and return the applicability matrix keyed by dotted field path."""
    data = yaml.safe_load(MATRIX_PATH.read_text())
    return dict(data)


def field_paths() -> list[str]:
    """Return all dotted field paths in matrix order."""
    return list(load_matrix().keys())


def workflow_codes(workflow: Workflow) -> dict[str, str]:
    """Return ``{field_path: code}`` for a single workflow."""
    return {path: entry["applicability"][workflow.value] for path, entry in load_matrix().items()}
