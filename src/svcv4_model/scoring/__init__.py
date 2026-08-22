"""Reference (non-authoritative) scoring layer for the SVCv4 model.

CSpec is the authoritative scorer. This package mirrors the documented Supplementary-Material
point rules for tests, worked examples, and the practice-variant-set. It is intentionally NOT
re-exported from the top-level ``svcv4_model`` package (so schema generation ignores it).
"""

from svcv4_model.scoring.pfd.canonical_splice import reference_score_canonical_splice
from svcv4_model.scoring.pfd.exon_deletion import reference_score_exon_deletion
from svcv4_model.scoring.pfd.exon_duplication import reference_score_exon_duplication
from svcv4_model.scoring.pfd.frameshift import reference_score_frameshift
from svcv4_model.scoring.pfd.nonsense import reference_score_nonsense
from svcv4_model.scoring.pfd.start_lost import reference_score_start_lost
from svcv4_model.scoring.pfd.stop_lost import reference_score_stop_lost
from svcv4_model.scoring.result import ScoreResult

__all__ = [
    "ScoreResult",
    "reference_score_canonical_splice",
    "reference_score_exon_deletion",
    "reference_score_exon_duplication",
    "reference_score_frameshift",
    "reference_score_nonsense",
    "reference_score_start_lost",
    "reference_score_stop_lost",
]
