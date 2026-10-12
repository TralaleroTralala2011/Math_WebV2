"""Regression tests for MATH WEB's additive multi-part problem mode."""
import unittest
import os
import tempfile
from math import comb

from app.ai.engine.service import AIQuestionService
from app.ai.engine.question_history import QuestionHistory


class ProblemGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._old_db_path = os.environ.get("MATHWEB_DB_PATH")
        cls._temp_dir = tempfile.TemporaryDirectory(prefix="mathweb-ai-tests-")
        os.environ["MATHWEB_DB_PATH"] = os.path.join(cls._temp_dir.name, "test.db")
        cls.service = AIQuestionService()

    @classmethod
    def tearDownClass(cls):
        if cls._old_db_path is None:
            os.environ.pop("MATHWEB_DB_PATH", None)
        else:
            os.environ["MATHWEB_DB_PATH"] = cls._old_db_path
        cls._temp_dir.cleanup()

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

    def test_mixed_question_set_contains_multiple_answer_modes(self):
        result = self.service.generate_set(11, ["xac_suat_11"], 9, "medium", "mixed")
        kinds = {q["question_type"] for q in result["questions"]}
        self.assertEqual(kinds, {"multiple_choice", "short_answer", "true_false"})

    def test_exact_question_history_persists_and_blocks_repeats(self):
        history = QuestionHistory()
        item = {
            "question": "Cho f(x)=x^2. Tính f(3).",
            "topic": "ham_so",
            "grade": 10,
            "difficulty": "easy",
            "structure_fingerprint": "test-structure",
            "archetype": "function_evaluate",
        }
        self.assertFalse(history.question_seen(item["question"]))
        history.record_question(item)
        self.assertTrue(history.question_seen(item["question"]))
        # A fresh history object represents a new request / service instance.
        self.assertTrue(QuestionHistory().question_seen(item["question"]))

    def test_problem_history_blocks_repeated_scenario_signature(self):
        history = QuestionHistory()
        signature = "probability_selection | Bài toán xác suất | Một lớp có 10 học sinh."
        self.assertFalse(history.problem_seen(signature))
        history.record_problem("xac_suat_11", 11, "medium", "probability_selection", signature)
        self.assertTrue(QuestionHistory().problem_seen(signature))

    def test_multiple_choice_server_accepts_displayed_correct_value(self):
        problem = self.service.problem_generator.generate(11, "xac_suat_11", "medium", 4)
        for part in problem["parts"]:
            if part["question_type"] == "multiple_choice":
                self.assertTrue(self.service._check(part, part["answer"]))


if __name__ == "__main__":
    unittest.main()
