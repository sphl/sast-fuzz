import unittest
from pathlib import Path

from sfa.logic import SASTFlag, SASTFlagSet, convert_sarif
from sfa.util.fs import get_parent


class TestFlagSetSarif(unittest.TestCase):
    def setUp(self) -> None:
        self.sarif_file = get_parent(Path(__file__), 2) / "data" / "test.sarif"

    def test_convert_sarif(self) -> None:
        # Arrange
        expected = SASTFlagSet()
        expected.add(SASTFlag("sast-tool", "file1", 10, "Rule-1"))
        expected.add(SASTFlag("sast-tool", "file2", 20, "Rule-2"))

        # Act
        actual = convert_sarif(self.sarif_file.read_text())

        # Assert
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
