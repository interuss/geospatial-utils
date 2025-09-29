import json
import pathlib

from uas_standards.eurocae_ed269 import ED269Schema


def loads(f: pathlib.Path) -> ED269Schema:
    json_body = json.loads(f.read_text(encoding="utf-8"))
    return ED269Schema.from_dict(json_body)
