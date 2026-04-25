import json
from pathlib import Path

from spec_validator.models.spec import SpecDocument
from spec_validator.parsers.base import BaseSpecParser
from spec_validator.parsers.excel_parser import ExcelSpecParser
from spec_validator.parsers.markdown_parser import MarkdownSpecParser
from spec_validator.parsers.word_parser import WordSpecParser


class SpecRegistry:
    def __init__(self, registry_path: Path | None = None) -> None:
        from spec_validator.config import settings

        self._path = registry_path or settings.registry_path
        self._specs: dict[str, SpecDocument] = {}
        self._parsers: list[BaseSpecParser] = [
            ExcelSpecParser(),
            MarkdownSpecParser(),
            WordSpecParser(),
        ]
        self._load()

    def load_spec(
        self, path: str, spec_id: str, force_reparse: bool = False
    ) -> SpecDocument:
        if spec_id in self._specs and not force_reparse:
            return self._specs[spec_id]

        parser = self._auto_detect_parser(path)
        spec = parser.parse(path, spec_id)
        self._specs[spec_id] = spec
        self._save()
        return spec

    def get_spec(self, spec_id: str) -> SpecDocument:
        if spec_id not in self._specs:
            raise KeyError(f"Spec '{spec_id}' not found. Load it first with `specval load-spec`.")
        return self._specs[spec_id]

    def list_specs(self) -> list[dict]:
        return [
            {
                "spec_id": s.spec_id,
                "source_path": s.source_path,
                "source_format": s.source_format,
                "field_count": len(s.fields),
                "parsed_at": s.parsed_at,
            }
            for s in self._specs.values()
        ]

    def remove_spec(self, spec_id: str) -> None:
        if spec_id not in self._specs:
            raise KeyError(f"Spec '{spec_id}' not found.")
        del self._specs[spec_id]
        self._save()

    def _auto_detect_parser(self, path: str) -> BaseSpecParser:
        for parser in self._parsers:
            if parser.can_parse(path):
                return parser
        suffix = Path(path).suffix.lower()
        raise ValueError(
            f"No parser available for '{suffix}'. "
            "Supported formats: .xlsx, .xls, .md, .markdown, .docx"
        )

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {sid: spec.model_dump() for sid, spec in self._specs.items()}
        self._path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            self._specs = {sid: SpecDocument(**v) for sid, v in data.items()}
        except (json.JSONDecodeError, Exception):
            self._specs = {}
