"""Reference (non-authoritative) scoring layer for the SVCv4 model.

CSpec is the authoritative scorer. This package mirrors the documented Supplementary-Material
point rules for tests, worked examples, and the practice-variant-set. It is intentionally NOT
re-exported from the top-level ``svcv4_model`` package (so schema generation ignores it).
"""

from svcv4_model.scoring.pfd.frameshift import reference_score_frameshift
from svcv4_model.scoring.pfd.nonsense import reference_score_nonsense
from svcv4_model.scoring.result import ScoreResult

__all__ = ["ScoreResult", "reference_score_frameshift", "reference_score_nonsense"]
