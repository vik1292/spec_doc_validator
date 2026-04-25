# spec_doc_validator — AI-Powered Spec Validation

## What This Is

`spec_doc_validator` validates CSV and Excel data files against specification documents
(Markdown, Excel, Word). Claude reads the spec's business rules in prose — not just regex —
and checks data files for column presence, types, allowed values, nullability, naming
conventions, and business rule compliance.

The CLI tool is `specval`. These slash commands are the Claude Code interface to the same
functionality, with richer output and interactive guidance.

## Session Startup (run silently on first message)

Before doing anything else, silently check:

1. Is `ANTHROPIC_API_KEY` set in the environment or `.env`?
2. Is the package installed? (check if `specval` is available: `specval --version`)
3. Is the spec registry initialized? (check `~/.config/specval/registry.json` exists)

**If API key is missing**, surface immediately:
> "Your `ANTHROPIC_API_KEY` is not set. Add it to your environment or create a `.env` file
> in this directory with `ANTHROPIC_API_KEY=sk-ant-...` before running any commands."

**If `specval` is not installed**, surface immediately:
> "The package isn't installed yet. Run `uv sync` or `pip install -e .` first."

**If registry doesn't exist yet**, that's fine — it's created on first `load-spec`. Say nothing.

**If all checks pass**, display the welcome menu (same output as `/specval` with no args).

## What is spec_doc_validator

| File/Dir | Purpose |
|---|---|
| `spec_validator/cli.py` | Typer CLI — entry point for `specval` commands |
| `spec_validator/validator.py` | Core validation logic using Claude API |
| `spec_validator/parsers.py` | Spec document parsers (md/xlsx/docx) |
| `spec_validator/registry.py` | Spec registry (load/list/remove specs) |
| `examples/sample_spec.md` | Example spec document |
| `examples/sample_data.csv` | Example data file |
| `.claude/commands/` | Claude Code slash command definitions |
| `~/.config/specval/registry.json` | Persistent spec registry (created at runtime) |

## Slash Command Routing

| User input | Command to run |
|---|---|
| `/specval` (no args) | Show welcome menu with all commands |
| `/specval-load` | Load and register a spec document |
| `/specval-validate` | Validate a data file against a loaded spec |
| `/specval-list` | List all currently loaded specs |
| `/specval-report` | Display a saved validation report |

## Rules

- NEVER run `specval validate` and auto-apply fixes to a data file. Claude surfaces issues;
  the user decides what to do.
- NEVER delete spec entries from the registry without explicit user confirmation.
- When validation finds errors, always group them by severity: ERROR (blocks use),
  WARNING (review recommended), INFO (advisory only).
- When a spec file path or data file path doesn't exist, say so clearly and stop — don't
  guess at paths.
- Prefer running the underlying `specval` CLI commands via bash so the user sees the same
  output they'd get from the terminal. Augment with analysis; don't replace the tool output.