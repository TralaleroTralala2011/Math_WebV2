"""Regression tests for the additive geometry curriculum question bank."""
import unittest
from app.ai.engine.geometry_curriculum import generate


class GeometryCurriculumTests(unittest.TestCase):
    def test_grade_10_geometry_topics_are_relevant(self):
        expected = {
            "hinh_hoc_10": {"right_triangle", "triangle_area", "cosine_rule", "sine_rule", "bearing", "cosine_basic", "triangle_reverse"},
            "vector": {"vector_components", "vector_length", "dot_product", "midpoint", "collinearity"},
            "duong_tron": {"circle_equation", "circle_center_radius", "circle_tangent", "circle_intersection"},
            "duong_thang": {"distance_line", "line_through_point", "line_slope"},
        }
        for topic, families in expected.items():
            for level in ("easy", "medium", "hard"):
                for _ in range(20):
                    q = generate(10, topic, level)
                    self.assertIn(q["archetype"], families)
                    self.assertTrue(q["question"])
                    self.assertIsNotNone(q["answer"])
                    self.assertTrue(q["solution"])

    def test_grade_11_has_transformations_and_space_geometry(self):
        for topic, allowed in {
            "phep_bien_hinh_11": {"translation", "reflection", "rotation", "composition"},
            "hinh_khong_gian": {"parallel_planes", "line_plane_angle", "pyramid_section", "perpendicular_distance", "space_reasoning", "line_plane_position", "cube_diagonal"},
        }.items():
            for level in ("easy", "medium", "hard"):
                for _ in range(10):
                    self.assertIn(generate(11, topic, level)["archetype"], allowed)

    def test_grade_12_specialized_topics_stay_on_topic(self):
        for level in ("easy", "medium", "hard"):
            self.assertIn(generate(12, "mat_cau", level)["archetype"], {"sphere_equation", "sphere_center_radius", "sphere_point_check"})
            self.assertIn(generate(12, "duong_thang_oxyz", level)["archetype"], {"line_parametric"})
            self.assertIn(generate(12, "the_tich_khong_gian", level)["archetype"], {"pyramid_volume", "cylinder_volume", "sphere_surface", "cone_volume", "sphere_volume", "cube_volume"})

    def test_unknown_topic_falls_back_cleanly(self):
        self.assertIsNone(generate(10, "not_a_geometry_topic", "easy"))


if __name__ == "__main__":
    unittest.main()
