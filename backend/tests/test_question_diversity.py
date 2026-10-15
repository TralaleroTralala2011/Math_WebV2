import random
import unittest

from app.ai.engine.geometry_curriculum import generate as generate_geometry
from app.ai.engine.super_bank import _system_construct
from app.ai.engine.service import AIQuestionService
from app.ai.engine.topic_expansion import geometry_diagram


class QuestionDiversityTests(unittest.TestCase):
    def test_linear_system_bank_has_multiple_archetypes(self):
        random.seed(9217)
        medium = {_system_construct("medium")["archetype"] for _ in range(100)}
        hard = {_system_construct("hard")["archetype"] for _ in range(100)}
        archetypes = medium | hard
        self.assertGreaterEqual(len(medium), 3)
        self.assertGreaterEqual(len(hard), 3)
        self.assertIn("system_word_problem", archetypes)
        self.assertIn("system_solution_check", archetypes)
        self.assertIn("system_sum_difference", archetypes)

    def test_grade_10_plane_geometry_covers_three_levels(self):
        random.seed(1234)
        expected = {
            "easy": {"rectangle_area", "square_perimeter", "triangle_angles", "circle_radius", "parallel_angles", "triangle_area"},
            "medium": {"similar_triangles", "rhombus_area", "cyclic_quadrilateral", "tangent_radius", "trapezoid_area", "circle_chord"},
            "hard": {"angle_bisector", "tangent_secant", "triangle_median", "cyclic_power", "similarity_reverse", "geometry_proof"},
        }
        for level, families in expected.items():
            seen = {generate_geometry(10, "hinh_hoc_10", level)["archetype"] for _ in range(80)}
            self.assertTrue(seen.issubset(families))
            self.assertGreaterEqual(len(seen), 4)

    def test_game_system_levels_have_distinct_complexity(self):
        service = AIQuestionService()
        bank = service.generator.game_bank
        for method_name in ("system_investigation", "system_value", "system_match"):
            method = getattr(bank, method_name)
            easy = {method("easy").get("archetype") for _ in range(30)}
            hard = {method("hard").get("archetype") for _ in range(60)}
            self.assertTrue(all(value is not None for value in easy))
            self.assertTrue(all(value is not None for value in hard))
            self.assertGreaterEqual(len(hard), 2)
            self.assertTrue(easy.isdisjoint(hard) or len(hard - easy) >= 1)

    def test_geometry_diagrams_are_not_one_reused_triangle(self):
        examples = [
            ("hinh_hoc_10", "Hình chữ nhật ABCD có AB=8 cm, BC=4 cm. Tính diện tích."),
            ("duong_tron", "Hình chữ nhật ABCD nội tiếp đường tròn tâm O. Tính đường chéo."),
            ("duong_tron", "Tam giác ABC nội tiếp đường tròn có AB là đường kính. Tính góc C."),
            ("hinh_hoc_10", "Đường tròn tâm O có đường kính AB=10 cm. Tính bán kính."),
            ("hinh_hoc_10", "Tam giác ABC có góc A=50°. Tính góc B."),
            ("hinh_khong_gian", "Trong hình chóp S.ABCD, tìm giao tuyến."),
        ]
        diagrams = [geometry_diagram(topic, question, "5") for topic, question in examples]
        kinds = {d["type"] for d in diagrams}
        self.assertGreaterEqual(len(kinds), 4)
        self.assertTrue(any(d.get("shape") == "rectangle" for d in diagrams))
        self.assertIn("circle_inscribed_triangle", kinds)


if __name__ == "__main__":
    unittest.main()
