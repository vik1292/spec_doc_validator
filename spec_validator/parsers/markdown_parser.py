import re
from datetime import datetime, timezone
from pathlib import Path

from markdown_it import MarkdownIt

from spec_validator.models.spec import (
    DataType,
    FieldSpec,
    NamingConvention,
    NullPolicy,
    SpecDocument,
)
from spec_validator.parsers.base import BaseSpecParser

_FIELD_NAME_HEADERS = {"field", "name", "column", "field_name", "column_name", "fieldname"}
_TYPE_HEADERS = {"type", "data_type", "datatype", "dtype"}
_NULLABLE_HEADERS = {"nullable", "required", "mandatory", "null", "optional"}
_ALLOWED_HEADERS = {"allowed_values", "values", "enum", "valid_values", "allowed"}
_DESCRIPTION_HEADERS = {"description", "desc", "notes", "note", "comment"}
_PATTERN_HEADERS = {"pattern", "regex", "format"}

_TYPE_MAP: dict[str, DataType] = {
    "string": DataType.STRING, "str": DataType.STRING, "text": DataType.STRING,
    "integer": DataType.INTEGER, "int": DataType.INTEGER,
    "float": DataType.FLOAT, "double": DataType.FLOAT, "decimal": DataType.FLOAT,
    "boolean": DataType.BOOLEAN, "bool": DataType.BOOLEAN,
    "date": DataType.DATE,
    "datetime": DataType.DATETIME, "timestamp": DataType.DATETIME,
    "email": DataType.EMAIL,
    "url": DataType.URL, "uri": DataType.URL,
    "enum": DataType.ENUM,
}


class MarkdownSpecParser(BaseSpecParser):
    def __init__(self) -> None:
        self._md = MarkdownIt().enable("table")

    def can_parse(self, path: str) -> bool:
        return Path(path).suffix.lower() in (".md", ".markdown")

    def parse(self, path: str, spec_id: str) -> SpecDocument:
        text = Path(path).read_text(encoding="utf-8")
        tokens = self._md.parse(text)

        fields = self._extract_fields(tokens)
        naming_convention = self._extract_naming_convention(tokens)
        file_naming = self._extract_file_naming(tokens)
        title = self._extract_title(tokens)

        return SpecDocument(
            spec_id=spec_id,
            source_path=str(Path(path).resolve()),
            source_format="md",
            title=title or Path(path).stem,
            fields=fields,
            naming_convention=naming_convention,
            file_naming_pattern=file_naming,
            raw_content=text,
            parsed_at=datetime.now(timezone.utc).isoformat(),
        )

    def _extract_title(self, tokens) -> str:
        for i, tok in enumerate(tokens):
            if tok.type == "heading_open" and tok.tag == "h1":
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    return tokens[i + 1].content.strip()
        return ""

    def _extract_fields(self, tokens) -> list[FieldSpec]:
        tables = self._parse_tables(tokens)
        for table in tables:
            if not table:
                continue
            headers = {k.lower().strip() for k in table[0]}
            if headers & _FIELD_NAME_HEADERS:
                return self._rows_to_field_specs(table)
        return []

    def _parse_tables(self, tokens) -> list[list[dict]]:
        tables = []
        i = 0
        while i < len(tokens):
            if tokens[i].type == "table_open":
                table, i = self._consume_table(tokens, i)
                tables.append(table)
            else:
                i += 1
        return tables

    def _consume_table(self, tokens, start: int) -> tuple[list[dict], int]:
        i = start + 1
        headers: list[str] = []
        rows: list[dict] = []
        in_head = False
        in_body = False

        while i < len(tokens) and tokens[i].type != "table_close":
            t = tokens[i]
            if t.type == "thead_open":
                in_head = True
            elif t.type == "thead_close":
                in_head = False
            elif t.type == "tbody_open":
                in_body = True
            elif t.type == "tbody_close":
                in_body = False
            elif t.type == "tr_open":
                cells: list[str] = []
                i += 1
                while i < len(tokens) and tokens[i].type != "tr_close":
                    if tokens[i].type in ("td_open", "th_open"):
                        i += 1
                        cell_text = ""
                        while i < len(tokens) and tokens[i].type not in ("td_close", "th_close"):
                            if tokens[i].type == "inline":
                                cell_text = tokens[i].content.strip()
                            i += 1
                        cells.append(cell_text)
                    i += 1
                if in_head:
                    headers = cells
                elif in_body and headers:
                    rows.append(dict(zip(headers, cells)))
                i += 1
                continue
            i += 1

        return rows, i + 1

    def _rows_to_field_specs(self, rows: list[dict]) -> list[FieldSpec]:
        if not rows:
            return []

        def _find_key(candidates: set[str]) -> str | None:
            for k in rows[0]:
                normalized = k.lower().strip().replace(" ", "_")
                if normalized in candidates:
                    return k
            return None

        name_key = _find_key(_FIELD_NAME_HEADERS)
        type_key = _find_key(_TYPE_HEADERS)
        nullable_key = _find_key(_NULLABLE_HEADERS)
        allowed_key = _find_key(_ALLOWED_HEADERS)
        desc_key = _find_key(_DESCRIPTION_HEADERS)
        pattern_key = _find_key(_PATTERN_HEADERS)

        if name_key is None:
            return []

        fields = []
        for row in rows:
            name = row.get(name_key, "").strip()
            if not name:
                continue

            raw_type = row.get(type_key, "").lower().strip() if type_key else ""
            data_type = _TYPE_MAP.get(raw_type, DataType.ANY)

            raw_nullable = row.get(nullable_key, "").lower().strip() if nullable_key else ""
            if raw_nullable in ("yes", "true", "1", "nullable", "null"):
                nullable = NullPolicy.NULLABLE
            elif raw_nullable in ("no", "false", "0", "required", "mandatory", "not null"):
                nullable = NullPolicy.REQUIRED
            else:
                nullable = NullPolicy.OPTIONAL

            raw_allowed = row.get(allowed_key, "").strip() if allowed_key else ""
            allowed_values = None
            if raw_allowed:
                allowed_values = [v.strip() for v in raw_allowed.split(",") if v.strip()]

            description = row.get(desc_key, "").strip() if desc_key else ""
            pattern = row.get(pattern_key, "").strip() if pattern_key else ""

            fields.append(FieldSpec(
                name=name,
                data_type=data_type,
                nullable=nullable,
                allowed_values=allowed_values or None,
                pattern=pattern or None,
                description=description,
            ))
        return fields

    def _extract_naming_convention(self, tokens) -> NamingConvention | None:
        in_naming_section = False
        description_parts: list[str] = []

        for i, tok in enumerate(tokens):
            if tok.type == "heading_open":
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    heading = tokens[i + 1].content.lower()
                    in_naming_section = "naming" in heading or "convention" in heading
            elif in_naming_section and tok.type == "inline":
                description_parts.append(tok.content)

        if not description_parts:
            return None

        desc = " ".join(description_parts)
        pattern = None
        if "snake_case" in desc.lower():
            pattern = "snake_case"
        elif "camelcase" in desc.lower() or "camel_case" in desc.lower():
            pattern = "camelCase"
        elif "screaming_snake" in desc.lower() or "upper_snake" in desc.lower():
            pattern = "SCREAMING_SNAKE_CASE"
        elif "pascalcase" in desc.lower() or "pascal_case" in desc.lower():
            pattern = "PascalCase"

        return NamingConvention(pattern=pattern, description=desc)

    def _extract_file_naming(self, tokens) -> str | None:
        in_file_naming_section = False
        for i, tok in enumerate(tokens):
            if tok.type == "heading_open":
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    heading = tokens[i + 1].content.lower()
                    in_file_naming_section = "file naming" in heading or "file name" in heading
            elif in_file_naming_section and tok.type == "inline":
                content = tok.content.strip()
                # Return first non-empty inline content as the pattern
                if content:
                    return content
        return None
