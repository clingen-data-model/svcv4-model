"""SVCv4 Classification Model — Pydantic data model for the SVCv4 VA-Spec community profile.

This package publishes the **Classification Model** half of the SVCv4
software footprint: the shape of a Variant Pathogenicity Classification
expressed as a VA-Spec `Statement` with its `Proposition`, `EvidenceLine`s,
and `EvidenceItem`s. The Method Model — workflows, scoring rules,
criteria definitions — is **out of scope** and lives in ClinGen CSpec.

The placeholder classes here will evolve into the VA-Spec SVCv4
Community Profile as the SVCv4 Standards and the VA-Spec profile
firm up. See `docs/concepts/` for the conceptual narrative.
"""

from svcv4_model.case import (
    MOI,
    AdditionalVariant,
    Age,
    AgeMatchedPenetrance,
    AgeQualifier,
    AgeUnit,
    Case,
    CaseRelative,
    CaseTesting,
    CompoundHetVariant,
    CoOccurrenceLikelihood,
    Gene,
    GeneDiseaseValidity,
    Phase,
    PhaseConfidence,
    PhenoSeverity,
    PhenoSpecificity,
    Phenotype,
    Sex,
    TriState,
    Workflow,
    WorkflowParameters,
    Zygosity,
)
from svcv4_model.case_control import CaseControlStudyEvidence
from svcv4_model.classification import VariantPathogenicityClassification
from svcv4_model.evidence_item import EvidenceData, EvidenceItem
from svcv4_model.evidence_line import EvidenceLine
from svcv4_model.frameshift import (
    FrameshiftAssessment,
    FrameshiftPredictionOutcome,
    FrameshiftPredictiveEvidence,
)
from svcv4_model.functional import (
    AnimalModelEvidence,
    AnimalModelType,
    FunctionalAssayEvidence,
    MolecularMechanism,
    PhenotypeReplication,
    ProteinAssayType,
    ProteinFunctionalAssay,
)
from svcv4_model.informative import (
    InformativeVariant,
    InformativeVariantsEvidence,
    SimilarityBasis,
    VariantClassification,
)
from svcv4_model.inframe_indel import (
    InframeIndelAssessment,
    InframeIndelBranch,
    InframeIndelPredictiveEvidence,
)
from svcv4_model.inputs import MDE, VBC
from svcv4_model.mechanism import (
    ExonRelevance,
    GenccMechanism,
    ManeStatus,
    MechanismExonRelevanceEvidence,
)
from svcv4_model.method import Method
from svcv4_model.missense import (
    MissenseAminoAcidAssessment,
    MissenseAssessment,
    MissenseInfCategory,
    MissenseInformativeEvidence,
    MissenseInformativeVariant,
    MissensePredictiveEvidence,
    MissensePredictor,
    MissenseSelectedPath,
    MissenseSpliceAssessment,
)
from svcv4_model.nonsense import (
    NonsenseAssessment,
    NonsensePredictionOutcome,
    NonsensePredictiveEvidence,
)
from svcv4_model.pfd import (
    PfdCodeAssessment,
    PfdParentCode,
    PfdPredictiveEvidence,
)
from svcv4_model.population import (
    DaftCalculatorInputs,
    DaftMethod,
    PopulationEvidence,
)
from svcv4_model.proposition import Predicate, Proposition
from svcv4_model.splice import (
    SpliceAssayEvidence,
    SpliceAssayResult,
    SplicePredictionOutcome,
    SplicePredictiveEvidence,
    SplicePredictor,
)
from svcv4_model.statement import Statement

__all__ = [
    "MDE",
    "MOI",
    "VBC",
    "AdditionalVariant",
    "Age",
    "AgeMatchedPenetrance",
    "AgeQualifier",
    "AgeUnit",
    "AnimalModelEvidence",
    "AnimalModelType",
    "Case",
    "CaseControlStudyEvidence",
    "CaseRelative",
    "CaseTesting",
    "CompoundHetVariant",
    "CoOccurrenceLikelihood",
    "DaftCalculatorInputs",
    "DaftMethod",
    "EvidenceData",
    "EvidenceItem",
    "EvidenceLine",
    "ExonRelevance",
    "FrameshiftAssessment",
    "FrameshiftPredictionOutcome",
    "FrameshiftPredictiveEvidence",
    "FunctionalAssayEvidence",
    "GenccMechanism",
    "Gene",
    "GeneDiseaseValidity",
    "InformativeVariant",
    "InformativeVariantsEvidence",
    "InframeIndelAssessment",
    "InframeIndelBranch",
    "InframeIndelPredictiveEvidence",
    "ManeStatus",
    "MechanismExonRelevanceEvidence",
    "Method",
    "MissenseAminoAcidAssessment",
    "MissenseAssessment",
    "MissenseInfCategory",
    "MissenseInformativeEvidence",
    "MissenseInformativeVariant",
    "MissensePredictiveEvidence",
    "MissensePredictor",
    "MissenseSelectedPath",
    "MissenseSpliceAssessment",
    "MolecularMechanism",
    "NonsenseAssessment",
    "NonsensePredictionOutcome",
    "NonsensePredictiveEvidence",
    "PfdCodeAssessment",
    "PfdParentCode",
    "PfdPredictiveEvidence",
    "Phase",
    "PhaseConfidence",
    "Phenotype",
    "PhenoSeverity",
    "PhenoSpecificity",
    "PhenotypeReplication",
    "PopulationEvidence",
    "Predicate",
    "Proposition",
    "ProteinAssayType",
    "ProteinFunctionalAssay",
    "Sex",
    "SimilarityBasis",
    "SpliceAssayEvidence",
    "SpliceAssayResult",
    "SplicePredictionOutcome",
    "SplicePredictiveEvidence",
    "SplicePredictor",
    "Statement",
    "TriState",
    "VariantClassification",
    "VariantPathogenicityClassification",
    "Workflow",
    "WorkflowParameters",
    "Zygosity",
]
