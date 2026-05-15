"""Validation exception hierarchy for the schema layer."""


class ValidationError(Exception):
    """Base class for all content validation errors."""


class SchemaViolation(ValidationError):
    """A content file has a structural error: missing required field, wrong type, or invalid value."""


class VocabularyViolation(ValidationError):
    """A content file uses a string value not in the allowed vocabulary (e.g. unknown feature_type)."""


class ReferenceError(ValidationError):
    """A content file references content that does not exist in the registry. Used in M2."""
