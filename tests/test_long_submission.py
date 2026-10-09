import json
import unittest

from validate_long_submission import unique_object, validate_task


class SubmissionValidationTest(unittest.TestCase):
    def setUp(self):
        self.examples = [{"id": "q", "gold_ids_long": ["a", "b"],
                          "excluded_ids": ["c", "N/A"]}]
        self.docs = ["a", "b", "c"]

    def test_recall_not_hit_rate(self):
        result = validate_task({"q": {"a": 1, "b": 0}}, self.examples, self.docs)
        self.assertEqual(result["Recall@1"], 0.5)

    def test_rejects_invalid_runs(self):
        for run in ({}, {"q": {}}, {"q": {"c": 1}}, {"q": {"a#0": 1}},
                    {"q": {"a": float("nan")}}, {"q": {"a": True}},
                    {"q": {"a": "1"}}, {"q": {"a": 1}, "extra": {"a": 1}}):
            with self.subTest(run=run), self.assertRaises(ValueError):
                validate_task(run, self.examples, self.docs)

    def test_duplicate_json_keys(self):
        with self.assertRaises(ValueError):
            json.loads('{"q":{"a":1,"a":2}}', object_pairs_hook=unique_object)


if __name__ == "__main__":
    unittest.main()
