# specval — Spec Doc Validator

AI-powered validation of CSV/Excel data files against spec documents.

## On Launch (no arguments)

Display this menu:

---

**spec_doc_validator** — Claude Code Commands

| Command | Description |
|---|---|
| `/specval-load <path> --id <id>` | Parse and register a spec document (md/xlsx/docx) |
| `/specval-validate <data-file> --spec <id>` | Validate a data file against a loaded spec |
| `/specval-list` | Show all currently loaded specs with metadata |
| `/specval-report <report.json>` | Display and summarize a saved validation report |

**Quick start:**

Run `/specval` at any time to show this menu.

---

## If Arguments Are Passed

If the user passes a file path directly (e.g., `/specval examples/sample_data.csv`),
treat it as a validate request and ask which spec ID to use if none is specified:
> "Which spec should I validate against? Run `/specval-list` to see loaded specs,
> or `/specval-load <path> --id <id>` to load one first."