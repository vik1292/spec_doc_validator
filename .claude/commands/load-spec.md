Load and parse a spec document into the validator registry.

**No API key required.**

**Usage:** `/load-spec <path-to-spec> --id <spec-id>`

Run the following shell command with the arguments supplied by the user:

```bash
specval load-spec $ARGUMENTS
```

If no `--id` argument is provided, derive a sensible ID from the filename (strip extension, replace spaces/hyphens with underscores, lowercase) and include `--id <derived-id>` in the command.

After loading, run:
```bash
specval list-specs
```
Show the user the current registry so they can confirm the spec loaded and see the detected field count.

**Supported formats:** `.xlsx`, `.xls`, `.md`, `.markdown`, `.docx`

**Examples:**
- `/load-spec ./specs/customer_data_spec.xlsx --id customer_v2`
- `/load-spec ./docs/orders_schema.md --id orders`
- `/load-spec ./specs/product_catalog.docx --id products`
- `/load-spec ./specs/product_catalog.docx` ← ID auto-derived as `product_catalog`

Use `--force` to re-parse a spec that is already registered (e.g. after editing the spec file).
