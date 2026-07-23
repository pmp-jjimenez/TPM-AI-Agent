# ADR 0002: Separate Executive Report Content, Semantic Artifact Composition, and Rendering

- Status: Accepted
- Date: 2026-07-23
- Decision owners: Javier Jiménez, Product Owner; TPM Operating System engineering
- Scope: ART-1.0 Executive Artifact Foundation

## Context

Executive reporting must preserve the distinction between recorded Program facts,
deterministic calculations, recommendations, and unavailable information. If that
classification is performed in a PDF renderer, the same Program could acquire
different meaning in PDF, PowerPoint, HTML, Markdown, or an API response. Conversely,
placing visual concepts in the report truth model would couple business meaning to a
particular layout system.

## Decision

The architecture is separated into these boundaries:

```text
normalized Program
  -> ExecutiveReportViewModel
  -> SemanticArtifact
  -> ArtifactRenderer
  -> format-specific output
```

- The compatibility-normalized Program is the authoritative source.
- `ExecutiveReportViewModel` owns truthful executive-report meaning. It preserves
  source references and keeps stored facts, deterministic values, recommendations,
  and missing information distinct.
- A future `SemanticArtifact` will own renderer-neutral presentation intent and
  selection. It may choose a display subset while disclosing omissions, but it may not
  reclassify Program records.
- Renderers own only format-specific layout and serialization. No renderer may
  classify Program data or create business conclusions.
- The report view model may not contain visual components, format-native objects,
  pages, slides, fonts, colors, coordinates, file paths, or output behavior.
- Future PowerPoint and HTML implementations may reuse the same report content model.
- `SemanticArtifact` is deliberately not implemented in ART-1.0 Increment 2.

## Consequences

- Report meaning is deterministic, testable without ReportLab, and reusable across
  presentation formats.
- Presentation limits do not cause source records to disappear from the truth model.
- Missing schema capabilities, including dependency criticality and explicit
  decision-blocker evidence, remain visible limitations instead of inferred values.
- Later composition and renderer increments must consume this contract without moving
  classification logic downstream.

## Alternatives Considered

- **Classify records in each renderer:** rejected because meaning would vary by output
  format and renderer tests would become domain tests.
- **Combine truth and presentation in one semantic model:** rejected because visual
  selection and hierarchy would obscure the complete source-backed report contract.
- **Generate report narrative with Gemini:** rejected because this boundary requires
  deterministic, source-traceable content and the Program schema has no approved
  stored executive-summary field.
