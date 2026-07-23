import ast
import inspect
import sys
import unittest
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

import artifact_design
from artifact_design import (
    ARTIFACT_DESIGN_SYSTEM_NAME,
    ARTIFACT_DESIGN_SYSTEM_VERSION,
    AlternatingRowRole,
    ArtifactDesignError,
    BorderRole,
    ColorRole,
    DEFAULT_ARTIFACT_DESIGN_SYSTEM,
    DensityAdjustment,
    RelativeScale,
    SpacingRole,
    StatusVisualRole,
    SurfaceRole,
    TypographyRole,
    build_artifact_design_system,
    status_visual_role_for_health,
    validate_artifact_design_system,
)
from artifact_semantics import (
    ArtifactFooter,
    ArtifactHeader,
    Callout,
    CompletenessNotice,
    DensityProfile,
    MetricGroup,
    NarrativeBlock,
    RecordCollection,
    SemanticEmphasis,
    StatusSummary,
)
from executive_report import MissingValue, StoredFact


SYSTEM = DEFAULT_ARTIFACT_DESIGN_SYSTEM


class RendererIndependenceTests(unittest.TestCase):
    def test_module_imports_only_renderer_neutral_dependencies(self):
        tree = ast.parse(Path(artifact_design.__file__).read_text())
        imported = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        self.assertTrue(
            imported.isdisjoint(
                {
                    "reportlab",
                    "PIL",
                    "pypdf",
                    "html",
                    "css",
                    "pathlib",
                    "os",
                    "io",
                }
            )
        )

    def test_contract_has_no_format_specific_or_physical_fields(self):
        forbidden_names = {
            "page",
            "pages",
            "page_size",
            "page_margin",
            "slide",
            "slides",
            "coordinate",
            "x",
            "y",
            "point",
            "pixel",
            "inch",
            "centimeter",
            "path",
            "filename",
            "output",
            "pagination",
        }
        contract_types = (
            value
            for value in vars(artifact_design).values()
            if isinstance(value, type)
            and value.__module__ == artifact_design.__name__
            and is_dataclass(value)
        )
        for contract_type in contract_types:
            self.assertTrue(
                forbidden_names.isdisjoint(field.name for field in fields(contract_type)),
                contract_type.__name__,
            )

    def test_no_renderer_font_or_compliance_claims(self):
        source = inspect.getsource(artifact_design).lower()
        for forbidden in (
            "reportlab",
            "postscript",
            ".ttf",
            "font-family",
            "pdf/ua",
            "wcag certification",
            "wcag certified",
        ):
            self.assertNotIn(forbidden, source)


class IdentityVocabularyAndImmutabilityTests(unittest.TestCase):
    def test_identity_is_explicit(self):
        self.assertEqual(
            ARTIFACT_DESIGN_SYSTEM_NAME,
            "TPM Executive Artifact Design System",
        )
        self.assertEqual(ARTIFACT_DESIGN_SYSTEM_VERSION, "1.0")
        self.assertEqual(SYSTEM.name, ARTIFACT_DESIGN_SYSTEM_NAME)
        self.assertEqual(SYSTEM.version, ARTIFACT_DESIGN_SYSTEM_VERSION)

    def test_vocabularies_are_closed(self):
        self.assertEqual(
            tuple(role.value for role in TypographyRole),
            (
                "display",
                "title",
                "heading",
                "subheading",
                "body",
                "body_emphasis",
                "label",
                "caption",
                "metric",
                "monospace_identifier",
            ),
        )
        self.assertEqual(
            tuple(role.value for role in RelativeScale),
            ("xs", "sm", "md", "lg", "xl", "xxl"),
        )
        self.assertEqual(
            tuple(role.value for role in SpacingRole),
            ("none", "xxs", "xs", "sm", "md", "lg", "xl", "xxl"),
        )
        self.assertEqual(len(ColorRole), 15)
        self.assertEqual(
            tuple(role.value for role in SurfaceRole),
            ("canvas", "standard", "raised", "emphasis", "muted", "status"),
        )
        self.assertEqual(
            tuple(role.value for role in BorderRole),
            ("none", "subtle", "standard", "strong", "status"),
        )
        self.assertEqual(
            tuple(role.value for role in StatusVisualRole),
            (
                "positive",
                "caution",
                "negative",
                "neutral",
                "informational",
                "unavailable",
            ),
        )

    def test_design_system_and_nested_tokens_are_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            SYSTEM.name = "changed"
        with self.assertRaises(FrozenInstanceError):
            SYSTEM.typography_tokens[0].hierarchy_level = 99
        with self.assertRaises(TypeError):
            SYSTEM.typography_tokens[0] = SYSTEM.typography_tokens[1]
        self.assertIsInstance(SYSTEM.typography_tokens, tuple)
        self.assertIsInstance(SYSTEM.component_tokens, tuple)

    def test_all_contract_dataclasses_are_frozen(self):
        for value in vars(artifact_design).values():
            if (
                isinstance(value, type)
                and value.__module__ == artifact_design.__name__
                and is_dataclass(value)
            ):
                self.assertTrue(value.__dataclass_params__.frozen, value.__name__)

    def test_repeated_construction_is_deeply_equal(self):
        first = build_artifact_design_system()
        second = build_artifact_design_system()
        self.assertEqual(first, second)
        self.assertIsNot(first, second)


class ComponentAndDensityMappingTests(unittest.TestCase):
    def test_exact_semantic_components_have_mappings(self):
        expected = {
            ArtifactHeader,
            StatusSummary,
            MetricGroup,
            NarrativeBlock,
            Callout,
            RecordCollection,
            CompletenessNotice,
            ArtifactFooter,
        }
        self.assertEqual(
            {token.component_type for token in SYSTEM.component_tokens}, expected
        )
        self.assertFalse(hasattr(artifact_design, "Section"))

    def test_all_semantic_emphasis_values_are_mapped(self):
        self.assertEqual(
            {token.emphasis for token in SYSTEM.emphasis_tokens},
            set(SemanticEmphasis),
        )
        for emphasis in SemanticEmphasis:
            self.assertEqual(SYSTEM.emphasis(emphasis).emphasis, emphasis)

    def test_both_explicit_density_profiles_are_non_adaptive(self):
        self.assertEqual(
            {token.profile for token in SYSTEM.density_tokens},
            set(DensityProfile),
        )
        standard = SYSTEM.density(DensityProfile.EXECUTIVE_STANDARD)
        compact = SYSTEM.density(DensityProfile.EXECUTIVE_COMPACT)
        self.assertEqual(standard.spacing_adjustment, DensityAdjustment.STANDARD)
        self.assertEqual(compact.spacing_adjustment, DensityAdjustment.REDUCED)
        for token in (standard, compact):
            self.assertFalse(token.selects_records)
            self.assertFalse(token.hides_components)
            self.assertFalse(token.automatic)
        density_fields = {field.name for field in fields(type(standard))}
        self.assertTrue(
            density_fields.isdisjoint({"record_count", "text_length", "components"})
        )

    def test_record_collection_design_is_renderer_neutral_and_explicit(self):
        token = SYSTEM.component(RecordCollection)
        self.assertEqual(token.alternating_row_role, AlternatingRowRole.MUTED)
        self.assertEqual(
            token.identifier_typography_role,
            TypographyRole.MONOSPACE_IDENTIFIER,
        )
        self.assertTrue(token.missing_value_text_required)
        self.assertTrue(token.omitted_count_explicit)
        self.assertTrue(token.overdue_status_emphasis)


class StatusAndAccessibilityTests(unittest.TestCase):
    def test_all_status_visual_roles_resolve(self):
        for role in StatusVisualRole:
            token = SYSTEM.status(role)
            self.assertEqual(token.role, role)
            self.assertTrue(token.textual_label_required)
            self.assertTrue(token.non_color_indicator_required)

    def test_health_mapping_preserves_supplied_meaning(self):
        self.assertEqual(
            status_visual_role_for_health(StoredFact("Green", ())),
            StatusVisualRole.POSITIVE,
        )
        self.assertEqual(
            status_visual_role_for_health(StoredFact("Yellow", ())),
            StatusVisualRole.CAUTION,
        )
        self.assertEqual(
            status_visual_role_for_health(StoredFact("Red", ())),
            StatusVisualRole.NEGATIVE,
        )
        self.assertEqual(
            status_visual_role_for_health(MissingValue("not recorded")),
            StatusVisualRole.UNAVAILABLE,
        )
        self.assertEqual(
            status_visual_role_for_health(None), StatusVisualRole.UNAVAILABLE
        )
        with self.assertRaises(ArtifactDesignError):
            status_visual_role_for_health("blue")

    def test_accessibility_contract_is_complete(self):
        requirements = SYSTEM.accessibility
        self.assertFalse(requirements.color_is_only_status_indicator)
        self.assertTrue(requirements.textual_status_labels_required)
        self.assertTrue(requirements.missing_value_text_required)
        self.assertEqual(requirements.normal_text_minimum_contrast_ratio, 4.5)
        self.assertEqual(requirements.large_text_minimum_contrast_ratio, 3.0)
        self.assertTrue(requirements.grayscale_distinguishability_required)
        self.assertTrue(requirements.selectable_text_expected)
        self.assertTrue(requirements.reading_order_follows_component_order)
        self.assertTrue(requirements.evidence_ids_remain_available)
        self.assertTrue(requirements.omitted_counts_remain_explicit)
        self.assertFalse(requirements.decorative_information_may_replace_text)

    def test_grayscale_contract_preserves_all_meaning(self):
        policy = SYSTEM.grayscale
        self.assertTrue(policy.status_understandable_without_color)
        self.assertTrue(policy.status_reinforced_by_text_or_structure)
        self.assertTrue(policy.adjacent_surfaces_distinguishable)
        self.assertFalse(policy.critical_information_may_depend_only_on_hue)
        self.assertTrue(policy.alternating_rows_distinguishable)
        self.assertTrue(policy.callout_importance_distinguishable)


class LookupAndValidationTests(unittest.TestCase):
    def test_all_references_resolve_to_immutable_tokens(self):
        for role in TypographyRole:
            self.assertEqual(SYSTEM.typography(role).role, role)
        for role in SpacingRole:
            self.assertEqual(SYSTEM.spacing(role).role, role)
        for role in ColorRole:
            self.assertEqual(SYSTEM.color(role).role, role)
        for role in SurfaceRole:
            self.assertEqual(SYSTEM.surface(role).role, role)
        for role in BorderRole:
            self.assertEqual(SYSTEM.border(role).role, role)
        token = SYSTEM.typography("body")
        with self.assertRaises(FrozenInstanceError):
            token.hierarchy_level = 10

    def test_invalid_lookups_are_rejected_deterministically(self):
        lookups = (
            (SYSTEM.typography, "invented"),
            (SYSTEM.spacing, "invented"),
            (SYSTEM.color, "invented"),
            (SYSTEM.surface, "invented"),
            (SYSTEM.border, "invented"),
            (SYSTEM.status, "invented"),
            (SYSTEM.emphasis, "invented"),
            (SYSTEM.component, str),
            (SYSTEM.density, "invented"),
        )
        for lookup, value in lookups:
            with self.subTest(lookup=lookup.__name__):
                with self.assertRaises(ArtifactDesignError):
                    lookup(value)

    def test_validation_succeeds_for_default(self):
        self.assertIsNone(validate_artifact_design_system(SYSTEM))

    def test_validation_rejects_incomplete_component_mapping(self):
        invalid = replace(SYSTEM, component_tokens=SYSTEM.component_tokens[:-1])
        with self.assertRaises(ArtifactDesignError):
            validate_artifact_design_system(invalid)

    def test_validation_rejects_malformed_component_entry_with_bounded_error(self):
        invalid = replace(
            SYSTEM,
            component_tokens=("not-a-component-token", *SYSTEM.component_tokens[1:]),
        )
        with self.assertRaises(ArtifactDesignError):
            validate_artifact_design_system(invalid)

    def test_validation_rejects_unresolved_references(self):
        invalid_component = replace(
            SYSTEM.component_tokens[0], primary_typography_role="invented"
        )
        invalid = replace(
            SYSTEM,
            component_tokens=(invalid_component, *SYSTEM.component_tokens[1:]),
        )
        with self.assertRaises(ArtifactDesignError):
            validate_artifact_design_system(invalid)

    def test_validation_rejects_malformed_nested_token_values(self):
        invalid_typography = replace(
            SYSTEM.typography_tokens[0], relative_scale="invented"
        )
        invalid_color = replace(
            SYSTEM.color_tokens[0], canonical_hex="not-a-color"
        )
        invalid_tone = replace(
            SYSTEM.color_tokens[0], grayscale_tone="dark"
        )
        systems = (
            replace(
                SYSTEM,
                typography_tokens=(
                    invalid_typography,
                    *SYSTEM.typography_tokens[1:],
                ),
            ),
            replace(
                SYSTEM,
                color_tokens=(invalid_color, *SYSTEM.color_tokens[1:]),
            ),
            replace(
                SYSTEM,
                color_tokens=(invalid_tone, *SYSTEM.color_tokens[1:]),
            ),
        )
        for invalid in systems:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ArtifactDesignError):
                    validate_artifact_design_system(invalid)

    def test_validation_rejects_non_finite_contrast(self):
        for value in (float("nan"), float("inf"), -float("inf"), True, "4.5"):
            with self.subTest(value=value):
                invalid = replace(
                    SYSTEM,
                    accessibility=replace(
                        SYSTEM.accessibility,
                        normal_text_minimum_contrast_ratio=value,
                    ),
                )
                with self.assertRaises(ArtifactDesignError):
                    validate_artifact_design_system(invalid)

    def test_validation_rejects_unresolved_component_emphasis(self):
        invalid_component = replace(
            SYSTEM.component_tokens[0], semantic_emphasis="invented"
        )
        invalid = replace(
            SYSTEM,
            component_tokens=(invalid_component, *SYSTEM.component_tokens[1:]),
        )
        with self.assertRaises(ArtifactDesignError):
            validate_artifact_design_system(invalid)

    def test_validation_rejects_unresolved_alternating_row_role(self):
        invalid_component = replace(
            SYSTEM.component_tokens[0], alternating_row_role="invented"
        )
        invalid = replace(
            SYSTEM,
            component_tokens=(invalid_component, *SYSTEM.component_tokens[1:]),
        )
        with self.assertRaises(ArtifactDesignError):
            validate_artifact_design_system(invalid)

    def test_validation_rejects_contradictory_component_accessibility(self):
        record_index = next(
            index
            for index, token in enumerate(SYSTEM.component_tokens)
            if token.component_type is RecordCollection
        )
        for changes in (
            {"accessibility_label_required": False},
            {"missing_value_text_required": False},
            {"omitted_count_explicit": False},
            {"overdue_status_emphasis": False},
            {"identifier_typography_role": None},
            {"alternating_row_role": AlternatingRowRole.NONE},
        ):
            with self.subTest(changes=changes):
                tokens = list(SYSTEM.component_tokens)
                tokens[record_index] = replace(tokens[record_index], **changes)
                with self.assertRaises(ArtifactDesignError):
                    validate_artifact_design_system(
                        replace(SYSTEM, component_tokens=tuple(tokens))
                    )

    def test_validation_rejects_non_boolean_component_policy(self):
        for field_name in (
            "uses_status_role",
            "accessibility_label_required",
            "density_aware",
            "missing_value_text_required",
            "omitted_count_explicit",
            "overdue_status_emphasis",
        ):
            with self.subTest(field_name=field_name):
                invalid_component = replace(
                    SYSTEM.component_tokens[0], **{field_name: "false"}
                )
                invalid = replace(
                    SYSTEM,
                    component_tokens=(
                        invalid_component,
                        *SYSTEM.component_tokens[1:],
                    ),
                )
                with self.assertRaises(ArtifactDesignError):
                    validate_artifact_design_system(invalid)

    def test_validation_rejects_duplicate_identities(self):
        invalid = replace(
            SYSTEM,
            spacing_tokens=(
                SYSTEM.spacing_tokens[0],
                SYSTEM.spacing_tokens[0],
                *SYSTEM.spacing_tokens[2:],
            ),
        )
        with self.assertRaises(ArtifactDesignError):
            validate_artifact_design_system(invalid)

    def test_validation_rejects_contradictory_spacing_order(self):
        for order in (-1, 1, True, "0"):
            with self.subTest(order=order):
                invalid_token = replace(SYSTEM.spacing_tokens[0], order=order)
                invalid = replace(
                    SYSTEM,
                    spacing_tokens=(invalid_token, *SYSTEM.spacing_tokens[1:]),
                )
                with self.assertRaises(ArtifactDesignError):
                    validate_artifact_design_system(invalid)

    def test_validation_rejects_automatic_or_content_changing_density(self):
        invalid_density = replace(
            SYSTEM.density_tokens[0],
            automatic=True,
            selects_records=True,
            hides_components=True,
        )
        invalid = replace(
            SYSTEM,
            density_tokens=(invalid_density, SYSTEM.density_tokens[1]),
        )
        with self.assertRaises(ArtifactDesignError):
            validate_artifact_design_system(invalid)

    def test_validation_rejects_unresolved_density_adjustment(self):
        invalid_density = replace(
            SYSTEM.density_tokens[0],
            spacing_adjustment="invented",
            typography_adjustment="invented",
        )
        invalid = replace(
            SYSTEM,
            density_tokens=(invalid_density, SYSTEM.density_tokens[1]),
        )
        with self.assertRaises(ArtifactDesignError):
            validate_artifact_design_system(invalid)


if __name__ == "__main__":
    unittest.main()
