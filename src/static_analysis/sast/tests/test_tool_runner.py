import unittest
from pathlib import Path

from sfa.analysis import SASTFlag, SASTFlags
from sfa.analysis.tool_runner import convert_sarif


class TestFlagSetSarif(unittest.TestCase):
    def setUp(self) -> None:
        self.sarif_file = Path(__file__).parent / "data" / "test.sarif"

    def test_convert_sarif(self) -> None:
        # Arrange
        expected = SASTFlags()
        expected.add(SASTFlag("sast-tool", "file1", 10, "Rule-1"))
        expected.add(SASTFlag("sast-tool", "file2", 20, "Rule-2"))

        # Act
        actual = convert_sarif(self.sarif_file.read_text())

        # Assert
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
