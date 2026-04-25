from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from spec_validator.models.validation import Severity, ValidationResult

_SEVERITY_COLORS = {
    Severity.ERROR: "red",
    Severity.WARNING: "yellow",
    Severity.INFO: "cyan",
}


class RichReporter:
    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()

    def print_result(self, result: ValidationResult) -> None:
        self._print_header(result)
        if result.violations:
            self._print_violations_table(result)
        if result.summary:
            self._console.print(
                Panel(result.summary, title="[bold]Summary[/bold]", border_style="blue")
            )
        self._print_cache_stats(result)

    def _print_header(self, result: ValidationResult) -> None:
        if result.passed:
            status = Text("PASSED", style="bold green")
        else:
            status = Text("FAILED", style="bold red")

        header = (
            f"Status: {status}  |  Spec: [bold]{result.spec_id}[/bold]  "
            f"|  File: [bold]{result.data_file}[/bold]\n"
            f"Errors: [red]{result.error_count}[/red]  "
            f"Warnings: [yellow]{result.warning_count}[/yellow]  "
            f"Infos: [cyan]{sum(1 for v in result.violations if v.severity == Severity.INFO)}[/cyan]"
        )
        border = "green" if result.passed else "red"
        self._console.print(Panel(header, title="[bold]Spec Doc Validator[/bold]", border_style=border))

    def _print_violations_table(self, result: ValidationResult) -> None:
        table = Table(
            title="Violations",
            box=box.ROUNDED,
            show_lines=True,
            expand=True,
        )
        table.add_column("Severity", style="bold", width=10)
        table.add_column("Category", width=20)
        table.add_column("Field", width=20)
        table.add_column("Row", width=6, justify="right")
        table.add_column("Message", ratio=2)
        table.add_column("Suggestion", ratio=1)

        for v in result.violations:
            color = _SEVERITY_COLORS[v.severity]
            table.add_row(
                f"[{color}]{v.severity.value.upper()}[/{color}]",
                v.category.value,
                v.field_name or "",
                str(v.row_index) if v.row_index is not None else "",
                v.message,
                v.suggestion,
            )

        self._console.print(table)

    def _print_cache_stats(self, result: ValidationResult) -> None:
        hit = "[green]HIT[/green]" if result.cache_hit else "[yellow]MISS[/yellow]"
        self._console.print(
            f"\n[dim]Cache: {hit}  |  "
            f"Cached read: {result.cache_read_tokens:,}  |  "
            f"Cache write: {result.cache_write_tokens:,}  |  "
            f"Uncached input: {result.input_tokens:,}  |  "
            f"Output: {result.output_tokens:,}[/dim]"
        )
