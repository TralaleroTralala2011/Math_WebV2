"""Regression tests for MATH WEB's additive multi-part problem mode."""
import unittest
from math import comb

from app.ai.engine.service import AIQuestionService


class ProblemGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = AIQuestionService()

    def test_curriculum_topics_generate_complete_problems(self):
        count = 0
        for grade in (10, 11, 12):
            for topic in self.service.topics(grade):
                problem = self.service.problem_generator.generate(grade, topic["id"], "medium", 4)
                self.assertTrue(problem["title"])
                self.assertTrue(problem["context"])
                self.assertEqual(len(problem["parts"]), 4)
                self.assertEqual([p["part"] for p in problem["parts"]], ["a", "b", "c", "d"])
                for part in problem["parts"]:
                    self.assertTrue(part["question"])
                    self.assertTrue(part["solution"])
                    self.assertIsNotNone(part["answer"])
                    if part["question_type"] == "multiple_choice":
                        values = [str(option["value"]) for option in part["options"]]
                        self.assertEqual(len(values), 4)
                        self.assertEqual(len(set(values)), 4)
                        self.assertIn(str(part["answer"]), values)
                count += 1
        self.assertGreaterEqual(count, 80)

    def test_probability_selection_counts(self):
        for _ in range(100):
            problem = self.service.problem_generator._build_probability_selection(11, "xac_suat_11", "medium")
            data = problem["data"]
            a, b, k = data["class_11a"], data["class_11b"], data["group_size"]
            total = comb(a + b, k)
            all_a = comb(a, k)
            both = total - all_a - comb(b, k)
            favorable = comb(a, k - 1) * comb(b, 1)
            conditional_total = total - all_a
            self.assertEqual(data["total_groups"], total)
            self.assertEqual(data["all_a_groups"], all_a)
            self.assertEqual(data["both_classes_groups"], both)
            self.assertEqual(data["conditional_favorable"], favorable)
            self.assertEqual(data["conditional_total"], conditional_total)

    def test_requested_part_counts_two_through_six(self):
        for count in range(2, 7):
            problem = self.service.problem_generator.generate(11, "xac_suat_11", "medium", count)
            self.assertEqual(len(problem["parts"]), count)
            self.assertEqual([p["part"] for p in problem["parts"]], list("abcdef")[:count])

    def test_multiple_choice_server_accepts_displayed_correct_value(self):
        problem = self.service.problem_generator.generate(11, "xac_suat_11", "medium", 4)
        for part in problem["parts"]:
            if part["question_type"] == "multiple_choice":
                self.assertTrue(self.service._check(part, part["answer"]))


if __name__ == "__main__":
    unittest.main()
