import unittest

from geo import ensure_polygon_rings_winding_order, is_ring_clockwise


class IsRingClockwiseTestCase(unittest.TestCase):
    def test_square_clockwise(self):
        # Clockwise square
        ring = [[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]
        self.assertTrue(is_ring_clockwise(ring))

    def test_square_counter_clockwise(self):
        # Counter-clockwise square
        ring = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]
        self.assertFalse(is_ring_clockwise(ring))

    def test_triangle_clockwise(self):
        # Clockwise triangle
        ring = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [0.0, 0.0]]
        self.assertTrue(is_ring_clockwise(ring))

    def test_triangle_counter_clockwise(self):
        # Counter-clockwise triangle
        ring = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 0.0]]
        self.assertFalse(is_ring_clockwise(ring))

    def test_concave_clockwise(self):
        # Concave polygon (L-shape) clockwise
        ring = [
            [0.0, 0.0],
            [0.0, 2.0],
            [1.0, 2.0],
            [1.0, 1.0],
            [2.0, 1.0],
            [2.0, 0.0],
            [0.0, 0.0],
        ]
        self.assertTrue(is_ring_clockwise(ring))

    def test_concave_counter_clockwise(self):
        # Concave polygon (L-shape) clockwise
        ring = [
            [0.0, 0.0],
            [2.0, 0.0],
            [2.0, 1.0],
            [1.0, 1.0],
            [1.0, 2.0],
            [0.0, 2.0],
            [0.0, 0.0],
        ]
        self.assertFalse(is_ring_clockwise(ring))


class EnsurePolygonRingsWindingOrderTestCase(unittest.TestCase):
    def test_correct_winding_order(self):
        # Exterior: Clockwise square
        exterior = [[0.0, 0.0], [0.0, 5.0], [5.0, 5.0], [5.0, 0.0], [0.0, 0.0]]
        self.assertTrue(is_ring_clockwise(exterior))

        # Hole: Counter-clockwise square
        hole = [[1.0, 1.0], [4.0, 1.0], [4.0, 4.0], [1.0, 4.0], [1.0, 1.0]]
        self.assertFalse(is_ring_clockwise(hole))

        polygon = [exterior, hole]

        corrected_polygon = ensure_polygon_rings_winding_order(polygon)
        self.assertFalse(is_ring_clockwise(corrected_polygon[0]))
        self.assertTrue(is_ring_clockwise(corrected_polygon[1]))

    def test_already_correct_winding_order(self):
        # Exterior: Counter-clockwise square
        exterior = [[0.0, 0.0], [5.0, 0.0], [5.0, 5.0], [0.0, 5.0], [0.0, 0.0]]

        # Hole: Clockwise square
        hole = [[1.0, 1.0], [1.0, 4.0], [4.0, 4.0], [4.0, 1.0], [1.0, 1.0]]

        polygon = [exterior, hole]

        corrected_polygon = ensure_polygon_rings_winding_order(polygon)
        self.assertEqual(corrected_polygon, polygon)
        self.assertFalse(is_ring_clockwise(corrected_polygon[0]))
        self.assertTrue(is_ring_clockwise(corrected_polygon[1]))


if __name__ == "__main__":
    unittest.main()
