import inspect
import sys
import unittest
from dataclasses import FrozenInstanceError, fields, is_dataclass
from pathlib import Path
from typing import get_args


APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

import artifact_semantics
from artifact_semantics import (
    ArtifactFooter,
    ArtifactHeader,
    Callout,
    CompletenessNotice,
    MetricGroup,
    NarrativeBlock,
    RecordCollection,
    SemanticArtifact,
    SemanticComponent,
    StatusSummary,
)


class SemanticContractTests(unittest.TestCase):
    def test_module_has_no_reportlab_or_renderer_native_imports(self):
        source = inspect.getsource(artifact_semantics).lower()
        for forbidden in ("reportlab", "pillow", "pypdf"):
            self.assertNotIn(forbidden, source)

    def test_component_union_is_exactly_the_approved_vocabulary(self):
        self.assertEqual(
            set(get_args(SemanticComponent)),
            {
                ArtifactHeader,
                StatusSummary,
                MetricGroup,
                NarrativeBlock,
                Callout,
                RecordCollection,
                CompletenessNotice,
                ArtifactFooter,
            },
        )

    def test_no_generic_or_record_specific_card_contract_exists(self):
        for name in (
            "Section",
            "RiskCard",
            "IssueCard",
            "DependencyCard",
            "DecisionCard",
            "ActionCard",
        ):
            self.assertFalse(hasattr(artifact_semantics, name))

    def test_all_contract_dataclasses_are_frozen(self):
        contract_types = tuple(
            value
            for value in vars(artifact_semantics).values()
            if isinstance(value, type)
            and value.__module__ == artifact_semantics.__name__
            and is_dataclass(value)
        )
        self.assertTrue(contract_types)
        for contract_type in contract_types:
            self.assertTrue(
                contract_type.__dataclass_params__.frozen,
                contract_type.__name__,
            )

    def test_contract_exposes_no_format_or_layout_fields(self):
        forbidden = {
            "page",
            "pages",
            "page_count",
            "page_break",
            "slide",
            "slides",
            "html",
            "css",
            "coordinate",
            "width",
            "height",
            "font",
            "color",
            "border",
            "path",
            "filename",
            "pdf_metadata",
        }
        for value in vars(artifact_semantics).values():
            if (
                isinstance(value, type)
                and value.__module__ == artifact_semantics.__name__
                and is_dataclass(value)
            ):
                self.assertTrue(forbidden.isdisjoint(field.name for field in fields(value)))

    def test_semantic_artifact_components_contract_is_a_tuple(self):
        annotation = SemanticArtifact.__annotations__["components"]
        self.assertEqual(get_args(annotation)[0], SemanticComponent)
        self.assertIs(get_args(annotation)[1], Ellipsis)


if __name__ == "__main__":
    unittest.main()
