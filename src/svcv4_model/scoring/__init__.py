"""Reference (non-authoritative) scoring layer for the SVCv4 model.

CSpec is the authoritative scorer. This package mirrors the documented Supplementary-Material
point rules for tests, worked examples, and the practice-variant-set. It is intentionally NOT
re-exported from the top-level ``svcv4_model`` package (so schema generation ignores it).
"""

from svcv4_model.scoring.aggregate import (
    reference_aggregate_loc,
    reference_aggregate_pop,
)
from svcv4_model.scoring.classification import (
    Classification,
    VusSubclass,
    reference_classify,
)
from svcv4_model.scoring.hod.clinical import (
    reference_score_cln_aff_biallelic,
    reference_score_cln_aff_mono,
    reference_score_cln_alt,
    reference_score_cln_ccs,
    reference_score_cln_dnv,
    reference_score_cln_proband,
    reference_score_cln_uaf,
)
from svcv4_model.scoring.hod.locus import reference_score_loc_phe
from svcv4_model.scoring.hod.population import reference_score_population
from svcv4_model.scoring.pfd.canonical_splice import reference_score_canonical_splice
from svcv4_model.scoring.pfd.exon_deletion import reference_score_exon_deletion
from svcv4_model.scoring.pfd.exon_duplication import reference_score_exon_duplication
from svcv4_model.scoring.pfd.frameshift import reference_score_frameshift
from svcv4_model.scoring.pfd.intronic_synonymous import reference_score_intronic_synonymous
from svcv4_model.scoring.pfd.missense import reference_score_missense
from svcv4_model.scoring.pfd.missense_amino_acid import reference_score_missense_amino_acid
from svcv4_model.scoring.pfd.missense_splice import reference_score_missense_splice
from svcv4_model.scoring.pfd.nonsense import reference_score_nonsense
from svcv4_model.scoring.pfd.start_lost import reference_score_start_lost
from svcv4_model.scoring.pfd.stop_lost import reference_score_stop_lost
from svcv4_model.scoring.result import MissenseScoreResult, ScoreResult

__all__ = [
    "Classification",
    "MissenseScoreResult",
    "ScoreResult",
    "VusSubclass",
    "reference_aggregate_loc",
    "reference_aggregate_pop",
    "reference_classify",
    "reference_score_canonical_splice",
    "reference_score_cln_aff_biallelic",
    "reference_score_cln_aff_mono",
    "reference_score_cln_alt",
    "reference_score_cln_ccs",
    "reference_score_cln_dnv",
    "reference_score_cln_proband",
    "reference_score_cln_uaf",
    "reference_score_exon_deletion",
    "reference_score_exon_duplication",
    "reference_score_frameshift",
    "reference_score_intronic_synonymous",
    "reference_score_loc_phe",
    "reference_score_missense",
    "reference_score_missense_amino_acid",
    "reference_score_missense_splice",
    "reference_score_nonsense",
    "reference_score_population",
    "reference_score_start_lost",
    "reference_score_stop_lost",
]
