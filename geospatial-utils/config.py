from __future__ import annotations

from implicitdict import ImplicitDict, StringBasedDateTime
from uas_standards.eurocae_ed318 import TextShortType


class ConverterConfiguration(ImplicitDict):
    name: str
    ed318_additions: ED318Additions
    adjusters: list[str]


class ED318Additions(ImplicitDict):
    default_lang: str
    provider: list[TextShortType]
    description: list[TextShortType]
    technicalLimitation: list[TextShortType]
    issued: StringBasedDateTime
    otherGeoid: str
    feature_collection_bbox: list[float]
    collection_name: str
