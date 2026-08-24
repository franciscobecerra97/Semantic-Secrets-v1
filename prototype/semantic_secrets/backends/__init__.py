"""Versioned generator and semantic-extractor backend contracts."""

from .interfaces import (
    BackendMetadata,
    DenseEmbeddingBackend,
    GeneratedImage,
    GenerationBackend,
    GenerationRequest,
    StructuredExtractionBackend,
    StructuredExtractionRequest,
    TextSemanticBackend,
)

__all__ = [
    "BackendMetadata",
    "DenseEmbeddingBackend",
    "GeneratedImage",
    "GenerationBackend",
    "GenerationRequest",
    "StructuredExtractionBackend",
    "StructuredExtractionRequest",
    "TextSemanticBackend",
]
