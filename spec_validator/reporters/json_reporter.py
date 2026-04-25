from pathlib import Path

from spec_validator.models.validation import ValidationResult


class JsonReporter:
    def to_string(self, result: ValidationResult) -> str:
        return result.model_dump_json(indent=2)

    def save(self, result: ValidationResult, path: str) -> None:
        Path(path).write_text(self.to_string(result), encoding="utf-8")
