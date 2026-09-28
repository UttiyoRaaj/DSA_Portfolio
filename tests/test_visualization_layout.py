import unittest
from pathlib import Path


class VisualizationLayoutTests(unittest.TestCase):
    def test_visualization_shell_uses_split_panels_with_left_input_area(self):
        template_path = Path(__file__).resolve().parent.parent / "templates" / "question.html"
        content = template_path.read_text(encoding="utf-8")

        self.assertIn("visualization-split-shell", content)
        self.assertIn("visualization-pane-left", content)
        self.assertIn("visualization-pane-right", content)
        self.assertIn("data-splitter", content)
        self.assertIn("visualization-input-panel", content)


if __name__ == "__main__":
    unittest.main()
