"""Test the primary run script."""
from unittest import TestCase

from click.testing import CliRunner

from run import merge, transform


class TestRun(TestCase):
    """Test the run.py script."""

    def setUp(self) -> None:
        """Set up the run script tests."""
        self.runner = CliRunner()

    def test_transform(self):
        """Test the transform command."""
        result = self.runner.invoke(cli=transform, args=["-i", "tests/data/raw"])
        self.assertNotEqual(result.exit_code, 0)

    def test_merge_missing_file_error(self):
        """Test the merge command, as when a file is missing."""
        with self.assertRaises(FileNotFoundError):
            result = self.runner.invoke(
                catch_exceptions=False,
                cli=merge,
                args=["-y", "tests/resources/merge_MISSING_FILE.yaml"],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertRegexpMatches(result.output, "does not exist")
