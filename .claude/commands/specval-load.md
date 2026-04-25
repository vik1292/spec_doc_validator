# specval-load — Load a Spec Document

Parse and register a spec document so it can be used for validation.

## Arguments

- `$ARGUMENTS` — expected format: `<path-to-spec> --id <spec-id>`
  - `<path-to-spec>`: path to a `.md`, `.xlsx`/`.xls`, or `.docx` spec file
  - `--id <spec-id>`: short identifier for this spec (e.g., `customer`, `orders`, `loans`)

## Steps

1. Parse `$ARGUMENTS` to extract the file path and `--id` value.

2. If either is missing, prompt:
   - If no path: "What spec file do you want to load? (supports .md, .xlsx, .xls, .docx)"
   - If no `--id`: "What ID should I register this spec under? (e.g., `customer`, `orders`)"

3. Verify the file exists before running. If not found, say:
   > "File not found: `<path>`. Check the path and try again."

4. Run:
```bash
   specval load-spec <path> --id <id>
```

5. After success, confirm:
   > "Spec `<id>` loaded from `<path>`.
   > Fields extracted: <N> columns
   > Ready to validate — run `/specval-validate <data-file> --spec <id>`"

6. If the spec already exists under that ID, ask:
   > "A spec with ID `<id>` is already loaded. Replace it? (yes/no)"
   Wait for confirmation before re-running.

## Supported Formats

| Format | How fields are extracted |
|---|---|
| `.md` | Pipe tables with `field`/`name`/`column` header |
| `.xlsx` / `.xls` | Sheet named "schema"/"fields"/"spec", or first sheet with field-name column |
| `.docx` | First table with `field`/`name`/`column` header |

The full document text is passed to Claude for business rule interpretation.