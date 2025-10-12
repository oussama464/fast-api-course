from parse_ddf import Schema , Column , SchemaValidationError
import pytest
def build_valid_schema(**overrides):
    base = {
        "version": 1,
        "title": "My Schema",
        "description": "optional",
        "properties": {
            "name": {"type": "string"},
            "is_active": {"type": "boolean"},
            "amount": {"type": "float"},
            "created_date": {"type": "date"},
            "event_date_time": {"type": "date-time"},
            "count": {"type": "integer"},
        },
    }
    base.update(overrides)
    return base

def test_schema_from_yaml_valid_minimal():
    data = {
        "version": 1,
        "title": "X",
        "properties": {"foo": {"type": "string"}},
    }
    s = Schema.from_yaml(data)
    assert s.version == 1
    assert s.title == "X"
    assert isinstance(s.properties["foo"], Column)
    assert s.properties["foo"].type == "string"
    assert s.properties["foo"].description is None

def test_unknown_top_level_keys_forbidden():
    data = build_valid_schema(extra="nope")
    with pytest.raises(SchemaValidationError) as e:
        Schema.from_yaml(data)
    assert "unknown top-level key" in str(e.value)


@pytest.mark.parametrize("bad_name", ["BadName", "snake-Case", "9start", "UPPER", "mixed_Case"])
def test_invalid_column_names_rejected(bad_name):
    data = build_valid_schema()
    data["properties"] = {bad_name: {"type": "string"}}
    with pytest.raises(SchemaValidationError) as e:
        Schema.from_yaml(data)
    assert "invalid column name; must be lower_snake_case" in str(e.value)


def test_column_forbids_extra_keys():
    with pytest.raises(SchemaValidationError) as e:
        Column.from_raw("foo", {"type": "string", "description": "ok", "extra": True})
    assert "unknown key(s)" in str(e.value)

def test_date_time_column_name_must_end_with_suffix():
    with pytest.raises(SchemaValidationError) as e:
        Column.from_raw("timestamp", {"type": "date-time"})
    assert "must end with '_date_time'" in str(e.value)













"""
Strict YAML schema validator.

Spec enforced:
- Top level keys allowed: version, title, description, properties.
- Required: version (int >=1), title (non-empty str), properties (mapping with >=1 entry).
- description: optional str.
- Column names: lower_snake_case: ^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$
- Column object: keys allowed -> type (required), description (optional). No others.
- type allowed: boolean, integer, float, date, date-time, string
  (Explicitly reject: time, enum — marked “to be implemented”)
- If type == date-time: column name must end with "_date_time"
"""
import re
from dataclasses import dataclass, field ,asdict
from pathlib import Path

from typing import Self, Any

import yaml
from pprint import pprint


# ----------------- dataclasses describing the expected structure -----------------

ALLOWED_TOP_KEYS = {"version", "title", "description", "properties"}
ALLOWED_TYPES = {"boolean", "integer", "float", "date", "date-time", "string"}
RESERVED_NOT_IMPLEMENTED = {"time", "enum"}
SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


class SchemaValidationError(Exception):
    pass


@dataclass
class Column:
    type: str
    description: str | None = None

    @classmethod
    def from_raw(cls,name: str, raw: Any) -> Self:
        if not isinstance(raw, dict):
            raise SchemaValidationError(
                f"properties.{name}: must be a mapping with keys 'type' and optional 'description'."
            )

        # Forbid extra keys
        extra = set(raw.keys()) - {"type", "description"}
        if extra:
            raise SchemaValidationError(
                f"properties.{name}: unknown key(s): {', '.join(sorted(extra))}."
            )

        # Required: type
        t = raw.get("type")
        if not isinstance(t, str):
            raise SchemaValidationError(f"properties.{name}.type: must be a string.")

        # Reject reserved types
        if t in RESERVED_NOT_IMPLEMENTED:
            raise SchemaValidationError(
                f"properties.{name}.type='{t}' is reserved and not implemented."
            )

        # Only allow current types
        if t not in ALLOWED_TYPES:
            allowed = ", ".join(sorted(ALLOWED_TYPES))
            raise SchemaValidationError(
                f"properties.{name}.type='{t}' is not allowed; allowed: {allowed}."
            )

        # Optional description
        desc = raw.get("description")
        if desc is not None and not isinstance(desc, str):
            raise SchemaValidationError(
                f"properties.{name}.description: must be a string if provided."
            )

        # Naming rule for date-time columns
        if t == "date-time":
            if not name.endswith("_date_time"):
                raise SchemaValidationError(
                    f"properties.{name}: 'date-time' columns must end with '_date_time'."
                )


        return cls(type=t, description=desc)


@dataclass
class Schema:
    version: int
    title: str
    description: str | None = None
    properties: dict[str, Column] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls,data: dict[str,Any]) -> Self:
        # Root must be a mapping
        if not isinstance(data, dict):
            raise SchemaValidationError("root: document must be a YAML mapping/object.")

        # Forbid unknown top-level keys
        unknown = set(data.keys()) - ALLOWED_TOP_KEYS
        if unknown:
            raise SchemaValidationError(
                f"root: unknown top-level key(s): {', '.join(sorted(unknown))}."
            )

        # Required fields
        version = data.get("version")
        if not isinstance(version, int) or version < 1:
            raise SchemaValidationError("version: must be an integer >= 1.")

        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            raise SchemaValidationError("title: must be a non-empty string.")

        # Optional description
        description = data.get("description")
        if description is not None and not isinstance(description, str):
            raise SchemaValidationError("description: must be a string if provided.")

        # properties
        props_raw = data.get("properties")
        if not isinstance(props_raw, dict) or not props_raw:
            raise SchemaValidationError(
                "properties: must be a non-empty mapping of column_name -> {type, description?}."
            )

        props: dict[str, Column] = {}
        for name, raw in props_raw.items():
            # Column name must be lower_snake_case
            if not isinstance(name, str) or not SNAKE_CASE_RE.match(name):
                raise SchemaValidationError(
                    f"properties.{name}: invalid column name; must be lower_snake_case."
                )
            props[name] = Column.from_raw(name, raw)

        return cls(version=version, title=title, description=description, properties=props)



def validate_file(path: Path) -> None:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            pprint(data)
        s = Schema.from_yaml(data)
        pprint(s)
        pprint(asdict(s))
    except yaml.YAMLError as e:
        raise SchemaValidationError(f"YAML parsing error: {e}") from e


def main() -> None:
    ddf_schema = Path(__file__).parent / "ddf.yaml"
    validate_file(ddf_schema)


if __name__ == "__main__":
    main()
