import unittest
from inspect import getsourcefile
from os.path import abspath
from pathlib import Path

from typer.testing import CliRunner

from cli import app
from tests.TestBase import TestBase

THIS_DIR = Path(__file__).parent


class TestCLI(TestBase):
    def setUp(self):
        super().setUp()

        self.runner = CliRunner()

    def test_general(self):
        # Not found
        result = self.runner.invoke(app, ["anonymize", "-f", "notFound.json"])
        self.assertEqual(1, result.exit_code)

        result = self.runner.invoke(app, ["do_something_wrong", "-f", "notFound.json"])
        self.assertIn('Error: No such command', result.stdout)

    def test_anonymizer(self):
        file = THIS_DIR.parent / "tests/files/config_anonymizer_example.json"
        result = self.runner.invoke(app, ["anonymize", "-f", file])
        self.assertEqual(0, result.exit_code)


if __name__ == '__main__':
    unittest.main()
