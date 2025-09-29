from config import ED318Additions
from models.eurocae_ed318 import (
    Authority,
    CodeVerticalReferenceType,
    CodeWeekDayType,
    CodeZoneReasonType,
    CodeZoneType,
    DailyPeriod,
    DatasetMetadata,
    ED318Schema,
    ExtentCircle,
    Feature,
    Geometry,
    GeometryCollection,
    Point,
    Polygon,
    TextShortType,
    TimePeriod,
    UASZone,
    UomDistance,
    VerticalLayer,
)
from uas_standards.eurocae_ed269 import (
    ApplicableTimePeriod,
    ED269Schema,
    HorizontalProjectionType,
    Reason,
    Restriction,
    UASZoneAirspaceVolume,
    UASZoneAuthority,
    UomDimensions,
)

COUNTRY_REGION_MAPPING = {"CHE": 0, "LIE": 27}


def _convert_restriction(restriction: Restriction):
    if restriction is Restriction.REQ_AUTHORISATION:
        return CodeZoneType.REQ_AUTHORIZATION
    return restriction


def _convert_uom(uom_dimensions: UomDimensions):
    return UomDistance(uom_dimensions.lower())


def _convert_authority(za: UASZoneAuthority, default_lang: str) -> Authority:
    return Authority(
        name=[TextShortType(text=za.name, lang=default_lang)] if "name" in za else [],
        service=[TextShortType(text=za.service, lang=default_lang)]
        if "service" in za
        else [],
        contactName=[TextShortType(text=za.contactName, lang=default_lang)]
        if "contactName" in za
        else [],
        siteURL=za.siteURL if "siteURL" in za else None,
        email=TextShortType(text=za.email, lang=default_lang)
        if "email" in za
        else None,
        phone=za.phone if "phone" in za else None,
        purpose=za.purpose if "purpose" in za else None,
        intervalBefore=za.intervalBefore if "intervalBefore" in za else None,
    )


def _convert_geometry(g: UASZoneAirspaceVolume) -> Geometry:
    vertical_layer = VerticalLayer(
        upper=g.upperLimit if "upperLimit" in g else None,
        upperReference=CodeVerticalReferenceType(g.upperVerticalReference),
        lower=g.lowerLimit if "lowerLimit" in g else None,
        lowerReference=CodeVerticalReferenceType(g.lowerVerticalReference),
        uom=_convert_uom(g.uomDimensions),
    )

    hp = g.horizontalProjection
    if hp.type is HorizontalProjectionType.Circle:
        return Point(
            coordinates=hp.center if "center" in hp else None,
            extent=ExtentCircle(radius=hp.radius) if "radius" in hp else None,
            layer=vertical_layer,
        )
    else:
        return Polygon(
            type="Polygon",
            coordinates=hp.coordinates if "coordinates" in hp else None,
            layer=vertical_layer,
        )


def _convert_reason(reason: list[Reason] | None) -> list[CodeZoneReasonType]:
    result: list[CodeZoneReasonType] = []
    for r in reason or []:
        if r == Reason.FOREIGN_TERRITORY:
            raise NotImplementedError(
                "Reason FOREIGN_TERRITORY is not supported yet. (Value inexistent in ED-318)"
            )
        result.append(CodeZoneReasonType(r))
    return result


def _convert_applicability(a: ApplicableTimePeriod) -> TimePeriod:
    schedule: list[DailyPeriod] = []
    if "schedule" in a:
        for d in a.schedule or []:
            schedule.append(
                DailyPeriod(
                    day=CodeWeekDayType(d.day) if "day" in d else None,
                    startTime=d.startTime if "startTime" in d else None,
                    startEvent=None,
                    endTime=d.endTime if "endTime" in d else None,
                    endEvent=None,
                )
            )

    return TimePeriod(
        startDateTime=a.startDateTime if "startDateTime" in a else None,
        endDateTime=a.endDateTime if "endDateTime" in a else None,
        schedule=schedule,
    )


def from_ed269_to_ed318(ed269_data: ED269Schema, config: ED318Additions) -> ED318Schema:

    dataset_metadata = DatasetMetadata(
        validFrom=None,
        validTo=None,
        provider=config.provider,
        description=config.description,
        issued=config.issued,
        otherGeoid=config.otherGeoid,
    )

    features: list[Feature] = []
    for i, zv in enumerate(ed269_data.features):
        zone_authority: list[Authority] = []
        for za in zv.zoneAuthority:
            zone_authority.append(_convert_authority(za, config.default_lang))

        geometries: list[Geometry] = []
        for g in zv.geometry:
            geometries.append(_convert_geometry(g))

        if len(geometries) > 1:
            geometry = GeometryCollection(
                type="GeometryCollection", geometries=geometries
            )
        elif len(geometries) == 1:
            geometry = geometries[0]
        else:
            raise ValueError(f"No geometry found for geozone {zv.name}")

        feature = Feature(
            id=str(i),
            type="Feature",
            properties=UASZone(
                identifier=zv.identifier,
                country=zv.country,
                name=[TextShortType(text=zv.name, lang=config.default_lang)],
                type=_convert_restriction(zv.restriction),
                variant=zv.type,
                restrictionConditions=zv.restrictionConditions
                if "restrictionConditions" in zv
                else None,
                region=COUNTRY_REGION_MAPPING[zv.country],
                reason=_convert_reason(zv.reason) if "reason" in zv else None,
                otherReasonInfo=[
                    TextShortType(text=zv.otherReasonInfo, lang=config.default_lang)
                ],
                regulationExemption=zv.regulationExemption,
                message=[TextShortType(text=zv.message, lang=config.default_lang)]
                if "message" in zv
                else [],
                extendedProperties=zv.extendedProperties
                if "extendedProperties" in zv
                else None,
                limitedApplicability=[
                    _convert_applicability(a) for a in zv.applicability
                ],
                zoneAuthority=zone_authority,
                dataSource=None,
            ),
            geometry=geometry,
        )

        features.append(feature)

    return ED318Schema(
        type="FeatureCollection",
        metadata=dataset_metadata,
        features=features,
    )
