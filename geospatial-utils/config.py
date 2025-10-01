from __future__ import annotations

from datetime import datetime

from implicitdict import ImplicitDict, StringBasedDateTime
from uas_standards.eurocae_ed318 import TextShortType


class ConverterConfiguration(ImplicitDict):
    ed318_additions: ED318Additions


class ED318Additions(ImplicitDict):
    default_lang: str
    provider: list[TextShortType]
    description: list[TextShortType]
    technicalLimitation: list[TextShortType]
    issued: StringBasedDateTime
    otherGeoid: str
    feature_collection_bbox: list[float]
    collection_name: str


FOCA = ED318Additions(
    default_lang="en-GB",
    provider=[
        TextShortType(lang="de-CH", text="BAZL"),
        TextShortType(lang="fr-CH", text="OFAC"),
        TextShortType(lang="it-CH", text="UFAC"),
        TextShortType(lang="en-GB", text="FOCA"),
    ],
    description=[  # TODO: To validate
        TextShortType(
            lang="de-CH",
            text="Schweizerische UAS Geozones, herausgegeben vom Bundesamt für Zivilluftfahrt (BAZL). Umwandlung aus dem Modell ED-269.",
        ),
        TextShortType(
            lang="fr-CH",
            text="UAS Geozones suisses publiées par l'Office fédéral de l'aviation civile (OFAC). Conversion à partir du modèle ED-269",
        ),
        TextShortType(
            lang="it-CH",
            text="Geozones UAS svizzere emesse dall'Ufficio federale dell'aviazione civile (UFAC). Conversione dal modello ED-269",
        ),
        TextShortType(
            lang="en-GB",
            text="Swiss UAS Geozones issued by the Federal Office of Civil Aviation (FOCA). Conversion from the ED-269 model",
        ),
    ],
    technicalLimitation=[  # TODO: To validate
        TextShortType(
            lang="de-CH",
            text="Der Datensatz entsteht durch die Umwandlung der Originaldaten des ED-269-Modells ins neue ED-318. Für die Umwandlung sind einige Datenänderungen nötig. Diese Datei wurde in INTERLIS 2.4 erstellt.",
        ),
        TextShortType(
            lang="fr-CH",
            text="Le fichier a été créé en convertissant les données originales du modèle ED-269 dans le nouveau ED-318. La conversion nécessite des modifications des données. Ce fichier a été créé en INTERLIS 2.4",
        ),
        TextShortType(
            lang="it-CH",
            text="Il dataset è stato creato convertendo i dati originali del modello ED-269 nel nuovo ED-318. Per la conversione alcune modifiche dei dati sono necessarie. Questo file è stato creato in INTERLIS 2.4",
        ),
        TextShortType(
            lang="en-GB",
            text="The dataset was created by converting the original data from the ED-269 model to the new ED-318. Some data modifications are necessary for conversion. This file was created in INTERLIS 2.4",
        ),
    ],
    issued=StringBasedDateTime(datetime.now()),
    otherGeoid="CHGeo2004",
    collection_name="Swiss UAS Geozones according to ED-318 converted from the ED-269 data model",
    feature_collection_bbox=[2485410.215, 1075268.136, 2833857.724, 1295933.698],
)
