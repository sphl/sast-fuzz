import os
import unittest
from pathlib import Path

from sfa.logic import SASTToolFlags, SASTToolFlag, CSV_SEP


class TestSASTToolFlags(unittest.TestCase):
    def setUp(self):
        self.flags = SASTToolFlags()
        self.flags.add(SASTToolFlag("ToolA", "FileA", 10, "VulnA"))
        self.flags.add(SASTToolFlag("ToolB", "FileB", 20, "VulnB"))

    def test_add(self):
        # Arrange
        flag = SASTToolFlag("ToolC", "FileC", 30, "VulnC")

        # Act
        self.flags.add(flag)

        # Assert
        self.assertIn(flag, self.flags)

    def test_remove(self):
        # Arrange
        flag = SASTToolFlag("ToolA", "FileA", 10, "VulnA")

        # Act
        self.flags.remove(flag)

        # Assert
        self.assertNotIn(flag, self.flags)

    def test_to_csv(self):
        # Arrange
        temp_file = Path("data") / "test.csv"

        # Act
        self.flags.to_csv(temp_file)

        with temp_file.open("r") as file:
            lines = [line.strip() for line in file.readlines()]
        temp_file.unlink()

        # Assert
        self.assertEqual(len(self.flags), len(lines))
        self.assertIn(CSV_SEP.join(["ToolA", "FileA", "10", "VulnA"]), lines)
        self.assertIn(CSV_SEP.join(["ToolB", "FileB", "20", "VulnB"]), lines)

    def test_from_csv(self):
        # Arrange
        temp_file = Path("data") / "test.csv"
        lines = [
            CSV_SEP.join(["ToolA", "FileA", "10", "VulnA"]) + os.linesep,
            CSV_SEP.join(["ToolB", "FileB", "20", "VulnB"]) + os.linesep,
            CSV_SEP.join(["ToolC", "FileC", "30", "VulnC"]) + os.linesep,
        ]

        with temp_file.open("w") as file:
            file.writelines(lines)

        # Act
        actual = SASTToolFlags.from_csv(temp_file)
        temp_file.unlink()

        # Assert
        expected = SASTToolFlags()
        expected.add(SASTToolFlag("ToolA", "FileA", 10, "VulnA"))
        expected.add(SASTToolFlag("ToolB", "FileB", 20, "VulnB"))
        expected.add(SASTToolFlag("ToolC", "FileC", 30, "VulnC"))

        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
