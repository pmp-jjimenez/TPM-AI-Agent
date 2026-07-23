# ADR 0003: Use a Renderer-Neutral Artifact Design System

- Status: Accepted
- Date: 2026-07-23
- Decision owners: Javier Jiménez, Product Owner; TPM Operating System engineering
- Scope: ART-1.0 Executive Artifact Foundation

## Context

ADR 0002 separates executive-report meaning, semantic artifact composition, and
format-specific rendering. It does not decide how stable visual intent is shared
across renderers. Mapping semantic components directly to concrete ReportLab styles
would make the PDF backend the source of design policy and would force future
PowerPoint or HTML renderers either to duplicate that policy or to depend on PDF
concepts.

Executive artifacts also need accessibility and grayscale requirements before a
renderer chooses colors, type measurements, borders, or layout primitives.

## Decision

Add an immutable `ArtifactDesignSystem` boundary:

```text
ExecutiveReportViewModel
  -> SemanticArtifact
  -> ArtifactDesignSystem
  -> ArtifactRenderer
  -> format-specific output
```

- Keep semantic artifact meaning unchanged. The design system maps semantic roles to
  design intent and does not reclassify Program health, confidence, records, or
  recommendations.
- Use closed relative vocabularies for typography scale, spacing, surfaces, borders,
  status visuals, semantic emphasis, and density adjustments.
- Use a restrained executive palette expressed as immutable canonical hexadecimal
  values and semantic color roles, never renderer-native color objects.
- Map all eight semantic component classes explicitly. Do not add a generic section
  fallback.
- Map already supplied Green, Yellow, and Red health to positive, caution, and
  negative visual roles. Map missing health to unavailable. Reject unsupported health
  rather than inferring a favorable state.
- Require textual status and missing-value meaning, non-color status reinforcement,
  explicit evidence IDs and omitted counts, semantic component reading order,
  selectable text for text-based renderers, minimum 4.5:1 normal-text and 3:1
  large-text contrast, and grayscale-distinguishable status, surfaces, row
  alternation, and callouts.
- Keep density explicit and non-adaptive. Density may adjust relative typography and
  spacing intent but may not inspect content, select records, hide components, or
  paginate.
- Store all registries as immutable tuples of frozen tokens. Lookups reject
  unsupported values, and whole-system validation rejects incomplete, duplicate,
  unresolved, or contradictory definitions.
- Exclude physical measurements, page and slide concepts, coordinates, pagination,
  renderer callbacks, renderer-native objects, font paths, and filesystem output.

Future renderers translate the relative tokens to concrete format-specific
implementations. The design contract does not generate an artifact and makes no
claim of WCAG certification, PDF/UA conformance, tagged-PDF support, or screen-reader
certification.

## Consequences

- PDF and future renderers can share one stable visual policy without sharing layout
  objects or physical measurements.
- Accessibility and grayscale expectations are testable before rendering, while
  rendered-output validation remains required in later increments.
- The palette is operational and deterministic, but each renderer must still validate
  actual contrast and grayscale behavior in its concrete output.
- Adding or removing a token, component mapping, or density is a versioned design-
  system change rather than a runtime registration action.

## Alternatives Considered

- **Define styles inside the ReportLab renderer:** rejected because design policy
  would become PDF-specific and difficult to reuse consistently.
- **Put visual tokens in `SemanticArtifact`:** rejected because semantic meaning and
  design policy have different responsibilities and versioning pressure.
- **Allow runtime theme or plugin registration:** rejected because ART-1.0 requires
  one deterministic executive design system, not negotiation or arbitrary fallback.
- **Use only abstract color names without canonical values:** rejected because future
  renderer implementations would be free to produce inconsistent palettes.
