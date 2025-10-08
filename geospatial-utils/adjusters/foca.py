from typing import Any

from uas_standards.eurocae_ed318 import (
    CodeAuthorityRole,
    CodeZoneType,
    ED318Schema,
    TextShortType,
)

# This file includes adjustments specific to Swiss FOCA.
# References:
# ED-269: https://www.bazl.admin.ch/dam/bazl/fr/dokumente/Fachleute/Geoinformationen/dokumentation_minimales_geodatenmodell_version_1.0.pdf.download.pdf/ZonesG%C3%A9ographiquesUAS_FR_V1_0.pdf
# ED-318: https://www.bazl.admin.ch/dam/bazl/fr/dokumente/Fachleute/Geoinformationen/dokumentation_minimales_geodatenmodell_uas_geozones_version_2.0.pdf.download.pdf/ZonesG%C3%A9ographiquesUAS_FR_V2_0.pdf

DEFAULT_LANG = "en-GB"

ED269_RESTRICTION_TEXT_EN = {
    "RST01": "The operation of unmanned aircraft is prohibited.",
    "RST02": "The operation of unmanned aircraft weighing more than 250 g is prohibited.",
    "RST03": "The operation of unmanned aircraft weighing more than 250 g is prohibited from an altitude of 120 m above ground.",
}

# Purposedly not used yet.
RESTRICTION_TEXT = {
    "REC02a": [
        TextShortType(
            lang="de-CH",
            text="Der Betrieb von unbemannten Luftfahrzeugen ist nur mit Ausnahmebewilligung erlaubt.",
        ),
        TextShortType(
            lang="fr-CH",
            text="L'exploitation d'aéronefs sans occupants n'est autorisée que avec une autorisation exceptionnelle.",
        ),
        TextShortType(
            lang="it-CH",
            text="L’esercizio di aeromobili senza occupanti è consentito solo con permesso d’esenzione.",
        ),
        TextShortType(
            lang="en-GB",
            text="The operation of unmanned aircraft is only allowed with exemption permit.",
        ),
    ],
    "REC02b": [
        TextShortType(
            lang="de-CH",
            text="Der Betrieb von unbemannten Luftfahrzeugen mit einem Gewicht von mehr als 250 g ist nur mit Ausnahmebewilligung erlaubt.",
        ),
        TextShortType(
            lang="fr-CH",
            text="L'exploitation d'aéronefs sans occupants d'un poids supérieur à 250 g n'est autorisée que avec une autorisation exceptionnelle.",
        ),
        TextShortType(
            lang="it-CH",
            text="L’esercizio di aeromobili senza occupanti di peso superiore a 250 g è consentito solo con permesso d’esenzione.",
        ),
        TextShortType(
            lang="en-GB",
            text="The operation of unmanned aircraft weighing more than 250 g is only allowed with exemption permit.",
        ),
    ],
    "REC02c": [
        TextShortType(
            lang="de-CH",
            text="Der Betrieb von unbemannten Luftfahrzeugen mit einem Gewicht von mehr als 250 g ist ab einer Höhe von 120 m über Grund nur mit Ausnahmebewilligung erlaubt.",
        ),
        TextShortType(
            lang="fr-CH",
            text="L'exploitation d'aéronefs sans occupants d'un poids supérieur à 250 g n'est autorisée que avec une autorisation exceptionnelle à partir d'une hauteur de 120 m audessus du sol.",
        ),
        TextShortType(
            lang="it-CH",
            text="L’esercizio di aeromobili senza occupanti di peso superiore a 250 g è consentito a partire da un’altezza di 120 m sopra il suolo solo con permesso d’esenzione.",
        ),
        TextShortType(
            lang="en-GB",
            text="The operation of unmanned aircraft weighing more than 250 g is only permitted from an altitude of 120 m above ground with exemption permit.",
        ),
    ],
    "REC05": [
        TextShortType(
            lang="de-CH",
            text="Der Betrieb von unbemannten Luftfahrzeugen ist zulässig.",
        ),
        TextShortType(
            lang="fr-CH", text="L'exploitation d'aéronefs sans occupants est permise."
        ),
        TextShortType(
            lang="it-CH", text="L’esercizio di aeromobili senza occupanti è consentito."
        ),
        TextShortType(
            lang="en-GB", text="The operation of unmanned aircraft is permitted."
        ),
    ],
}

RESTRICTION_TEXT_MAPPING = {"RST01": "REC02a", "RST02": "REC02b", "RST03": "REC02c"}

ADD_INFO_TEXT = {
    "EXP02": [
        TextShortType(
            lang="de-CH",
            text="Ausnahmebewilligungen können bei der zuständigen Stelle beantragt werden.",
        ),
        TextShortType(
            lang="fr-CH",
            text="Des autorisations exceptionnelles peuvent être demandées auprès de l’autorité compétente.",
        ),
        TextShortType(
            lang="it-CH",
            text="I permessi d’esenzione possono essere richiesti all’autorità competente.",
        ),
        TextShortType(
            lang="en-GB",
            text="Exemption permits may be applied for at the competent authority.",
        ),
    ],
    "EXP05": [
        TextShortType(lang="de-CH", text="Es gibt keine Einschränkungen."),
        TextShortType(lang="fr-CH", text="Il n'y a pas de restrictions."),
        TextShortType(lang="it-CH", text="Non ci sono restrizioni."),
        TextShortType(lang="en-GB", text="There are no restrictions"),
    ],
}


def _restriction_code(restriction_conditions: str | None, _type: CodeZoneType) -> str:
    if _type == CodeZoneType.NO_RESTRICTION:
        return "REC05"

    for code, text in ED269_RESTRICTION_TEXT_EN.items():
        if restriction_conditions == text:
            return RESTRICTION_TEXT_MAPPING[code]

    raise ValueError(
        f"CodeZoneType was {_type} rather than NO_RESTRICTION and no known ED-269 English restriction text matched '{restriction_conditions}'"
    )


def _add_info_text(_type: CodeZoneType) -> list[TextShortType]:
    if _type == CodeZoneType.REQ_AUTHORIZATION:
        return ADD_INFO_TEXT["EXP02"]
    elif _type == CodeZoneType.NO_RESTRICTION:
        return ADD_INFO_TEXT["EXP05"]
    else:
        raise ValueError(
            f"Cannot determine info text from CodeZoneType '{_type}'"
        )


def _adjust_restriction_conditions(
    restriction_conditions: str | None, _type: CodeZoneType
) -> str:
    restriction_code = _restriction_code(restriction_conditions, _type)

    for translation in RESTRICTION_TEXT[restriction_code]:
        if translation.lang == DEFAULT_LANG:
            return translation.text or ""

    raise ValueError(
        f"Could not find '{DEFAULT_LANG}' language in RESTRICTION_TEXT for code '{restriction_code}'"
    )


def _adjust_extended_properties(
    restriction_conditions: str | None, _type: CodeZoneType
) -> dict[str, list[TextShortType]]:
    restriction_code = _restriction_code(restriction_conditions, _type)

    return {
        "addInfoText": _add_info_text(_type),
        "requirementText": RESTRICTION_TEXT[restriction_code],
    }


def _adjust_purpose(_type: CodeZoneType) -> CodeAuthorityRole:
    if _type == CodeZoneType.REQ_AUTHORIZATION:
        return CodeAuthorityRole.AUTHORIZATION
    elif _type == CodeZoneType.NO_RESTRICTION:
        return CodeAuthorityRole.INFORMATION
    else:
        raise ValueError(f"CodeAuthorityRole not known for CodeZoneType '{_type}'")


def adjust(ed318_data: ED318Schema) -> dict[Any, str]:
    for f in ed318_data.features:
        if f.properties is not None:
            original_restriction_conditions = f.properties.restrictionConditions
            original_type = f.properties.type
            f.properties.restrictionConditions = _adjust_restriction_conditions(
                original_restriction_conditions, original_type
            )
            f.properties.extendedProperties = _adjust_extended_properties(
                original_restriction_conditions, original_type
            )
            if "zoneAuthority" in f.properties:
                for za in f.properties.zoneAuthority:
                    za.purpose = _adjust_purpose(original_type)

    return ed318_data
