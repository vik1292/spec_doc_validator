# spec_doc_validator

Validate CSV and Excel data files against specification documents using Claude AI.

## Features

- **Multi-format spec documents** — Excel (`.xlsx`/`.xls`), Markdown (`.md`), Word (`.docx`)
- **Multi-format data files** — CSV and Excel
- **Intelligent validation** — Claude understands business rules described in prose, not just regex
- **What gets checked:**
  - Missing / extra columns
  - Data types
  - Allowed values (enums, ranges)
  - Nullability / required fields
  - Column naming conventions
  - File naming conventions
  - Business rules from spec prose
- **Prompt caching** — spec content is cached in Claude's prompt cache for cost efficiency
- **Multiple specs** — load specs for different initiatives simultaneously
- **Claude Code slash commands** — `/validate`, `/load-spec`, `/list-specs`, `/report`

## Installation

```bash
# With uv (recommended)
uv sync

# Or with pip
pip install -e .
```

Requires Python 3.11+. Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or add to a .env file: ANTHROPIC_API_KEY=sk-ant-...
```

## Quick Start

```bash
# 1. Load a spec document
specval load-spec examples/sample_spec.md --id customer

# 2. Validate a data file
specval validate examples/sample_data.csv --spec customer

# 3. Save report as JSON
specval validate examples/sample_data.csv --spec customer --save report.json

# 4. List loaded specs
specval list-specs

# 5. Remove a spec
specval remove-spec customer
```

## Claude Code Slash Commands

Inside a Claude Code session, use these commands:

| Command | Description |
|---------|-------------|
| `/load-spec <path> --id <id>` | Parse and register a spec document |
| `/validate <data-file> --spec <id>` | Validate data against a spec |
| `/list-specs` | Show all loaded specs |
| `/report <report.json>` | Display a saved report |

## Supported Spec Formats

| Format | How fields are extracted |
|--------|--------------------------|
| Markdown `.md` | Pipe tables with `field`/`name`/`column` header |
| Excel `.xlsx` | Sheet named "schema"/"fields"/"spec", or first sheet with field-name column |
| Word `.docx` | First table with `field`/`name`/`column` header |

All formats: the full document text is included in Claude's context for business rule interpretation.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key (required) |
| `SPECVAL_REGISTRY_PATH` | Path to spec registry JSON (default: `~/.config/specval/registry.json`) |
| `SPECVAL_MODEL` | Claude model (default: `claude-sonnet-4-6`) |

## Running Tests

```bash
pytest
```
