from enum import Enum
from pydantic import BaseModel, Field


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ViolationCategory(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    INVALID_VALUE = "invalid_value"
    MISSING_COLUMN = "missing_column"
    EXTRA_COLUMN = "extra_column"
    NULL_VIOLATION = "null_violation"
    PATTERN_MISMATCH = "pattern_mismatch"
    RANGE_VIOLATION = "range_violation"
    NAMING_CONVENTION = "naming_convention"
    FILE_NAMING = "file_naming"
    BUSINESS_RULE = "business_rule"
    SEMANTIC_MISMATCH = "semantic_mismatch"


class ValidationViolation(BaseModel):
    category: ViolationCategory
    severity: Severity
    field_name: str | None = None
    row_index: int | None = None
    value: str | None = None
    message: str
    suggestion: str = ""
    claude_reasoning: str = ""


class ValidationResult(BaseModel):
    spec_id: str
    data_file: str
    validated_at: str
    violations: list[ValidationViolation] = Field(default_factory=list)
    summary: str = ""
    cache_hit: bool = False
    input_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    output_tokens: int = 0

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.WARNING)

    @property
    def passed(self) -> bool:
        return self.error_count == 0
