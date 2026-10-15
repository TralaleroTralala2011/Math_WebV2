"""Regression tests for the additive geometry curriculum question bank."""
import unittest
from app.ai.engine.geometry_curriculum import generate


class GeometryCurriculumTests(unittest.TestCase):
    def test_grade_10_geometry_topics_are_relevant(self):
        expected = {
            "hinh_hoc_10": {"rectangle_area", "square_perimeter", "triangle_angles", "circle_radius", "parallel_angles", "triangle_area", "similar_triangles", "rhombus_area", "cyclic_quadrilateral", "tangent_radius", "trapezoid_area", "circle_chord", "angle_bisector", "tangent_secant", "triangle_median", "cyclic_power", "similarity_reverse", "geometry_proof"},
            "vector": {"vector_components", "vector_length", "dot_product", "midpoint", "collinearity"},
            "duong_tron": {"circle_equation", "circle_center_radius", "circle_tangent", "circle_intersection", "circle_angle", "inscribed_triangle_angle", "inscribed_triangle_diameter", "inscribed_rectangle_diagonal", "inscribed_rectangle_area", "rectangle_max_area", "external_tangents"},
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


    def test_geometry_game_modes_are_topic_specific(self):
        for level in ("easy", "medium", "hard"):
            angle = generate(10, "he_thuc_luong_tam_giac", level, "he_thuc_luong_tam_giac_Giải mã góc_variety")
            length = generate(10, "he_thuc_luong_tam_giac", level, "he_thuc_luong_tam_giac_Săn cạnh tam giác_variety")
            application = generate(10, "he_thuc_luong_tam_giac", level, "he_thuc_luong_tam_giac_Ứng dụng tam giác_variety")
            self.assertIn(angle["archetype"], {"cosine_rule", "sine_rule", "cosine_basic"})
            self.assertIn(length["archetype"], {"right_triangle", "triangle_area", "triangle_reverse", "altitude_multi_step"})
            self.assertIn(application["archetype"], {"bearing", "triangle_reverse", "triangle_area"})

            circle_angle = generate(10, "duong_tron", level, "duong_tron_Góc nội tiếp bí ẩn_variety")
            circle_length = generate(10, "duong_tron", level, "duong_tron_Truy tìm bán kính_variety")
            circle_application = generate(10, "duong_tron", level, "duong_tron_Tiếp tuyến thử thách_variety")
            self.assertIn(circle_angle["archetype"], {"circle_angle", "inscribed_triangle_angle", "inscribed_triangle_diameter"})
            self.assertIn(circle_length["archetype"], {"circle_center_radius", "circle_intersection", "inscribed_rectangle_diagonal", "inscribed_rectangle_area"})
            self.assertIn(circle_application["archetype"], {"circle_tangent", "circle_intersection", "inscribed_rectangle_diagonal", "inscribed_rectangle_area", "rectangle_max_area", "inscribed_triangle_diameter"})

    def test_circle_bank_includes_inscribed_rectangle_and_triangle(self):
        seen = {generate(10, "duong_tron", level)["archetype"] for level in ("easy", "medium", "hard") for _ in range(80)}
        self.assertIn("inscribed_triangle_angle", seen)
        self.assertIn("inscribed_triangle_diameter", seen)
        self.assertIn("inscribed_rectangle_diagonal", seen)
        self.assertIn("rectangle_max_area", seen)
        for _ in range(50):
            q = generate(10, "duong_tron", "hard", "duong_tron_Tiếp tuyến thử thách_variety")
            self.assertTrue(q["question"] and q["solution"])
            self.assertIsNotNone(q["answer"])

    def test_unknown_topic_falls_back_cleanly(self):
        self.assertIsNone(generate(10, "not_a_geometry_topic", "easy"))


if __name__ == "__main__":
    unittest.main()
