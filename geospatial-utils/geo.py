def ensure_polygon_rings_winding_order(
    rings: list[list[list[float]]],
) -> list[list[list[float]]]:
    """
    Ensures the linear rings of a polygon are defined according to https://datatracker.ietf.org/doc/rfc7946/ 3.1.6.:
     "A linear ring MUST follow the right-hand rule with respect to the area it bounds, i.e., exterior rings are
     counterclockwise, and holes are clockwise."

     "For Polygons with more than one of these rings, the first MUST be the exterior ring, and any others MUST be
     interior rings.  The exterior ring bounds the surface, and the interior rings (if present) bound holes within the
     surface."
    """
    if not rings:
        return []

    rings = rings.copy()
    rings[0] = ensure_ring_counterclockwise(rings[0])
    for i in range(1, len(rings)):
        rings[i] = ensure_ring_clockwise(rings[i])
    return rings


def ensure_ring_clockwise(ring: list[list[float]]) -> list[list[float]]:
    if is_ring_clockwise(ring):
        return ring
    return list(reversed(ring))


def ensure_ring_counterclockwise(ring: list[list[float]]) -> list[list[float]]:
    if is_ring_clockwise(ring):
        return list(reversed(ring))
    return ring


def is_ring_clockwise(ring: list[list[float]]) -> bool:
    """
    Determines if a linear ring is clockwise.
    Implementation of the "Shoelace Formula" which yields a positive area if vertices go counter-clockwise and a negative one if they go clockwise.
    See https://en.wikipedia.org/wiki/Shoelace_formula and https://rosettacode.org/wiki/Shoelace_formula_for_polygonal_area#Python.
    """
    if (
        ring[0] == ring[-1]
    ):  # GeoJSON linear rings will have first and last coordinates equal
        ring = ring[:-1]
    return sum((c2[0] - c1[0]) * (c2[1] + c1[1]) for c1, c2 in zip(ring, ring[1:])) > 0
