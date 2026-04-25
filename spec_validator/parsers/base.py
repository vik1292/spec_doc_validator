from abc import ABC, abstractmethod

from spec_validator.models.spec import SpecDocument


class BaseSpecParser(ABC):
    @abstractmethod
    def parse(self, path: str, spec_id: str) -> SpecDocument:
        ...

    @abstractmethod
    def can_parse(self, path: str) -> bool:
        ...
