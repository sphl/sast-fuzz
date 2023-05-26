import unittest
from pathlib import Path

from sfa.logic import SASTToolFlag, SASTToolFlags, convert_sarif
from sfa.util.io import read


class TestConvertSarif(unittest.TestCase):
    def setUp(self) -> None:
        self.sarif_file = Path("data") / "test.sarif"

    def test_convert_sarif(self):
        # Arrange
        expected = SASTToolFlags()
        expected.add(SASTToolFlag("sast-tool", "file1", 10, "Rule-1"))
        expected.add(SASTToolFlag("sast-tool", "file2", 20, "Rule-2"))

        # Act
        actual = convert_sarif(read(self.sarif_file))

        # Assert
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
