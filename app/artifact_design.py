"""Immutable, renderer-neutral design intent for semantic artifacts."""

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Optional

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
from executive_report import MissingValue


ARTIFACT_DESIGN_SYSTEM_NAME = "TPM Executive Artifact Design System"
ARTIFACT_DESIGN_SYSTEM_VERSION = "1.0"


class ArtifactDesignError(ValueError):
    """Raised when design tokens or design-system definitions are unsupported."""


class RelativeScale(str, Enum):
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "xxl"


class SpacingRole(str, Enum):
    NONE = "none"
    XXS = "xxs"
    XS = "xs"
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"
    XXL = "xxl"


class TypographyRole(str, Enum):
    DISPLAY = "display"
    TITLE = "title"
    HEADING = "heading"
    SUBHEADING = "subheading"
    BODY = "body"
    BODY_EMPHASIS = "body_emphasis"
    LABEL = "label"
    CAPTION = "caption"
    METRIC = "metric"
    MONOSPACE_IDENTIFIER = "monospace_identifier"


class TextEmphasis(str, Enum):
    REGULAR = "regular"
    STRONG = "strong"


class MinimumReadableCategory(str, Enum):
    NORMAL = "normal"
    LARGE = "large"


class UppercasePolicy(str, Enum):
    PRESERVE = "preserve"
    UPPERCASE_SHORT_LABELS = "uppercase_short_labels"


class LetterSpacingCategory(str, Enum):
    NORMAL = "normal"
    COMPACT = "compact"
    OPEN = "open"


class ColorRole(str, Enum):
    CANVAS = "canvas"
    SURFACE = "surface"
    SURFACE_EMPHASIS = "surface_emphasis"
    TEXT_PRIMARY = "text_primary"
    TEXT_SECONDARY = "text_secondary"
    TEXT_INVERSE = "text_inverse"
    BORDER = "border"
    BORDER_EMPHASIS = "border_emphasis"
    ACCENT = "accent"
    STATUS_POSITIVE = "status_positive"
    STATUS_CAUTION = "status_caution"
    STATUS_NEGATIVE = "status_negative"
    STATUS_NEUTRAL = "status_neutral"
    STATUS_INFORMATION = "status_information"
    STATUS_UNAVAILABLE = "status_unavailable"


class GrayscaleTone(str, Enum):
    LIGHTEST = "lightest"
    LIGHT = "light"
    MID = "mid"
    DARK = "dark"
    DARKEST = "darkest"


class SurfaceRole(str, Enum):
    CANVAS = "canvas"
    STANDARD = "standard"
    RAISED = "raised"
    EMPHASIS = "emphasis"
    MUTED = "muted"
    STATUS = "status"


class BorderRole(str, Enum):
    NONE = "none"
    SUBTLE = "subtle"
    STANDARD = "standard"
    STRONG = "strong"
    STATUS = "status"


class StatusVisualRole(str, Enum):
    POSITIVE = "positive"
    CAUTION = "caution"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    INFORMATIONAL = "informational"
    UNAVAILABLE = "unavailable"


class AlternatingRowRole(str, Enum):
    NONE = "none"
    MUTED = "muted"


class DensityAdjustment(str, Enum):
    STANDARD = "standard"
    REDUCED = "reduced"


@dataclass(frozen=True)
class TypographyToken:
    role: TypographyRole
    hierarchy_level: int
    relative_scale: RelativeScale
    emphasis: TextEmphasis
    line_height_ratio: float
    minimum_readable_category: MinimumReadableCategory
    uppercase_policy: UppercasePolicy
    letter_spacing: LetterSpacingCategory


@dataclass(frozen=True)
class SpacingToken:
    role: SpacingRole
    order: int


@dataclass(frozen=True)
class ColorToken:
    role: ColorRole
    canonical_hex: str
    grayscale_tone: GrayscaleTone


@dataclass(frozen=True)
class SurfaceToken:
    role: SurfaceRole
    color_role: ColorRole


@dataclass(frozen=True)
class BorderToken:
    role: BorderRole
    color_role: Optional[ColorRole]


@dataclass(frozen=True)
class StatusVisualToken:
    role: StatusVisualRole
    color_role: ColorRole
    surface_role: SurfaceRole
    border_role: BorderRole
    textual_label_required: bool
    non_color_indicator_required: bool


@dataclass(frozen=True)
class EmphasisDesignToken:
    emphasis: SemanticEmphasis
    typography_role: TypographyRole
    surface_role: SurfaceRole
    border_role: BorderRole
    spacing_role: SpacingRole


@dataclass(frozen=True)
class ComponentDesignToken:
    component_type: type
    primary_typography_role: TypographyRole
    secondary_typography_role: TypographyRole
    semantic_emphasis: SemanticEmphasis
    surface_role: SurfaceRole
    border_role: BorderRole
    internal_spacing: SpacingRole
    external_spacing: SpacingRole
    uses_status_role: bool
    accessibility_label_required: bool
    density_aware: bool
    alternating_row_role: AlternatingRowRole = AlternatingRowRole.NONE
    identifier_typography_role: Optional[TypographyRole] = None
    missing_value_text_required: bool = True
    omitted_count_explicit: bool = False
    overdue_status_emphasis: bool = False


@dataclass(frozen=True)
class DensityDesignToken:
    profile: DensityProfile
    spacing_adjustment: DensityAdjustment
    typography_adjustment: DensityAdjustment
    selects_records: bool = False
    hides_components: bool = False
    automatic: bool = False


@dataclass(frozen=True)
class AccessibilityRequirements:
    color_is_only_status_indicator: bool
    textual_status_labels_required: bool
    missing_value_text_required: bool
    normal_text_minimum_contrast_ratio: float
    large_text_minimum_contrast_ratio: float
    grayscale_distinguishability_required: bool
    selectable_text_expected: bool
    reading_order_follows_component_order: bool
    evidence_ids_remain_available: bool
    omitted_counts_remain_explicit: bool
    decorative_information_may_replace_text: bool


@dataclass(frozen=True)
class GrayscalePolicy:
    status_understandable_without_color: bool
    status_reinforced_by_text_or_structure: bool
    adjacent_surfaces_distinguishable: bool
    critical_information_may_depend_only_on_hue: bool
    alternating_rows_distinguishable: bool
    callout_importance_distinguishable: bool


@dataclass(frozen=True)
class ArtifactDesignSystem:
    name: str
    version: str
    typography_tokens: tuple[TypographyToken, ...]
    spacing_tokens: tuple[SpacingToken, ...]
    color_tokens: tuple[ColorToken, ...]
    surface_tokens: tuple[SurfaceToken, ...]
    border_tokens: tuple[BorderToken, ...]
    status_tokens: tuple[StatusVisualToken, ...]
    emphasis_tokens: tuple[EmphasisDesignToken, ...]
    component_tokens: tuple[ComponentDesignToken, ...]
    density_tokens: tuple[DensityDesignToken, ...]
    accessibility: AccessibilityRequirements
    grayscale: GrayscalePolicy

    def typography(self, role) -> TypographyToken:
        return _lookup_enum(self.typography_tokens, "role", role, TypographyRole)

    def spacing(self, role) -> SpacingToken:
        return _lookup_enum(self.spacing_tokens, "role", role, SpacingRole)

    def color(self, role) -> ColorToken:
        return _lookup_enum(self.color_tokens, "role", role, ColorRole)

    def surface(self, role) -> SurfaceToken:
        return _lookup_enum(self.surface_tokens, "role", role, SurfaceRole)

    def border(self, role) -> BorderToken:
        return _lookup_enum(self.border_tokens, "role", role, BorderRole)

    def status(self, role) -> StatusVisualToken:
        return _lookup_enum(self.status_tokens, "role", role, StatusVisualRole)

    def emphasis(self, value) -> EmphasisDesignToken:
        return _lookup_enum(
            self.emphasis_tokens, "emphasis", value, SemanticEmphasis
        )

    def component(self, component_type) -> ComponentDesignToken:
        if not isinstance(component_type, type):
            component_type = type(component_type)
        for token in self.component_tokens:
            if token.component_type is component_type:
                return token
        raise ArtifactDesignError("Unsupported semantic component design role.")

    def density(self, profile) -> DensityDesignToken:
        return _lookup_enum(self.density_tokens, "profile", profile, DensityProfile)


def _lookup_enum(tokens, attribute, requested, enum_type):
    try:
        key = requested if isinstance(requested, enum_type) else enum_type(requested)
    except (TypeError, ValueError) as error:
        raise ArtifactDesignError(f"Unsupported {enum_type.__name__} token.") from error
    for token in tokens:
        if getattr(token, attribute) is key:
            return token
    raise ArtifactDesignError(f"Unsupported {enum_type.__name__} token.")


def status_visual_role_for_health(health) -> StatusVisualRole:
    """Map supplied Program health meaning without deriving or reclassifying it."""
    if health is None or isinstance(health, MissingValue):
        return StatusVisualRole.UNAVAILABLE
    value = getattr(health, "value", health)
    if value is None:
        return StatusVisualRole.UNAVAILABLE
    if not isinstance(value, str):
        raise ArtifactDesignError("Unsupported health status.")
    normalized = value.strip().lower()
    mapping = {
        "green": StatusVisualRole.POSITIVE,
        "yellow": StatusVisualRole.CAUTION,
        "red": StatusVisualRole.NEGATIVE,
    }
    try:
        return mapping[normalized]
    except KeyError as error:
        raise ArtifactDesignError("Unsupported health status.") from error


def build_artifact_design_system() -> ArtifactDesignSystem:
    """Construct the approved deterministic design system."""
    system = ArtifactDesignSystem(
        name=ARTIFACT_DESIGN_SYSTEM_NAME,
        version=ARTIFACT_DESIGN_SYSTEM_VERSION,
        typography_tokens=_typography_tokens(),
        spacing_tokens=tuple(
            SpacingToken(role=role, order=index)
            for index, role in enumerate(SpacingRole)
        ),
        color_tokens=_color_tokens(),
        surface_tokens=(
            SurfaceToken(SurfaceRole.CANVAS, ColorRole.CANVAS),
            SurfaceToken(SurfaceRole.STANDARD, ColorRole.SURFACE),
            SurfaceToken(SurfaceRole.RAISED, ColorRole.SURFACE),
            SurfaceToken(SurfaceRole.EMPHASIS, ColorRole.SURFACE_EMPHASIS),
            SurfaceToken(SurfaceRole.MUTED, ColorRole.SURFACE_EMPHASIS),
            SurfaceToken(SurfaceRole.STATUS, ColorRole.SURFACE),
        ),
        border_tokens=(
            BorderToken(BorderRole.NONE, None),
            BorderToken(BorderRole.SUBTLE, ColorRole.BORDER),
            BorderToken(BorderRole.STANDARD, ColorRole.BORDER),
            BorderToken(BorderRole.STRONG, ColorRole.BORDER_EMPHASIS),
            BorderToken(BorderRole.STATUS, ColorRole.BORDER_EMPHASIS),
        ),
        status_tokens=_status_tokens(),
        emphasis_tokens=(
            EmphasisDesignToken(
                SemanticEmphasis.PRIMARY,
                TypographyRole.HEADING,
                SurfaceRole.EMPHASIS,
                BorderRole.STRONG,
                SpacingRole.LG,
            ),
            EmphasisDesignToken(
                SemanticEmphasis.STANDARD,
                TypographyRole.BODY,
                SurfaceRole.STANDARD,
                BorderRole.STANDARD,
                SpacingRole.MD,
            ),
            EmphasisDesignToken(
                SemanticEmphasis.SUPPORTING,
                TypographyRole.CAPTION,
                SurfaceRole.MUTED,
                BorderRole.SUBTLE,
                SpacingRole.SM,
            ),
        ),
        component_tokens=_component_tokens(),
        density_tokens=(
            DensityDesignToken(
                DensityProfile.EXECUTIVE_STANDARD,
                DensityAdjustment.STANDARD,
                DensityAdjustment.STANDARD,
            ),
            DensityDesignToken(
                DensityProfile.EXECUTIVE_COMPACT,
                DensityAdjustment.REDUCED,
                DensityAdjustment.REDUCED,
            ),
        ),
        accessibility=AccessibilityRequirements(
            color_is_only_status_indicator=False,
            textual_status_labels_required=True,
            missing_value_text_required=True,
            normal_text_minimum_contrast_ratio=4.5,
            large_text_minimum_contrast_ratio=3.0,
            grayscale_distinguishability_required=True,
            selectable_text_expected=True,
            reading_order_follows_component_order=True,
            evidence_ids_remain_available=True,
            omitted_counts_remain_explicit=True,
            decorative_information_may_replace_text=False,
        ),
        grayscale=GrayscalePolicy(
            status_understandable_without_color=True,
            status_reinforced_by_text_or_structure=True,
            adjacent_surfaces_distinguishable=True,
            critical_information_may_depend_only_on_hue=False,
            alternating_rows_distinguishable=True,
            callout_importance_distinguishable=True,
        ),
    )
    validate_artifact_design_system(system)
    return system


def _typography_tokens():
    definitions = (
        (TypographyRole.DISPLAY, 1, RelativeScale.XXL, TextEmphasis.STRONG, 1.15, MinimumReadableCategory.LARGE, UppercasePolicy.PRESERVE, LetterSpacingCategory.COMPACT),
        (TypographyRole.TITLE, 2, RelativeScale.XL, TextEmphasis.STRONG, 1.2, MinimumReadableCategory.LARGE, UppercasePolicy.PRESERVE, LetterSpacingCategory.COMPACT),
        (TypographyRole.HEADING, 3, RelativeScale.LG, TextEmphasis.STRONG, 1.25, MinimumReadableCategory.LARGE, UppercasePolicy.PRESERVE, LetterSpacingCategory.NORMAL),
        (TypographyRole.SUBHEADING, 4, RelativeScale.MD, TextEmphasis.STRONG, 1.3, MinimumReadableCategory.NORMAL, UppercasePolicy.PRESERVE, LetterSpacingCategory.NORMAL),
        (TypographyRole.BODY, 5, RelativeScale.MD, TextEmphasis.REGULAR, 1.45, MinimumReadableCategory.NORMAL, UppercasePolicy.PRESERVE, LetterSpacingCategory.NORMAL),
        (TypographyRole.BODY_EMPHASIS, 5, RelativeScale.MD, TextEmphasis.STRONG, 1.45, MinimumReadableCategory.NORMAL, UppercasePolicy.PRESERVE, LetterSpacingCategory.NORMAL),
        (TypographyRole.LABEL, 6, RelativeScale.SM, TextEmphasis.STRONG, 1.3, MinimumReadableCategory.NORMAL, UppercasePolicy.UPPERCASE_SHORT_LABELS, LetterSpacingCategory.OPEN),
        (TypographyRole.CAPTION, 7, RelativeScale.XS, TextEmphasis.REGULAR, 1.35, MinimumReadableCategory.NORMAL, UppercasePolicy.PRESERVE, LetterSpacingCategory.NORMAL),
        (TypographyRole.METRIC, 3, RelativeScale.XL, TextEmphasis.STRONG, 1.15, MinimumReadableCategory.LARGE, UppercasePolicy.PRESERVE, LetterSpacingCategory.COMPACT),
        (TypographyRole.MONOSPACE_IDENTIFIER, 7, RelativeScale.XS, TextEmphasis.REGULAR, 1.35, MinimumReadableCategory.NORMAL, UppercasePolicy.PRESERVE, LetterSpacingCategory.NORMAL),
    )
    return tuple(TypographyToken(*definition) for definition in definitions)


def _color_tokens():
    definitions = (
        (ColorRole.CANVAS, "#FFFFFF", GrayscaleTone.LIGHTEST),
        (ColorRole.SURFACE, "#F8FAFC", GrayscaleTone.LIGHTEST),
        (ColorRole.SURFACE_EMPHASIS, "#E8EEF5", GrayscaleTone.LIGHT),
        (ColorRole.TEXT_PRIMARY, "#17212B", GrayscaleTone.DARKEST),
        (ColorRole.TEXT_SECONDARY, "#4B5B6B", GrayscaleTone.DARK),
        (ColorRole.TEXT_INVERSE, "#FFFFFF", GrayscaleTone.LIGHTEST),
        (ColorRole.BORDER, "#A8B3BF", GrayscaleTone.MID),
        (ColorRole.BORDER_EMPHASIS, "#526273", GrayscaleTone.DARK),
        (ColorRole.ACCENT, "#174A7E", GrayscaleTone.DARK),
        (ColorRole.STATUS_POSITIVE, "#246B45", GrayscaleTone.DARK),
        (ColorRole.STATUS_CAUTION, "#8A5A00", GrayscaleTone.DARK),
        (ColorRole.STATUS_NEGATIVE, "#A1262D", GrayscaleTone.DARK),
        (ColorRole.STATUS_NEUTRAL, "#5C6773", GrayscaleTone.DARK),
        (ColorRole.STATUS_INFORMATION, "#245B8A", GrayscaleTone.DARK),
        (ColorRole.STATUS_UNAVAILABLE, "#6B7280", GrayscaleTone.DARK),
    )
    return tuple(ColorToken(*definition) for definition in definitions)


def _status_tokens():
    colors = {
        StatusVisualRole.POSITIVE: ColorRole.STATUS_POSITIVE,
        StatusVisualRole.CAUTION: ColorRole.STATUS_CAUTION,
        StatusVisualRole.NEGATIVE: ColorRole.STATUS_NEGATIVE,
        StatusVisualRole.NEUTRAL: ColorRole.STATUS_NEUTRAL,
        StatusVisualRole.INFORMATIONAL: ColorRole.STATUS_INFORMATION,
        StatusVisualRole.UNAVAILABLE: ColorRole.STATUS_UNAVAILABLE,
    }
    return tuple(
        StatusVisualToken(
            role,
            colors[role],
            SurfaceRole.STATUS,
            BorderRole.STATUS,
            textual_label_required=True,
            non_color_indicator_required=True,
        )
        for role in StatusVisualRole
    )


def _component_tokens():
    return (
        ComponentDesignToken(ArtifactHeader, TypographyRole.DISPLAY, TypographyRole.BODY, SemanticEmphasis.PRIMARY, SurfaceRole.CANVAS, BorderRole.STRONG, SpacingRole.LG, SpacingRole.XL, False, True, True),
        ComponentDesignToken(StatusSummary, TypographyRole.METRIC, TypographyRole.LABEL, SemanticEmphasis.PRIMARY, SurfaceRole.EMPHASIS, BorderRole.STATUS, SpacingRole.MD, SpacingRole.LG, True, True, True),
        ComponentDesignToken(MetricGroup, TypographyRole.METRIC, TypographyRole.LABEL, SemanticEmphasis.STANDARD, SurfaceRole.RAISED, BorderRole.STANDARD, SpacingRole.MD, SpacingRole.LG, True, True, True),
        ComponentDesignToken(NarrativeBlock, TypographyRole.HEADING, TypographyRole.BODY, SemanticEmphasis.STANDARD, SurfaceRole.STANDARD, BorderRole.NONE, SpacingRole.MD, SpacingRole.LG, False, True, True),
        ComponentDesignToken(Callout, TypographyRole.HEADING, TypographyRole.BODY_EMPHASIS, SemanticEmphasis.PRIMARY, SurfaceRole.EMPHASIS, BorderRole.STRONG, SpacingRole.LG, SpacingRole.XL, True, True, True),
        ComponentDesignToken(RecordCollection, TypographyRole.HEADING, TypographyRole.BODY, SemanticEmphasis.STANDARD, SurfaceRole.STANDARD, BorderRole.STANDARD, SpacingRole.SM, SpacingRole.LG, True, True, True, AlternatingRowRole.MUTED, TypographyRole.MONOSPACE_IDENTIFIER, True, True, True),
        ComponentDesignToken(CompletenessNotice, TypographyRole.SUBHEADING, TypographyRole.CAPTION, SemanticEmphasis.SUPPORTING, SurfaceRole.MUTED, BorderRole.SUBTLE, SpacingRole.SM, SpacingRole.MD, True, True, True),
        ComponentDesignToken(ArtifactFooter, TypographyRole.CAPTION, TypographyRole.CAPTION, SemanticEmphasis.SUPPORTING, SurfaceRole.CANVAS, BorderRole.SUBTLE, SpacingRole.SM, SpacingRole.MD, False, True, False),
    )


def validate_artifact_design_system(system: ArtifactDesignSystem) -> None:
    """Reject incomplete, duplicate, unresolved, or contradictory design systems."""
    if not isinstance(system, ArtifactDesignSystem):
        raise ArtifactDesignError("Design system contract is invalid.")
    if system.name != ARTIFACT_DESIGN_SYSTEM_NAME or system.version != ARTIFACT_DESIGN_SYSTEM_VERSION:
        raise ArtifactDesignError("Design system identity is unsupported.")

    registries = (
        system.typography_tokens,
        system.spacing_tokens,
        system.color_tokens,
        system.surface_tokens,
        system.border_tokens,
        system.status_tokens,
        system.emphasis_tokens,
        system.component_tokens,
        system.density_tokens,
    )
    if any(not isinstance(registry, tuple) for registry in registries):
        raise ArtifactDesignError("Design token registries must be immutable tuples.")
    _validate_complete_unique(system.typography_tokens, "role", TypographyRole, TypographyToken)
    _validate_complete_unique(system.spacing_tokens, "role", SpacingRole, SpacingToken)
    _validate_complete_unique(system.color_tokens, "role", ColorRole, ColorToken)
    _validate_complete_unique(system.surface_tokens, "role", SurfaceRole, SurfaceToken)
    _validate_complete_unique(system.border_tokens, "role", BorderRole, BorderToken)
    _validate_complete_unique(system.status_tokens, "role", StatusVisualRole, StatusVisualToken)
    _validate_complete_unique(system.emphasis_tokens, "emphasis", SemanticEmphasis, EmphasisDesignToken)
    _validate_complete_unique(system.density_tokens, "profile", DensityProfile, DensityDesignToken)
    for token in system.typography_tokens:
        if (
            not isinstance(token.relative_scale, RelativeScale)
            or not isinstance(token.emphasis, TextEmphasis)
            or not isinstance(token.minimum_readable_category, MinimumReadableCategory)
            or not isinstance(token.uppercase_policy, UppercasePolicy)
            or not isinstance(token.letter_spacing, LetterSpacingCategory)
            or not isinstance(token.hierarchy_level, int)
            or isinstance(token.hierarchy_level, bool)
            or token.hierarchy_level < 1
            or not _is_finite_number(token.line_height_ratio)
            or token.line_height_ratio < 1.0
        ):
            raise ArtifactDesignError("Typography token definition is invalid.")
    hexadecimal = frozenset("0123456789ABCDEF")
    for token in system.color_tokens:
        if (
            not isinstance(token.grayscale_tone, GrayscaleTone)
            or not isinstance(token.canonical_hex, str)
            or len(token.canonical_hex) != 7
            or token.canonical_hex[0] != "#"
            or any(character not in hexadecimal for character in token.canonical_hex[1:])
        ):
            raise ArtifactDesignError("Color token definition is invalid.")
    expected_spacing_order = {
        role: index for index, role in enumerate(SpacingRole)
    }
    if any(
        not isinstance(token.order, int)
        or isinstance(token.order, bool)
        or token.order != expected_spacing_order[token.role]
        for token in system.spacing_tokens
    ):
        raise ArtifactDesignError("Spacing token order is contradictory.")

    expected_components = {
        ArtifactHeader,
        StatusSummary,
        MetricGroup,
        NarrativeBlock,
        Callout,
        RecordCollection,
        CompletenessNotice,
        ArtifactFooter,
    }
    if any(
        not isinstance(token, ComponentDesignToken)
        for token in system.component_tokens
    ):
        raise ArtifactDesignError("Semantic component token definition is invalid.")
    component_types = tuple(token.component_type for token in system.component_tokens)
    if len(component_types) != len(set(component_types)) or set(component_types) != expected_components:
        raise ArtifactDesignError("Semantic component design mappings are incomplete.")

    typography = set(TypographyRole)
    spacing = set(SpacingRole)
    colors = set(ColorRole)
    surfaces = set(SurfaceRole)
    borders = set(BorderRole)
    for token in system.surface_tokens:
        if not isinstance(token.color_role, ColorRole) or token.color_role not in colors:
            raise ArtifactDesignError("Surface color reference is unresolved.")
    for token in system.border_tokens:
        if token.color_role is not None and (
            not isinstance(token.color_role, ColorRole)
            or token.color_role not in colors
        ):
            raise ArtifactDesignError("Border color reference is unresolved.")
    for token in system.status_tokens:
        if (
            not isinstance(token.color_role, ColorRole)
            or not isinstance(token.surface_role, SurfaceRole)
            or not isinstance(token.border_role, BorderRole)
            or token.color_role not in colors
            or token.surface_role not in surfaces
            or token.border_role not in borders
        ):
            raise ArtifactDesignError("Status design reference is unresolved.")
        if (
            not _all_booleans(
                token.textual_label_required,
                token.non_color_indicator_required,
            )
            or not token.textual_label_required
            or not token.non_color_indicator_required
        ):
            raise ArtifactDesignError("Status meaning cannot depend only on color.")
    for token in system.emphasis_tokens:
        if (
            not isinstance(token.typography_role, TypographyRole)
            or not isinstance(token.spacing_role, SpacingRole)
            or not isinstance(token.surface_role, SurfaceRole)
            or not isinstance(token.border_role, BorderRole)
            or token.typography_role not in typography
            or token.spacing_role not in spacing
            or token.surface_role not in surfaces
            or token.border_role not in borders
        ):
            raise ArtifactDesignError("Emphasis design reference is unresolved.")
    for token in system.component_tokens:
        if not isinstance(token.semantic_emphasis, SemanticEmphasis):
            raise ArtifactDesignError("Component emphasis reference is unresolved.")
        if not isinstance(token.alternating_row_role, AlternatingRowRole):
            raise ArtifactDesignError(
                "Component alternating-row reference is unresolved."
            )
        if not _all_booleans(
            token.uses_status_role,
            token.accessibility_label_required,
            token.density_aware,
            token.missing_value_text_required,
            token.omitted_count_explicit,
            token.overdue_status_emphasis,
        ):
            raise ArtifactDesignError("Component policy values must be boolean.")
        if not token.accessibility_label_required or not token.missing_value_text_required:
            raise ArtifactDesignError(
                "Component accessibility requirements are contradictory."
            )
        if (
            not isinstance(token.primary_typography_role, TypographyRole)
            or not isinstance(token.secondary_typography_role, TypographyRole)
            or token.primary_typography_role not in typography
            or token.secondary_typography_role not in typography
        ):
            raise ArtifactDesignError("Component typography reference is unresolved.")
        if (
            not isinstance(token.internal_spacing, SpacingRole)
            or not isinstance(token.external_spacing, SpacingRole)
            or token.internal_spacing not in spacing
            or token.external_spacing not in spacing
        ):
            raise ArtifactDesignError("Component spacing reference is unresolved.")
        if (
            not isinstance(token.surface_role, SurfaceRole)
            or not isinstance(token.border_role, BorderRole)
            or token.surface_role not in surfaces
            or token.border_role not in borders
        ):
            raise ArtifactDesignError("Component design reference is unresolved.")
        if token.identifier_typography_role is not None and (
            not isinstance(token.identifier_typography_role, TypographyRole)
            or token.identifier_typography_role not in typography
        ):
            raise ArtifactDesignError("Component identifier reference is unresolved.")
        if token.component_type is RecordCollection and (
            token.alternating_row_role is not AlternatingRowRole.MUTED
            or token.identifier_typography_role is None
            or not token.omitted_count_explicit
            or not token.overdue_status_emphasis
        ):
            raise ArtifactDesignError(
                "Record collection design requirements are incomplete."
            )

    requirements = system.accessibility
    if not isinstance(requirements, AccessibilityRequirements):
        raise ArtifactDesignError("Accessibility requirements are invalid.")
    if not _all_booleans(
        requirements.color_is_only_status_indicator,
        requirements.textual_status_labels_required,
        requirements.missing_value_text_required,
        requirements.grayscale_distinguishability_required,
        requirements.selectable_text_expected,
        requirements.reading_order_follows_component_order,
        requirements.evidence_ids_remain_available,
        requirements.omitted_counts_remain_explicit,
        requirements.decorative_information_may_replace_text,
    ):
        raise ArtifactDesignError("Accessibility policy values must be boolean.")
    if (
        requirements.color_is_only_status_indicator
        or not requirements.textual_status_labels_required
        or not requirements.missing_value_text_required
        or not _is_finite_number(requirements.normal_text_minimum_contrast_ratio)
        or not _is_finite_number(requirements.large_text_minimum_contrast_ratio)
        or requirements.normal_text_minimum_contrast_ratio < 4.5
        or requirements.large_text_minimum_contrast_ratio < 3.0
        or requirements.normal_text_minimum_contrast_ratio < requirements.large_text_minimum_contrast_ratio
        or not requirements.grayscale_distinguishability_required
        or not requirements.selectable_text_expected
        or not requirements.reading_order_follows_component_order
        or not requirements.evidence_ids_remain_available
        or not requirements.omitted_counts_remain_explicit
        or requirements.decorative_information_may_replace_text
    ):
        raise ArtifactDesignError("Accessibility requirements are incomplete or contradictory.")
    grayscale = system.grayscale
    if not isinstance(grayscale, GrayscalePolicy):
        raise ArtifactDesignError("Grayscale requirements are invalid.")
    if not _all_booleans(
        grayscale.status_understandable_without_color,
        grayscale.status_reinforced_by_text_or_structure,
        grayscale.adjacent_surfaces_distinguishable,
        grayscale.critical_information_may_depend_only_on_hue,
        grayscale.alternating_rows_distinguishable,
        grayscale.callout_importance_distinguishable,
    ):
        raise ArtifactDesignError("Grayscale policy values must be boolean.")
    if (
        not grayscale.status_understandable_without_color
        or not grayscale.status_reinforced_by_text_or_structure
        or not grayscale.adjacent_surfaces_distinguishable
        or grayscale.critical_information_may_depend_only_on_hue
        or not grayscale.alternating_rows_distinguishable
        or not grayscale.callout_importance_distinguishable
    ):
        raise ArtifactDesignError("Grayscale requirements are incomplete or contradictory.")
    for token in system.density_tokens:
        if not _all_booleans(
            token.selects_records,
            token.hides_components,
            token.automatic,
        ):
            raise ArtifactDesignError("Density policy values must be boolean.")
        if (
            not isinstance(token.spacing_adjustment, DensityAdjustment)
            or not isinstance(token.typography_adjustment, DensityAdjustment)
        ):
            raise ArtifactDesignError("Density adjustment reference is unresolved.")
        if token.selects_records or token.hides_components or token.automatic:
            raise ArtifactDesignError("Density mappings may only adjust relative design intent.")


def _validate_complete_unique(tokens, attribute, enum_type, token_type):
    if any(
        not isinstance(token, token_type)
        or not isinstance(getattr(token, attribute), enum_type)
        for token in tokens
    ):
        raise ArtifactDesignError(f"{enum_type.__name__} token definition is invalid.")
    identities = tuple(getattr(token, attribute) for token in tokens)
    if len(identities) != len(set(identities)) or set(identities) != set(enum_type):
        raise ArtifactDesignError(f"{enum_type.__name__} tokens are incomplete or duplicated.")


def _is_finite_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(value)
    )


def _all_booleans(*values):
    return all(isinstance(value, bool) for value in values)


DEFAULT_ARTIFACT_DESIGN_SYSTEM = build_artifact_design_system()
