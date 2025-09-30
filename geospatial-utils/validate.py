# Validation script extensively inspired from https://github.com/UASGeoZones/ED-318/blob/main/examples/validate_examples.py

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema
from referencing import Registry, Resource

SCHEMA_PATH = Path(os.path.dirname(__file__)).parent / "schemas/ED-318/schema"
ROOT_SCHEMA = Path(SCHEMA_PATH) / "Schema_GeoZones.json"


@dataclass
class ValidationErrorWithPath:
    """Error encountered while validating an instance against a schema."""

    message: str
    """Validation error message."""

    json_path: str
    """Location of the data causing the validation error."""


def _collect_errors(e: jsonschema.ValidationError) -> list[ValidationErrorWithPath]:
    if e.context:
        result: list[ValidationErrorWithPath] = []
        for child in e.context:
            result.extend(_collect_errors(child))
        return result
    else:
        return [ValidationErrorWithPath(message=e.message, json_path=e.json_path)]


def _build_registry(schema_dir: Path) -> Registry:
    def retrieve(uri: str):
        local_ref = (schema_dir / Path(uri)).resolve()
        return Resource.from_contents(json.loads(local_ref.read_text()))

    registry: Registry = Registry(retrieve=retrieve)
    return registry


def ed318(data: dict[str, Any]) -> list[ValidationErrorWithPath]:
    """Validate the data object using ED-318 jsonschemas"""
    schema_content = json.loads(ROOT_SCHEMA.read_bytes())
    registry = _build_registry(SCHEMA_PATH)
    validator = jsonschema.Draft7Validator(schema=schema_content, registry=registry)
    validator.check_schema(schema_content)

    errors: list[ValidationErrorWithPath] = []
    for e in validator.iter_errors(data):  # type: ignore
        errors.extend(_collect_errors(e))

    return errors
