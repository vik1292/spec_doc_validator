# specval-list — List Loaded Specs

Show all spec documents currently registered in the spec registry.

## Steps

1. Run:
```bash
   specval list-specs
```

2. Present the output in a clean table format:

   | Spec ID | Source File | Fields | Loaded |
   |---|---|---|---|
   | customer | examples/sample_spec.md | 12 | 2026-04-25 |
   | orders | specs/orders_v2.xlsx | 8 | 2026-04-24 |

3. If the registry is empty:
   > "No specs loaded yet. Use `/specval-load <path> --id <id>` to register one.
   > Example: `/specval-load examples/sample_spec.md --id demo`"

4. After listing, offer:
   > "Run `/specval-validate <data-file> --spec <id>` to validate against any of these."

## Environment

Registry is stored at:
- Default: `~/.config/specval/registry.json`
- Custom: set `SPECVAL_REGISTRY_PATH` environment variable