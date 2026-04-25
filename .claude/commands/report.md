Display a previously saved JSON validation report.

**No API key required.**

**Usage:** `/report <path-to-report.json>`

Run:

```bash
specval report $ARGUMENTS
```

Renders a saved JSON report with rich terminal formatting.

Reports are created by running `specval validate --save <file.json>` from the command line (requires an API key for that standalone path).

To re-analyse a dataset inside Claude Code without a saved report, use `/validate` instead.
