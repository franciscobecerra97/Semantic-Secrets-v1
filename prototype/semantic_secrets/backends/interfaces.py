"""Protocol-neutral backend contracts frozen for P4 screening.

Heavy ML libraries are deliberately absent from this module. Implementations load
them lazily and must report exact artifact/config metadata with each output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable


@dataclass(frozen=True)
class BackendMetadata:
    backend_id: str
    backend_version: str
    artifact_id: str | None
    artifact_revision: str | None
    config_sha256: str
    device: str
    dtype: str
    deterministic_controls: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GenerationRequest:
    request_id: str
    prompt: str
    seed: int
    width: int
    height: int
    inference_steps: int
    guidance_scale: float


@dataclass(frozen=True)
class GeneratedImage:
    request_id: str
    width: int
    height: int
    rgb_sha256: str
    encoded_sha256: str | None
    metadata: BackendMetadata


@dataclass(frozen=True)
class StructuredExtractionRequest:
    request_id: str
    image_rgb: bytes
    width: int
    height: int
    schema_version: str


@runtime_checkable
class GenerationBackend(Protocol):
    @property
    def metadata(self) -> BackendMetadata: ...

    def generate(self, request: GenerationRequest) -> GeneratedImage: ...


@runtime_checkable
class StructuredExtractionBackend(Protocol):
    @property
    def metadata(self) -> BackendMetadata: ...

    def extract(self, request: StructuredExtractionRequest) -> Mapping[str, Any]: ...


@runtime_checkable
class DenseEmbeddingBackend(Protocol):
    @property
    def metadata(self) -> BackendMetadata: ...

    def embed_images(self, images_rgb: Sequence[bytes], sizes: Sequence[tuple[int, int]]) -> Sequence[Sequence[float]]: ...

    def embed_texts(self, texts: Sequence[str]) -> Sequence[Sequence[float]]: ...


@runtime_checkable
class TextSemanticBackend(Protocol):
    @property
    def metadata(self) -> BackendMetadata: ...

    def extract_text(self, text: str, schema_version: str) -> Mapping[str, Any]: ...
