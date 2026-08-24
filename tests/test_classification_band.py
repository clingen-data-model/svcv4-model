"""Tests for reference_classify (SM 1 classification band, non-authoritative)."""

from __future__ import annotations

from svcv4_model.informative import VariantClassification as VC
from svcv4_model.scoring import Classification, VusSubclass, reference_classify


def test_midband_representatives() -> None:
    assert reference_classify(12.0) == Classification(VC.PATHOGENIC, None)
    assert reference_classify(8.0) == Classification(VC.LIKELY_PATHOGENIC, None)
    assert reference_classify(5.0) == Classification(VC.VUS, VusSubclass.HIGH)
    assert reference_classify(3.0) == Classification(VC.VUS, VusSubclass.MID)
    assert reference_classify(0.0) == Classification(VC.VUS, VusSubclass.LOW)
    assert reference_classify(-2.0) == Classification(VC.LIKELY_BENIGN, None)
    assert reference_classify(-6.0) == Classification(VC.BENIGN, None)


def test_exact_boundaries() -> None:
    assert reference_classify(-4.0) == Classification(VC.BENIGN, None)
    assert reference_classify(-1.0) == Classification(VC.LIKELY_BENIGN, None)
    assert reference_classify(2.0) == Classification(VC.VUS, VusSubclass.MID)
    assert reference_classify(4.0) == Classification(VC.VUS, VusSubclass.HIGH)
    assert reference_classify(6.0) == Classification(VC.LIKELY_PATHOGENIC, None)
    assert reference_classify(10.0) == Classification(VC.PATHOGENIC, None)


def test_across_boundary_neighbours() -> None:
    assert reference_classify(-3.999) == Classification(VC.LIKELY_BENIGN, None)
    assert reference_classify(-0.999) == Classification(VC.VUS, VusSubclass.LOW)
    assert reference_classify(1.999) == Classification(VC.VUS, VusSubclass.LOW)
    assert reference_classify(3.999) == Classification(VC.VUS, VusSubclass.MID)
    assert reference_classify(5.999) == Classification(VC.VUS, VusSubclass.HIGH)
    assert reference_classify(9.999) == Classification(VC.LIKELY_PATHOGENIC, None)


def test_vus_subclass_discipline() -> None:
    for p in (-6.0, -4.0, -2.0, -1.0, 0.0, 2.0, 4.0, 6.0, 10.0, 12.0):
        c = reference_classify(p)
        if c.category == VC.VUS:
            assert c.vus_subclass is not None
        else:
            assert c.vus_subclass is None


def test_namedtuple_ergonomics() -> None:
    cat, sub = reference_classify(3.0)
    assert cat == VC.VUS
    assert sub == VusSubclass.MID
    assert reference_classify(3.0).category == VC.VUS


def test_extremes_not_clamped() -> None:
    assert reference_classify(50.0).category == VC.PATHOGENIC
    assert reference_classify(-50.0).category == VC.BENIGN
