import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.questions import get_topic_data


class VisualizationTraceTests(unittest.TestCase):
    def test_two_sum_optimal_trace_exists_and_is_structured(self):
        topic = get_topic_data("arrays-hashing")
        question = next(q for q in topic["questions"] if q["title"] == "Two Sum")
        approach = next(ap for ap in question["approaches"] if ap["badge"] == "Optimal")

        self.assertIn("visualization", approach)
        self.assertIsInstance(approach["visualization"], dict)
        self.assertEqual(approach["visualization"].get("type"), "two-sum-hashmap")
        self.assertGreater(len(approach["visualization"].get("steps", [])), 0)

        first_step = approach["visualization"]["steps"][0]
        self.assertEqual(first_step["currentLine"], 3)
        self.assertIn("variables", first_step)
        self.assertIn("dataStructures", first_step)
        self.assertIn("mainStructure", first_step)
        self.assertIn("secondaryStructure", first_step)
        self.assertIn("explanation", first_step)
        self.assertIn("workflow", first_step)
        self.assertIn("currentNode", first_step["workflow"])


if __name__ == "__main__":
    unittest.main()
