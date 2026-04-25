import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="specval",
    help="Validate data files against spec documents using Claude AI.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)


def _get_registry():
    from spec_validator.registry.spec_registry import SpecRegistry
    return SpecRegistry()


@app.command("load-spec")
def load_spec(
    path: Path = typer.Argument(..., help="Path to spec document (.xlsx, .md, .docx)"),
    spec_id: str = typer.Option(..., "--id", "-i", help="Identifier for this spec"),
    force: bool = typer.Option(False, "--force", "-f", help="Re-parse even if already loaded"),
) -> None:
    """Parse and register a spec document for later validation."""
    if not path.exists():
        err_console.print(f"[red]Error:[/red] File not found: {path}")
        raise typer.Exit(1)

    registry = _get_registry()
    try:
        spec = registry.load_spec(str(path), spec_id, force_reparse=force)
    except ValueError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    console.print(
        f"[green]Loaded[/green] spec [bold]{spec_id!r}[/bold] from [bold]{path}[/bold]\n"
        f"  Fields detected: {len(spec.fields)}\n"
        f"  Format: {spec.source_format}\n"
        f"  Title: {spec.title or '(none)'}"
    )


@app.command()
def validate(
    data_file: Path = typer.Argument(..., help="CSV or Excel data file to validate"),
    spec_id: str = typer.Option(..., "--spec", "-s", help="Spec ID to validate against"),
    output: str = typer.Option("rich", "--output", "-o", help="Output format: rich|json"),
    save: Optional[Path] = typer.Option(None, "--save", help="Save JSON report to file"),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", envvar="ANTHROPIC_API_KEY", help="Anthropic API key"
    ),
) -> None:
    """Validate a data file against a loaded spec document using Claude AI."""
    if not data_file.exists():
        err_console.print(f"[red]Error:[/red] File not found: {data_file}")
        raise typer.Exit(1)

    registry = _get_registry()
    try:
        spec = registry.get_spec(spec_id)
    except KeyError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    from spec_validator.parsers.data_parser import DataFileParser
    from spec_validator.validators.claude_validator import ClaudeValidator
    from spec_validator.reporters.rich_reporter import RichReporter
    from spec_validator.reporters.json_reporter import JsonReporter

    console.print(f"[dim]Parsing data file: {data_file}[/dim]")
    try:
        sample = DataFileParser().parse(str(data_file))
    except Exception as e:
        err_console.print(f"[red]Error parsing data file:[/red] {e}")
        raise typer.Exit(1)

    from spec_validator.config import settings
    resolved_key = api_key or settings.anthropic_api_key
    if not resolved_key:
        err_console.print(
            "[red]Error:[/red] No Anthropic API key found.\n"
            "Set [bold]ANTHROPIC_API_KEY[/bold] in your environment or .env file, "
            "or pass [bold]--api-key[/bold].\n"
            "[dim]Tip: Inside Claude Code, use the [bold]/validate[/bold] slash command "
            "instead — no API key required.[/dim]"
        )
        raise typer.Exit(1)

    console.print(
        f"[dim]Validating {sample.row_count:,} rows × {len(sample.columns)} columns "
        f"against spec '{spec_id}'...[/dim]"
    )
    try:
        result = ClaudeValidator(api_key=resolved_key).validate(spec, sample, data_file.name)
    except Exception as e:
        err_console.print(f"[red]Claude API error:[/red] {e}")
        raise typer.Exit(1)

    if output == "json":
        console.print(JsonReporter().to_string(result))
    else:
        RichReporter(console).print_result(result)

    if save:
        JsonReporter().save(result, str(save))
        console.print(f"\n[dim]Report saved to {save}[/dim]")

    raise typer.Exit(0 if result.passed else 1)


@app.command("list-specs")
def list_specs() -> None:
    """List all currently loaded spec documents."""
    registry = _get_registry()
    specs = registry.list_specs()

    if not specs:
        console.print("[dim]No specs loaded. Use `specval load-spec` to add one.[/dim]")
        return

    table = Table(title="Loaded Specs", show_lines=True)
    table.add_column("ID", style="bold")
    table.add_column("Format", width=8)
    table.add_column("Fields", justify="right", width=8)
    table.add_column("Source Path")
    table.add_column("Parsed At")

    for s in specs:
        table.add_row(
            s["spec_id"],
            s["source_format"],
            str(s["field_count"]),
            s["source_path"],
            s["parsed_at"][:19] if s["parsed_at"] else "",
        )
    console.print(table)


@app.command()
def report(
    result_file: Path = typer.Argument(..., help="Path to a saved JSON validation result"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format: rich|json"),
) -> None:
    """Display a saved validation report."""
    if not result_file.exists():
        err_console.print(f"[red]Error:[/red] File not found: {result_file}")
        raise typer.Exit(1)

    from spec_validator.models.validation import ValidationResult
    from spec_validator.reporters.rich_reporter import RichReporter
    from spec_validator.reporters.json_reporter import JsonReporter

    try:
        result = ValidationResult.model_validate_json(result_file.read_text(encoding="utf-8"))
    except Exception as e:
        err_console.print(f"[red]Error reading report:[/red] {e}")
        raise typer.Exit(1)

    if format == "json":
        console.print(JsonReporter().to_string(result))
    else:
        RichReporter(console).print_result(result)


@app.command("dump-spec")
def dump_spec(
    spec_id: str = typer.Argument(..., help="Spec ID to dump as JSON"),
) -> None:
    """Print the parsed spec document as JSON (for Claude Code slash commands)."""
    registry = _get_registry()
    try:
        spec = registry.get_spec(spec_id)
    except KeyError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    print(spec.model_dump_json(indent=2))


@app.command("dump-sample")
def dump_sample(
    data_file: Path = typer.Argument(..., help="CSV or Excel data file to parse"),
) -> None:
    """Parse a data file and print the sample as JSON (for Claude Code slash commands)."""
    if not data_file.exists():
        err_console.print(f"[red]Error:[/red] File not found: {data_file}")
        raise typer.Exit(1)
    from spec_validator.parsers.data_parser import DataFileParser
    try:
        sample = DataFileParser().parse(str(data_file))
    except Exception as e:
        err_console.print(f"[red]Error parsing data file:[/red] {e}")
        raise typer.Exit(1)
    print(sample.model_dump_json(indent=2))


@app.command("remove-spec")
def remove_spec(
    spec_id: str = typer.Argument(..., help="Spec ID to remove from registry"),
) -> None:
    """Remove a spec from the registry."""
    registry = _get_registry()
    try:
        registry.remove_spec(spec_id)
        console.print(f"[green]Removed[/green] spec [bold]{spec_id!r}[/bold]")
    except KeyError as e:
        err_console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
