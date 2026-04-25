from pathlib import Path

import pytest

from spec_validator.parsers.data_parser import DataFileParser
from spec_validator.parsers.markdown_parser import MarkdownSpecParser

EXAMPLES = Path(__file__).parent.parent / "examples"


def test_markdown_parser_loads_fields():
    parser = MarkdownSpecParser()
    spec = parser.parse(str(EXAMPLES / "sample_spec.md"), "customer_test")

    assert spec.spec_id == "customer_test"
    assert spec.source_format == "md"
    assert len(spec.fields) > 0

    names = [f.name for f in spec.fields]
    assert "customer_id" in names
    assert "email" in names
    assert "status" in names


def test_markdown_parser_extracts_allowed_values():
    parser = MarkdownSpecParser()
    spec = parser.parse(str(EXAMPLES / "sample_spec.md"), "customer_test")

    status_field = next(f for f in spec.fields if f.name == "status")
    assert status_field.allowed_values is not None
    assert "active" in status_field.allowed_values
    assert "inactive" in status_field.allowed_values


def test_markdown_parser_extracts_naming_convention():
    parser = MarkdownSpecParser()
    spec = parser.parse(str(EXAMPLES / "sample_spec.md"), "customer_test")

    assert spec.naming_convention is not None
    assert spec.naming_convention.pattern == "snake_case"


def test_data_parser_loads_csv():
    parser = DataFileParser()
    sample = parser.parse(str(EXAMPLES / "sample_data.csv"))

    assert sample.file_name == "sample_data.csv"
    assert "customer_id" in sample.columns
    assert "email" in sample.columns
    assert sample.row_count == 7
    assert len(sample.sample_rows) <= 20


def test_data_parser_value_samples():
    parser = DataFileParser()
    sample = parser.parse(str(EXAMPLES / "sample_data.csv"))

    assert "status" in sample.value_samples
    # Should include at least active/inactive/suspended from the file
    statuses = sample.value_samples["status"]
    assert "active" in statuses


def test_markdown_parser_can_parse():
    parser = MarkdownSpecParser()
    assert parser.can_parse("spec.md") is True
    assert parser.can_parse("spec.markdown") is True
    assert parser.can_parse("spec.xlsx") is False
    assert parser.can_parse("spec.docx") is False
