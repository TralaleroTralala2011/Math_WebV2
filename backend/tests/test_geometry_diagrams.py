import math
import unittest
from app.ai.engine.geometry_diagrams import (
    right_triangle_with_altitude, external_tangents_to_circle,
    triangle_3_4_5, triangle_from_sides, triangle_with_base_height,
    rectangle, square, circle, inscribed_rectangle, inscribed_right_triangle,
    parallelogram, trapezoid, polygon, regular_polygon, rhombus, kite, pyramid_projection, triangular_prism_projection, validate_geometry_diagram, inscribed_triangle_by_angles, circle_with_central_angle, graph_diagram, line_graph, quadratic_graph, trigonometric_graph,
)
from app.ai.engine.geometry_curriculum import generate

class GeometryDiagramTests(unittest.TestCase):
    def test_right_triangle_coordinates_are_not_isosceles_by_accident(self):
        d=triangle_3_4_5(3,4)
        p=d["points"]
        def dist(a,b): return math.dist(p[a],p[b])
        self.assertAlmostEqual(dist("A","B"),4)
        self.assertAlmostEqual(dist("A","C"),3)
        self.assertAlmostEqual(dist("B","C"),5)
        self.assertEqual(d["right_angle"],"A")

    def test_inscribed_triangle_uses_diameter_and_correct_side_lengths(self):
        d=inscribed_right_triangle(3,4,5); p=d["points"]
        self.assertAlmostEqual(math.dist(p["A"],p["B"]),5)
        self.assertAlmostEqual(math.dist(p["A"],p["C"]),3)
        self.assertAlmostEqual(math.dist(p["B"],p["C"]),4)
        self.assertAlmostEqual(d["circles"][0]["radius"],2.5)
        self.assertEqual(d["right_angle"],"C")

    def test_inscribed_rectangle_diagonal_matches_circle_diameter(self):
        d=inscribed_rectangle(3,4,5); p=d["points"]
        self.assertAlmostEqual(math.dist(p["A"],p["C"]),10)
        self.assertAlmostEqual(2*d["circles"][0]["radius"],10)

    def test_drawing_tool_builders_cover_common_shapes(self):
        shapes=[rectangle(8,3),square(5),circle(4),triangle_from_sides(3,4,5),triangle_with_base_height(8,5),parallelogram(8,4,2),trapezoid(8,4,3),polygon({"A":[0,0],"B":[2,0],"C":[1,3]}),regular_polygon(6,4),rhombus(8,6),kite(8,6),pyramid_projection(),triangular_prism_projection()]
        self.assertEqual(len(shapes),13)
        self.assertTrue(all(d["type"]=="geometry" and (len(d["segments"])>=3 or bool(d.get("circles"))) for d in shapes))
        self.assertTrue(all(not validate_geometry_diagram(d) for d in shapes))

    def test_graph_builders_return_finite_sampled_curves_and_axes_ranges(self):
        line = line_graph(2, -1, (-4, 4), (-10, 10))
        self.assertEqual(line["type"], "graph")
        self.assertEqual(line["x_range"], [-4.0, 4.0])
        self.assertEqual(line["curves"][0]["label"], "y=2x+(-1)")
        self.assertTrue(all(math.isfinite(v) for p in line["curves"][0]["points"] for v in p))
        quad = quadratic_graph(1, -4, 3, (-5, 5), (-5, 10))
        self.assertEqual(quad["marked_points"][0]["label"], "I(2; -1)")
        trig = trigonometric_graph("sin", (-math.pi, math.pi), (-1.5, 1.5))
        self.assertEqual(trig["type"], "graph")
        self.assertGreater(len(trig["curves"][0]["points"]), 100)

    def test_graph_diagram_rejects_bad_ranges_and_nonfinite_points(self):
        with self.assertRaises(ValueError):
            graph_diagram([{"points": [[0, 0], [1, 1]]}], (2, 2), (-1, 1))
        with self.assertRaises(ValueError):
            graph_diagram([{"points": [[0, 0], [1, float("nan")]]}], (0, 2), (-1, 1))

    def test_inscribed_triangle_and_central_angle_diagrams_are_valid(self):
        tri=inscribed_triangle_by_angles(60,50)
        self.assertFalse(validate_geometry_diagram(tri))
        self.assertEqual(tri["angle_labels"]["C"],70)
        central=circle_with_central_angle(100)
        self.assertFalse(validate_geometry_diagram(central))
        self.assertEqual(central["angle_labels"]["ACB"],50)

    def test_ai_circle_questions_attach_data_bound_diagrams(self):
        for _ in range(120):
            q=generate(10,"duong_tron","hard","duong_tron_Tiếp tuyến thử thách")
            if q["archetype"]=="inscribed_triangle_diameter":
                d=q["diagram"]; p=d["points"]
                self.assertAlmostEqual(math.dist(p["A"],p["B"]),2*d["circles"][0]["radius"])
            if q["archetype"]=="inscribed_rectangle_diagonal":
                d=q["diagram"]; p=d["points"]
                self.assertAlmostEqual(math.dist(p["A"],p["C"]),2*d["circles"][0]["radius"])

    def test_rectangle_preserves_requested_length_width_ratio(self):
        d = rectangle(5, 4)
        p = d["points"]
        self.assertAlmostEqual(math.dist(p["A"], p["B"]) / math.dist(p["B"], p["C"]), 5/4)
        self.assertAlmostEqual(d["aspect_ratio"]["ratio"], 5/4)
        self.assertEqual(validate_geometry_diagram(d), [])

    def test_validator_rejects_rectangle_whose_side_ratio_was_corrupted(self):
        d = rectangle(5, 4)
        d["points"]["C"] = [5, 5]
        errors = validate_geometry_diagram(d)
        self.assertTrue(any("perpendicular" in e or "side ratio" in e for e in errors))

    def test_validator_rejects_inscribed_vertex_outside_circle(self):
        d = inscribed_triangle_by_angles(60, 50)
        d["points"]["A"] = [0, 0]
        self.assertTrue(any("does not lie on its declared circle" in e for e in validate_geometry_diagram(d)))

    def test_altitude_diagram_is_computed_from_projection(self):
        d = right_triangle_with_altitude(6, 8)
        p = d["points"]
        self.assertAlmostEqual(math.dist(p["A"], p["B"]), 6)
        self.assertAlmostEqual(math.dist(p["A"], p["C"]), 8)
        self.assertAlmostEqual(math.dist(p["A"], p["H"]), 4.8)
        self.assertEqual(validate_geometry_diagram(d), [])

    def test_external_tangent_diagram_is_geometrically_consistent(self):
        d = external_tangents_to_circle(2)
        p = d["points"]
        self.assertAlmostEqual(math.dist(p["O"], p["A"]), 2)
        self.assertAlmostEqual(math.dist(p["P"], p["A"]), math.sqrt(12))
        self.assertAlmostEqual(math.dist(p["A"], p["B"]), 2*math.sqrt(3))
        self.assertEqual(validate_geometry_diagram(d), [])

if __name__=="__main__": unittest.main()
