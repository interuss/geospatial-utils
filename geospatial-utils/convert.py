from config import ED318Additions
from uas_standards.eurocae_ed318 import (
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


def _convert_restriction(restriction: Restriction) -> CodeZoneType:
    if restriction is Restriction.REQ_AUTHORISATION:
        return CodeZoneType.REQ_AUTHORIZATION
    return CodeZoneType(restriction)


def _convert_uom(uom_dimensions: UomDimensions) -> UomDistance:
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
        email=za.email if "email" in za else None,
        phone=za.phone if "phone" in za and za.phone else None,
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

    return Polygon(
        type="Polygon",
        coordinates=hp.coordinates if "coordinates" in hp else None,
        layer=vertical_layer,
    )


def _convert_reasons(reason: list[Reason] | None) -> list[CodeZoneReasonType] | None:
    reason_types: list[CodeZoneReasonType] = []
    for r in reason or []:
        if r == Reason.FOREIGN_TERRITORY:
            raise NotImplementedError(
                "Reason FOREIGN_TERRITORY is not supported yet. (Value inexistent in ED-318)"
            )
        reason_types.append(CodeZoneReasonType(r))
    return reason_types if len(reason_types) > 0 else None


def _convert_applicability(a: ApplicableTimePeriod) -> TimePeriod | None:
    schedule: list[DailyPeriod] = []
    if "schedule" in a:
        for d in a.schedule or []:
            daily_period = DailyPeriod(
                day=CodeWeekDayType(d.day) if "day" in d else None,
                startTime=d.startTime if "startTime" in d else None,
                startEvent=None,
                endTime=d.endTime if "endTime" in d else None,
                endEvent=None,
            )

            if len(daily_period) > 0:
                schedule.append(daily_period)

    time_period = TimePeriod(
        startDateTime=a.startDateTime if "startDateTime" in a else None,
        endDateTime=a.endDateTime if "endDateTime" in a else None,
        schedule=schedule if len(schedule) > 0 else None,
    )
    return time_period if len(time_period) > 0 else None


def from_ed269_to_ed318(ed269_data: ED269Schema, config: ED318Additions) -> ED318Schema:
    """Convert ED269 data to ED318 data.
    Missing data in the new format is provided as a config."""

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

        limited_applicability = [_convert_applicability(a) for a in zv.applicability]

        # Ensures it is not a table of None since permanent zone may be represented like this.
        if (
            sum(
                [
                    1 if la is not None and len(la) > 0 else 0
                    for la in limited_applicability
                ]
            )
            == 0
        ):
            limited_applicability = None

        # Ensures the converter accepts either an optional string as specified in the standard
        # definition or a list of str of 0 or 1 item as provided in the jsonschema in the standard.
        restriction_conditions: str | None = None
        if "restrictionConditions" in zv and zv.restrictionConditions is not None:
            if isinstance(zv.restrictionConditions, dict):
                if len(zv.restrictionConditions) == 0:
                    restriction_conditions = None
                elif len(zv.restrictionConditions) == 1:
                    restriction_conditions = zv.restrictionConditions[0]
                else:
                    raise ValueError("Unexpected array with more than one item.")
            else:
                restriction_conditions = str(zv.restrictionConditions)

        feature = Feature(
            id=str(i),
            type="Feature",
            properties=UASZone(
                identifier=zv.identifier,
                country=zv.country,
                name=[TextShortType(text=zv.name, lang=config.default_lang)],
                type=_convert_restriction(zv.restriction),
                variant=zv.type,
                restrictionConditions=restriction_conditions,
                region=COUNTRY_REGION_MAPPING[zv.country],
                reason=_convert_reasons(zv.reason) if "reason" in zv else None,
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
                limitedApplicability=limited_applicability,
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
