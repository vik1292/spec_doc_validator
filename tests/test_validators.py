"""Tests for prompt_cache rendering — no API calls needed."""
from spec_validator.models.spec import DataType, FieldSpec, NullPolicy, SpecDocument
from spec_validator.validators.prompt_cache import _render_spec_content, build_system_prompt


def _make_spec(**kwargs) -> SpecDocument:
    defaults = dict(
        spec_id="test",
        source_path="/tmp/test.md",
        source_format="md",
        title="Test Spec",
        fields=[
            FieldSpec(
                name="user_id",
                data_type=DataType.INTEGER,
                nullable=NullPolicy.REQUIRED,
            ),
            FieldSpec(
                name="email",
                data_type=DataType.EMAIL,
                nullable=NullPolicy.REQUIRED,
                description="Primary email",
            ),
        ],
    )
    defaults.update(kwargs)
    return SpecDocument(**defaults)


def test_render_is_deterministic():
    spec = _make_spec()
    first = _render_spec_content(spec)
    second = _render_spec_content(spec)
    assert first == second


def test_render_includes_fields():
    spec = _make_spec()
    content = _render_spec_content(spec)
    assert "user_id" in content
    assert "email" in content
    assert "integer" in content


def test_render_fields_are_sorted():
    spec = _make_spec()
    content = _render_spec_content(spec)
    # email comes before user_id alphabetically
    assert content.index("### email") < content.index("### user_id")


def test_render_includes_raw_content():
    spec = _make_spec(raw_content="Some original prose content here.")
    content = _render_spec_content(spec)
    assert "Some original prose content here." in content


def test_build_system_prompt_returns_two_blocks():
    spec = _make_spec()
    blocks = build_system_prompt(spec)
    assert len(blocks) == 2
    assert all(b["type"] == "text" for b in blocks)
    assert all("cache_control" in b for b in blocks)


def test_build_system_prompt_cache_control_format():
    spec = _make_spec()
    blocks = build_system_prompt(spec)
    for block in blocks:
        assert block["cache_control"]["type"] == "ephemeral"


def test_allowed_values_sorted_for_determinism():
    spec = _make_spec(
        fields=[
            FieldSpec(
                name="status",
                allowed_values=["suspended", "active", "inactive"],
            )
        ]
    )
    content1 = _render_spec_content(spec)

    spec2 = _make_spec(
        fields=[
            FieldSpec(
                name="status",
                allowed_values=["inactive", "suspended", "active"],
            )
        ]
    )
    content2 = _render_spec_content(spec2)
    assert content1 == content2
