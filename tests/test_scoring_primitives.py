"""Tests for the reference-scorer primitives (non-authoritative)."""

from __future__ import annotations

import pytest

from svcv4_model.case import GeneDiseaseValidity
from svcv4_model.informative import InformativeVariant, VariantClassification
from svcv4_model.mechanism import ExonRelevance, GenccMechanism
from svcv4_model.missense import MissenseInfCategory, MissenseInformativeVariant
from svcv4_model.scoring import ScoreResult
from svcv4_model.scoring.primitives import (
    apply_sm18_multiplier,
    cap,
    hold_combined,
    informative_points,
    missense_informative_points,
    transcript_relevance_points,
)

MOD = GeneDiseaseValidity.MODERATE


def test_cap_clamps_and_passes_none() -> None:
    assert cap(5.0, -8.0, 10.0) == 5.0
    assert cap(-20.0, -8.0, 10.0) == -8.0
    assert cap(99.0, -8.0, 10.0) == 10.0
    assert cap(None, -8.0, 10.0) is None


def test_hold_combined_sums_caps_and_handles_none() -> None:
    assert hold_combined(6.0, 2.0, lo=-8.0, hi=10.0) == 8.0
    assert hold_combined(6.0, 8.0, lo=-8.0, hi=9.0) == 9.0  # capped
    assert hold_combined(6.0, None, lo=-8.0, hi=10.0) == 6.0
    assert hold_combined(None, None, lo=-8.0, hi=10.0) is None


def test_sm18_multiplier_mechanism_and_exon() -> None:
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, ExonRelevance.ALL, MOD) == 6.0
    assert apply_sm18_multiplier(6.0, GenccMechanism.LIKELY, ExonRelevance.ALL, MOD) == 3.0
    assert apply_sm18_multiplier(3.0, GenccMechanism.SUSPECTED, ExonRelevance.ALL, MOD) == 0.75
    assert apply_sm18_multiplier(6.0, GenccMechanism.UNCERTAIN, ExonRelevance.ALL, MOD) == 0.0
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, ExonRelevance.FEW, MOD) == 0.0
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, ExonRelevance.MOST, MOD) == 3.0


def test_sm18_special_case_suspected_most_is_quarter() -> None:
    # Figure-1-pending assumption: keep the Suspected fraction (0.25), NOT 0.125 and NOT 0.0
    assert apply_sm18_multiplier(4.0, GenccMechanism.SUSPECTED, ExonRelevance.MOST, MOD) == 1.0


def test_sm18_only_positive_and_gdv_gate() -> None:
    assert apply_sm18_multiplier(-1.0, GenccMechanism.UNCERTAIN, ExonRelevance.FEW, MOD) == -1.0
    assert apply_sm18_multiplier(0.0, GenccMechanism.ESTABLISHED, ExonRelevance.ALL, MOD) == 0.0
    assert apply_sm18_multiplier(None, GenccMechanism.ESTABLISHED, ExonRelevance.ALL, MOD) is None
    assert (
        apply_sm18_multiplier(
            6.0, GenccMechanism.ESTABLISHED, ExonRelevance.ALL, GeneDiseaseValidity.LIMITED
        )
        == 0.0
    )
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, ExonRelevance.ALL, None) == 0.0
    assert apply_sm18_multiplier(6.0, None, ExonRelevance.ALL, MOD) == 0.0
    assert apply_sm18_multiplier(6.0, GenccMechanism.ESTABLISHED, None, MOD) == 6.0


def _iv(cls: VariantClassification) -> InformativeVariant:
    return InformativeVariant(id="x", classification=cls)


def test_informative_points_tally() -> None:
    p, lp = VariantClassification.PATHOGENIC, VariantClassification.LIKELY_PATHOGENIC
    b, vus = VariantClassification.BENIGN, VariantClassification.VUS
    assert informative_points([_iv(p)]) == 2.0
    assert informative_points([_iv(p), _iv(lp), _iv(lp)]) == 4.0
    assert informative_points([_iv(lp)]) == 1.0
    assert informative_points([_iv(b), _iv(b)]) == -3.0
    assert informative_points([_iv(p), _iv(b)]) == 0.0
    assert informative_points([_iv(vus), _iv(vus)]) == 0.0
    assert informative_points([]) is None
    assert informative_points([InformativeVariant(id="x")]) is None  # classification None


def test_score_result_rejects_authoritative_true() -> None:
    ScoreResult()  # default authoritative=False is fine
    with pytest.raises(ValueError):
        ScoreResult(authoritative=True)


def test_transcript_relevance_positive_scaled_by_exon() -> None:
    assert transcript_relevance_points(4.0, ExonRelevance.ALL) == 4.0
    assert transcript_relevance_points(4.0, ExonRelevance.MOST) == 2.0
    assert transcript_relevance_points(4.0, ExonRelevance.FEW) == 0.0


def test_transcript_relevance_nonpositive_passthrough() -> None:
    assert transcript_relevance_points(-3.0, ExonRelevance.FEW) == -3.0  # skips the step
    assert transcript_relevance_points(0.0, ExonRelevance.ALL) == 0.0
    assert transcript_relevance_points(None, ExonRelevance.ALL) is None


def test_transcript_relevance_none_exon_is_full() -> None:
    assert transcript_relevance_points(4.0, None) == 4.0  # generous default


_MP = VariantClassification.PATHOGENIC
_MLP = VariantClassification.LIKELY_PATHOGENIC
_MB = VariantClassification.BENIGN
_MLB = VariantClassification.LIKELY_BENIGN
_MVUS = VariantClassification.VUS


def _mv(cat: MissenseInfCategory, cls: VariantClassification) -> MissenseInformativeVariant:
    return MissenseInformativeVariant(category=cat, classification=cls)


def test_mis_inf_empty_is_none() -> None:
    assert missense_informative_points([]) is None
    # a VUS (and an off-polarity class) score nothing -> None
    assert missense_informative_points([_mv(MissenseInfCategory.SAME_AA_PATHOGENIC, _MVUS)]) is None
    assert missense_informative_points([_mv(MissenseInfCategory.SAME_AA_PATHOGENIC, _MB)]) is None


def test_mis_inf_cat1_same_aa_pathogenic_doubled() -> None:
    c = MissenseInfCategory.SAME_AA_PATHOGENIC
    assert missense_informative_points([_mv(c, _MP)]) == 4.0
    assert missense_informative_points([_mv(c, _MP), _mv(c, _MP)]) == 6.0
    assert missense_informative_points([_mv(c, _MLP)]) == 2.0
    assert missense_informative_points([_mv(c, _MLP), _mv(c, _MLP)]) == 4.0
    assert missense_informative_points([_mv(c, _MP), _mv(c, _MLP)]) == 6.0


def test_mis_inf_cat2_distinct_aa_pathogenic_standard() -> None:
    c = MissenseInfCategory.DISTINCT_AA_PATHOGENIC
    assert missense_informative_points([_mv(c, _MP)]) == 2.0
    assert missense_informative_points([_mv(c, _MP), _mv(c, _MLP)]) == 3.0


def test_mis_inf_cat3_distinct_aa_benign_standard_negative() -> None:
    c = MissenseInfCategory.DISTINCT_AA_BENIGN
    assert missense_informative_points([_mv(c, _MB)]) == -2.0
    assert missense_informative_points([_mv(c, _MB), _mv(c, _MLB)]) == -3.0


def test_mis_inf_cat4_same_aa_benign_doubled_negative() -> None:
    c = MissenseInfCategory.SAME_AA_BENIGN
    assert missense_informative_points([_mv(c, _MB)]) == -4.0
    assert missense_informative_points([_mv(c, _MLB)]) == -2.0
    assert missense_informative_points([_mv(c, _MLB), _mv(c, _MLB)]) == -4.0
    assert missense_informative_points([_mv(c, _MB), _mv(c, _MLB)]) == -6.0


def test_mis_inf_sums_all_categories_uncapped() -> None:
    # cat1 +4, cat3 -2 -> +2 (uncapped; the caller applies the -8..+8 cap)
    variants = [
        _mv(MissenseInfCategory.SAME_AA_PATHOGENIC, _MP),
        _mv(MissenseInfCategory.DISTINCT_AA_BENIGN, _MB),
    ]
    assert missense_informative_points(variants) == 2.0
