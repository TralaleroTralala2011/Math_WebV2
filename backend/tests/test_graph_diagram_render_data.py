import math
import unittest
from app.ai.engine.geometry_diagrams import graph_diagram, line_graph, quadratic_graph, trigonometric_graph, ellipse_graph, hyperbola_graph, exponential_graph, logarithmic_graph
from app.ai.engine.topic_expansion import geometry_diagram


class GraphDiagramRenderDataTests(unittest.TestCase):
    def test_line_graph_matches_equation(self):
        d = line_graph(2, 3, (-2, 2), (-2, 8))
        curve = d["curves"][0]["points"]
        point = min(curve, key=lambda p: abs(p[0] - 1))
        self.assertAlmostEqual(point[1], 2 * point[0] + 3)
        self.assertEqual(d["type"], "graph")

    def test_quadratic_vertex_is_correct(self):
        d = quadratic_graph(1, -4, 3, (-5, 5), (-5, 10))
        self.assertAlmostEqual(d["marked_points"][0]["x"], 2)
        self.assertAlmostEqual(d["marked_points"][0]["y"], -1)

    def test_graph_fallback_detects_equation_from_question(self):
        d = geometry_diagram("ham_so_bac_hai", "Cho hàm số y=2x^2-3x+1. Tìm đỉnh parabol.", 0)
        self.assertEqual(d["type"], "graph")
        self.assertEqual(d["curves"][0]["label"], "y=2x^2-3x+1")
        self.assertAlmostEqual(d["marked_points"][0]["x"], 0.75)

    def test_trigonometric_graph_has_many_samples(self):
        d = trigonometric_graph("sin", (-math.pi, math.pi), (-1.5, 1.5))
        self.assertGreater(len(d["curves"][0]["points"]), 100)

    def test_conic_exponential_and_logarithmic_graph_builders(self):
        ellipse = ellipse_graph(4, 3)
        self.assertEqual(ellipse["type"], "graph")
        self.assertAlmostEqual(max(p[0] for p in ellipse["curves"][0]["points"]), 4)
        hyperbola = hyperbola_graph(2, 1)
        self.assertGreaterEqual(len(hyperbola["curves"]), 4)
        exponential = exponential_graph(2, (-3, 3), (0, 10))
        self.assertEqual(exponential["type"], "graph")
        logarithm = logarithmic_graph(2, (-0.5, 8), (-4, 4))
        self.assertTrue(any(a["value"] == 0 for a in logarithm["asymptotes"]))

    def test_standard_ellipse_equation_is_detected(self):
        d = geometry_diagram("elip", "Đồ thị elip x^2/16 + y^2/9 = 1.", 0)
        self.assertEqual(d["type"], "graph")
        self.assertAlmostEqual(max(p[0] for p in d["curves"][0]["points"]), 4)

    def test_invalid_graph_has_no_fabricated_curve(self):
        with self.assertRaises(ValueError):
            graph_diagram([{"label": "bad", "points": [[0, float("nan")], [1, float("inf")]]}], (-1, 1), (-1, 1))


if __name__ == "__main__":
    unittest.main()


def test_line_with_slope_and_point_draws_matching_cartesian_graph():
    from app.ai.engine.topic_expansion import geometry_diagram
    diagram = geometry_diagram(
        "duong_thang",
        "Tìm phương trình đường thẳng có hệ số góc -1 và đi qua P(0;4).",
        "y=-x+4",
    )
    assert diagram["type"] == "graph"
    assert diagram["curves"]
    assert any(abs(p["x"]) < 1e-9 and abs(p["y"] - 4) < 1e-9 and p["label"].startswith("P(") for p in diagram["marked_points"])
    curve_points = diagram["curves"][0]["points"]
    assert abs(curve_points[0][1] - (-(curve_points[0][0]) + 4)) < 1e-6


def test_difficulty_aliases_include_hell():
    from app.ai.engine.difficulty import normalize
    assert normalize("Địa ngục") == "hell"
    assert normalize("Nâng cao") == "hard"


def test_point_to_implicit_line_distance_diagram_includes_line_and_point():
    from app.ai.engine.topic_expansion import geometry_diagram
    diagram = geometry_diagram(
        "duong_thang",
        "Tính khoảng cách từ P(1;2) đến đường thẳng d: 1x -1y +2=0.",
        "0,7",
    )
    assert diagram["type"] == "graph"
    assert any("1x" in curve["label"] for curve in diagram["curves"])
    assert any(p["label"].startswith("P(1; 2)") for p in diagram["marked_points"])
