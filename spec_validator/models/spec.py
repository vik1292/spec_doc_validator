from enum import Enum
from pydantic import BaseModel, Field


class DataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    EMAIL = "email"
    URL = "url"
    ENUM = "enum"
    ANY = "any"


class NullPolicy(str, Enum):
    REQUIRED = "required"
    NULLABLE = "nullable"
    OPTIONAL = "optional"


class FieldSpec(BaseModel):
    name: str
    aliases: list[str] = Field(default_factory=list)
    data_type: DataType = DataType.ANY
    nullable: NullPolicy = NullPolicy.OPTIONAL
    allowed_values: list[str] | None = None
    min_value: float | None = None
    max_value: float | None = None
    pattern: str | None = None
    description: str = ""
    business_rules: list[str] = Field(default_factory=list)


class NamingConvention(BaseModel):
    pattern: str | None = None
    prefix: str | None = None
    suffix: str | None = None
    description: str = ""


class SpecDocument(BaseModel):
    spec_id: str
    source_path: str
    source_format: str
    title: str = ""
    description: str = ""
    version: str = ""
    fields: list[FieldSpec] = Field(default_factory=list)
    naming_convention: NamingConvention | None = None
    file_naming_pattern: str | None = None
    raw_content: str = ""
    parsed_at: str = ""
