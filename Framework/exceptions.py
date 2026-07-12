"""
=========================================================
BursaAI Framework Exceptions
Version : 6.0 Sprint 1
=========================================================
"""


class BursaAIError(Exception):
    """Base exception for all BursaAI framework errors."""


class DataError(BursaAIError):
    """Raised when required market data is missing or invalid."""


class ValidationError(BursaAIError):
    """Raised when an object fails validation."""


class EngineError(BursaAIError):
    """Raised when an analysis engine fails."""


class RegistryError(BursaAIError):
    """Raised when engine registration or dependency resolution fails."""


class PipelineError(BursaAIError):
    """Raised when pipeline execution cannot continue."""


class ConfigurationError(BursaAIError):
    """Raised when framework configuration is invalid."""
