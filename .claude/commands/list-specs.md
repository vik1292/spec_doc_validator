List all spec documents currently loaded in the registry.

**No API key required.**

**Usage:** `/list-specs`

Run:

```bash
specval list-specs
```

Displays a table showing:
- Spec ID
- Source format (xlsx / md / docx)
- Number of field definitions extracted
- Source file path
- When it was last parsed

**Managing specs:**
- Load a new spec: `/load-spec <path> --id <id>`
- Re-parse an updated spec: `/load-spec <path> --id <id> --force`
- Remove a spec: `specval remove-spec <id>`
- Inspect a spec's full field definitions: `specval dump-spec <id>`
