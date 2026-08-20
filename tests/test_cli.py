import json
import tempfile
import unittest
from pathlib import Path

from logdock.cli import ENV_DEFAULTS, init_project


class InitProjectTests(unittest.TestCase):
    def test_creates_default_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "sample-app"
            init_project(root)

            config = json.loads((root / "logdock.json").read_text(encoding="utf-8"))
            self.assertEqual(config["app_name"], "sample-app")
            self.assertFalse(config["notification"]["enabled"])
            self.assertFalse(config["persistence"]["enabled"])

            env = (root / ".env.example").read_text(encoding="utf-8")
            local = json.loads(
                (root / "local.settings.json.example").read_text(encoding="utf-8")
            )
            for name in ENV_DEFAULTS:
                self.assertIn(f"{name}=", env)
                self.assertIn(name, local["Values"])

    def test_preserves_existing_files_and_adds_missing_variables(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "logdock.json"
            config_path.write_text('{"custom": true}\n', encoding="utf-8")
            (root / ".env.example").write_text("CUSTOM=value\n", encoding="utf-8")
            (root / "local.settings.json.example").write_text(
                '{"Values": {"CUSTOM": "value"}}\n', encoding="utf-8"
            )

            init_project(root, app_name="ignored")

            self.assertEqual(config_path.read_text(encoding="utf-8"), '{"custom": true}\n')
            self.assertIn("CUSTOM=value", (root / ".env.example").read_text(encoding="utf-8"))
            local = json.loads(
                (root / "local.settings.json.example").read_text(encoding="utf-8")
            )
            self.assertEqual(local["Values"]["CUSTOM"], "value")
            self.assertTrue(set(ENV_DEFAULTS).issubset(local["Values"]))


if __name__ == "__main__":
    unittest.main()
