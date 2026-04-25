Validate a CSV or Excel data file against a loaded spec document.

**No API key required** — validation is performed by Claude Code directly.

**Usage:** `/validate <data-file> --spec <spec-id>`

Parse `$ARGUMENTS` to extract the data file path and spec ID (from `--spec` or `-s`).

Then follow these steps:

**Step 1 — Dump the spec:**
```bash
specval dump-spec <spec-id>
```
This prints the full `SpecDocument` JSON including all field definitions, types, allowed values, patterns, naming convention, and business rules.

**Step 2 — Dump the data sample:**
```bash
specval dump-sample <data-file>
```
This prints a `DataSample` JSON: column names, inferred dtypes, row count, null counts, sample rows (up to 20), and unique value samples per column.

**Step 3 — Validate**

Using the spec and data sample from above, perform a thorough validation and report your findings. Check all of the following:

- **Missing columns** — required columns absent from the data (error)
- **Extra columns** — columns present but not defined in spec (info)
- **Data types** — do values match the declared types?
- **Allowed values** — do enum fields only contain permitted values?
- **Nullability** — do required fields have any nulls/empty values?
- **Patterns** — do string fields match their regex constraints?
- **File naming** — does the filename match `file_naming_pattern` if defined?
- **Column naming** — do column names follow the `naming_convention` if defined?
- **Business rules** — apply any prose rules described in the spec
- **Semantic integrity** — does the data content make sense for what each field claims to be?

**Step 4 — Report results**

Present your findings as:
1. A clear **PASSED / FAILED** status (failed = any errors found)
2. A **violations table** listing each issue with: severity (error/warning/info), field name, row index if applicable, the offending value, a description, and a suggested fix
3. A **1–3 sentence summary** of overall data quality

If `--save <file.json>` was passed, also run:
```bash
specval report --help
```
and note that saving requires the standalone `specval validate` command with an API key.

**Examples:**
- `/validate ./data/customers_2026.csv --spec customer_v2`
- `/validate ./data/orders.xlsx --spec orders`
