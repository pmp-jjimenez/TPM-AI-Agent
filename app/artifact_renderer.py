"""Renderer-neutral contracts for in-memory artifact generation."""

from dataclasses import dataclass
from enum import Enum
from typing import Generic, Optional, Protocol, Tuple, TypeVar, runtime_checkable


MAX_DIAGNOSTIC_LENGTH = 160


class ArtifactFormat(str, Enum):
    PDF = "pdf"


class ArtifactRendererError(RuntimeError):
    """A bounded application-facing renderer error."""

    def __init__(self, code, public_message):
        self.code = _sanitize_diagnostic(code)
        self.public_message = _sanitize_diagnostic(public_message)
        super().__init__(self.public_message)


class ArtifactDependencyError(ArtifactRendererError):
    """Raised when an explicitly requested renderer dependency is unavailable."""


class ArtifactConfigurationError(ArtifactRendererError):
    """Raised when an explicitly requested renderer is not configured safely."""


@dataclass(frozen=True)
class RenderContext:
    language_tag: str
    deterministic_test_mode: bool = False
    title: Optional[str] = None
    subject: Optional[str] = None
    author: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    classification_label: Optional[str] = None

    def __post_init__(self):
        if not self.language_tag or len(self.language_tag) > 35:
            raise ValueError("language_tag must be a bounded non-empty value")
        for field_name in (
            "title",
            "subject",
            "author",
            "creator",
            "producer",
            "classification_label",
        ):
            value = getattr(self, field_name)
            if value is not None and (
                not isinstance(value, str)
                or not value.strip()
                or len(value) > 200
            ):
                raise ValueError(f"{field_name} must be a bounded non-empty value")


ArtifactRenderContext = RenderContext


@dataclass(frozen=True)
class RenderedArtifact:
    format: ArtifactFormat
    media_type: str
    extension: str
    payload: bytes
    diagnostics: Tuple[str, ...] = ()

    def __post_init__(self):
        if self.format != ArtifactFormat.PDF:
            raise ValueError("Unsupported artifact format")
        if self.media_type != "application/pdf" or self.extension != "pdf":
            raise ValueError("PDF artifact metadata is inconsistent")
        if not isinstance(self.payload, bytes) or not self.payload:
            raise ValueError("Rendered artifact payload must be non-empty bytes")
        object.__setattr__(
            self,
            "diagnostics",
            tuple(_sanitize_diagnostic(value) for value in self.diagnostics),
        )


ArtifactInput = TypeVar("ArtifactInput")


@runtime_checkable
class ArtifactRenderer(Protocol, Generic[ArtifactInput]):
    """A narrow protocol without defining a speculative artifact content model."""

    @property
    def format(self) -> ArtifactFormat:
        ...

    def render(self, artifact: ArtifactInput, context: RenderContext) -> RenderedArtifact:
        ...


def _sanitize_diagnostic(value):
    text = " ".join(str(value).split())
    text = text.replace("/", "-").replace("\\", "-")
    return text[:MAX_DIAGNOSTIC_LENGTH]
