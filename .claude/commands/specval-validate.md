# specval-validate — Validate a Data File Against a Spec

Run Claude AI validation of a CSV or Excel data file against a registered spec.

## Arguments

- `$ARGUMENTS` — expected format: `<data-file> --spec <spec-id>`
  - `<data-file>`: path to a `.csv` or `.xlsx`/`.xls` file
  - `--spec <spec-id>`: ID of a previously loaded spec

## Steps

1. Parse `$ARGUMENTS` to extract the data file path and `--spec` value.

2. If either is missing:
   - If no data file: "What data file do you want to validate?"
   - If no `--spec`: "Which spec ID should I validate against? Run `/specval-list` to see
     loaded specs."

3. Verify both the data file exists and the spec ID is registered. If spec not found:
   > "No spec registered with ID `<id>`. Run `/specval-list` to see what's loaded,
   > or `/specval-load` to add one."

4. Run validation:
```bash
   specval validate <data-file> --spec <spec-id>
```

5. Parse and present results grouped by severity:

   **ERRORs** (must fix before data is usable):
   - Missing required columns
   - Type mismatches
   - Null values in required fields
   - Values outside allowed enums/ranges

   **WARNINGs** (review recommended):
   - Extra columns not in spec
   - Column naming convention deviations
   - File naming convention issues

   **INFO** (advisory):
   - Business rule observations
   - Coverage notes

6. Provide a summary:
   > "Validation complete: X errors, Y warnings, Z info items.
   > Data file is [VALID / INVALID — fix errors before use]."

7. If errors found, offer next steps:
   > "Want me to explain any of these findings in detail, or suggest fixes?"

## Saving Reports

To save the report as JSON for later review:
```bash
specval validate <data-file> --spec <spec-id> --save <report.json>
```
Then use `/specval-report <report.json>` to display it.

## Rules

- NEVER auto-modify the data file. Surface issues only; the user fixes.
- If validation output is long, summarize the top errors first, then offer to show full detail.