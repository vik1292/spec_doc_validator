from spec_validator.models.spec import SpecDocument

_INSTRUCTIONS = """You are a data validation engine. Your task is to validate a data file \
against the spec document provided above.

You will receive a JSON object describing the data file (column names, inferred dtypes, \
null counts, and sample rows). Validate it thoroughly and respond with a JSON object \
matching this exact schema:

{
  "violations": [
    {
      "category": "<one of: type_mismatch|invalid_value|missing_column|extra_column|null_violation|pattern_mismatch|range_violation|naming_convention|file_naming|business_rule|semantic_mismatch>",
      "severity": "<error|warning|info>",
      "field_name": "<column name or null>",
      "row_index": <0-based integer or null>,
      "value": "<offending value as string or null>",
      "message": "<concise description of the violation>",
      "suggestion": "<how to fix it>",
      "claude_reasoning": "<why you flagged this>"
    }
  ],
  "summary": "<1-3 sentence prose summary of overall data quality>"
}

Validation rules:
- Use severity=error for violations that would cause data ingestion or processing failure.
- Use severity=warning for deviations that are unusual but may be acceptable in context.
- Use severity=info for observations (e.g. extra columns not defined in spec).
- Infer intent from business rules described in prose — don't just pattern-match.
- If a numeric field contains values stored as strings (e.g. "123" for an integer column), \
flag as warning not error.
- Check the file_name against file_naming_pattern if one is defined in the spec.
- Check column names against the naming_convention if one is defined.
- For missing required columns, always use severity=error.
- Respond ONLY with the JSON object. No markdown fences, no preamble, no trailing text."""


def build_system_prompt(spec: SpecDocument) -> list[dict]:
    """Build system content blocks with prompt caching for the spec document.

    Two cache breakpoints are used:
    - Block 0: spec content (large, stable) — cache_control applied here
    - Block 1: instructions (static prose) — cache_control applied here

    IMPORTANT: _render_spec_content() must be deterministic. Do NOT inject
    timestamps, random IDs, or any per-request state into the system prompt.
    Cache invalidation happens automatically when the spec content changes.
    """
    return [
        {
            "type": "text",
            "text": _render_spec_content(spec),
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": _INSTRUCTIONS,
            "cache_control": {"type": "ephemeral"},
        },
    ]


def _render_spec_content(spec: SpecDocument) -> str:
    """Render spec to a deterministic string for stable cache prefix matching.

    All collections are sorted to ensure identical output for identical input.
    """
    lines = [
        f'<spec_document id="{spec.spec_id}" format="{spec.source_format}">',
        f"<title>{spec.title or spec.spec_id}</title>",
        f"<description>{spec.description}</description>",
        f"<version>{spec.version}</version>",
        "",
        "## Field Definitions",
        "",
    ]

    for field in sorted(spec.fields, key=lambda f: f.name):
        lines.append(f"### {field.name}")
        lines.append(f"- type: {field.data_type.value}")
        lines.append(f"- nullable: {field.nullable.value}")
        if field.allowed_values:
            lines.append(f"- allowed_values: {sorted(field.allowed_values)}")
        if field.pattern:
            lines.append(f"- pattern: {field.pattern}")
        if field.min_value is not None:
            lines.append(f"- min: {field.min_value}")
        if field.max_value is not None:
            lines.append(f"- max: {field.max_value}")
        if field.description:
            lines.append(f"- description: {field.description}")
        for rule in sorted(field.business_rules):
            lines.append(f"- rule: {rule}")
        lines.append("")

    if spec.naming_convention:
        nc = spec.naming_convention
        lines.append("## Column Naming Convention")
        if nc.pattern:
            lines.append(f"- pattern: {nc.pattern}")
        if nc.prefix:
            lines.append(f"- prefix: {nc.prefix}")
        if nc.suffix:
            lines.append(f"- suffix: {nc.suffix}")
        if nc.description:
            lines.append(f"- description: {nc.description}")
        lines.append("")

    if spec.file_naming_pattern:
        lines.append(f"## File Naming Pattern\n{spec.file_naming_pattern}\n")

    if spec.raw_content:
        lines.append("## Original Spec Content (full context)")
        lines.append(spec.raw_content)

    lines.append("</spec_document>")
    return "\n".join(lines)
