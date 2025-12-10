import unittest
import json
import os


from playbook_demo import run_demo


class PlaybookDemoTest(unittest.TestCase):
    def test_run_demo_creates_output(self):
        out = run_demo()
        self.assertIn("iocs", out)
        self.assertIn("risk_score", out)
        self.assertTrue(os.path.exists("playbook_output.json"))
        with open("playbook_output.json", "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertEqual(data.get("risk_score"), out.get("risk_score"))


if __name__ == "__main__":
    unittest.main()
