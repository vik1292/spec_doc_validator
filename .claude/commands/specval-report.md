# specval-report — Display a Saved Validation Report

Load and display a previously saved validation report JSON file with rich formatting
and actionable analysis.

## Arguments

- `$ARGUMENTS` — path to a `.json` report file saved with `specval validate --save`

## Steps

1. If no path provided, ask:
   > "What report file do you want to display? (e.g., `report.json`)"

2. Verify the file exists. If not:
   > "File not found: `<path>`. Reports are saved with:
   > `specval validate <data-file> --spec <id> --save <report.json>`"

3. Run:
```bash
   specval report <report.json>
```

4. After displaying the raw report output, provide a structured summary:

   **Report Summary**
   - Spec validated against: `<spec-id>`
   - Data file: `<filename>`
   - Validated at: `<timestamp>`
   - Result: PASS / FAIL

   **Finding Breakdown**
   | Severity | Count | Top Issue |
   |---|---|---|
   | ERROR | N | <most critical issue> |
   | WARNING | N | <most common warning> |
   | INFO | N | — |

5. If the report shows failures, offer:
   > "Want me to walk through each error and suggest how to fix it?"

6. If the report shows a clean pass:
   > "This data file passed validation against spec `<id>`. All required columns present,
   > types match, and business rules satisfied."