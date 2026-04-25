import json
from datetime import datetime, timezone

import anthropic

from spec_validator.models.spec import SpecDocument
from spec_validator.models.validation import (
    Severity,
    ValidationResult,
    ValidationViolation,
    ViolationCategory,
)
from spec_validator.parsers.data_parser import DataSample
from spec_validator.validators.prompt_cache import build_system_prompt

MODEL = "claude-sonnet-4-6"


class ClaudeValidator:
    """Validates a DataSample against a SpecDocument using Claude with prompt caching.

    The spec content is cached in the system prompt (ephemeral, 5-min TTL default).
    The data sample is sent in the user message and is never cached.
    """

    def __init__(self, api_key: str | None = None) -> None:
        from spec_validator.config import settings

        self._client = anthropic.Anthropic(
            api_key=api_key or settings.anthropic_api_key
        )

    def validate(
        self,
        spec: SpecDocument,
        sample: DataSample,
        file_name: str,
    ) -> ValidationResult:
        system_blocks = build_system_prompt(spec)
        user_content = self._build_user_message(sample, file_name)

        response = self._client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_blocks,
            messages=[{"role": "user", "content": user_content}],
        )

        return self._parse_response(
            response=response,
            spec_id=spec.spec_id,
            data_file=file_name,
        )

    def _build_user_message(self, sample: DataSample, file_name: str) -> str:
        payload = {
            "file_name": file_name,
            "column_names": sample.columns,
            "inferred_dtypes": sample.dtypes,
            "row_count": sample.row_count,
            "null_counts": sample.null_counts,
            "sample_rows": sample.sample_rows,
            "value_samples": sample.value_samples,
        }
        return (
            "Validate the following data file against the spec document above.\n\n"
            f"```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```"
        )

    def _parse_response(
        self,
        response: anthropic.types.Message,
        spec_id: str,
        data_file: str,
    ) -> ValidationResult:
        usage = response.usage
        raw_text = next(
            (b.text for b in response.content if b.type == "text"), ""
        )

        # Strip markdown fences if Claude added them despite instructions
        stripped = raw_text.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            stripped = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            return ValidationResult(
                spec_id=spec_id,
                data_file=data_file,
                validated_at=datetime.now(timezone.utc).isoformat(),
                violations=[
                    ValidationViolation(
                        category=ViolationCategory.SEMANTIC_MISMATCH,
                        severity=Severity.ERROR,
                        message=f"Claude returned unparseable response: {raw_text[:300]}",
                    )
                ],
                cache_hit=getattr(usage, "cache_read_input_tokens", 0) > 0,
                input_tokens=usage.input_tokens,
                cache_read_tokens=getattr(usage, "cache_read_input_tokens", 0),
                cache_write_tokens=getattr(usage, "cache_creation_input_tokens", 0),
                output_tokens=usage.output_tokens,
            )

        violations = []
        for v in parsed.get("violations", []):
            try:
                violations.append(ValidationViolation(**v))
            except Exception:
                pass

        return ValidationResult(
            spec_id=spec_id,
            data_file=data_file,
            validated_at=datetime.now(timezone.utc).isoformat(),
            violations=violations,
            summary=parsed.get("summary", ""),
            cache_hit=getattr(usage, "cache_read_input_tokens", 0) > 0,
            input_tokens=usage.input_tokens,
            cache_read_tokens=getattr(usage, "cache_read_input_tokens", 0),
            cache_write_tokens=getattr(usage, "cache_creation_input_tokens", 0),
            output_tokens=usage.output_tokens,
        )
