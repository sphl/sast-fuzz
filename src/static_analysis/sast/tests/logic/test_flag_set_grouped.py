import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sfa.logic import CSV_SEP, GroupedSASTFlag, SASTFlagSet


class TestFlagSetGrouped(unittest.TestCase):
    def setUp(self) -> None:
        self.flags = SASTFlagSet()
        self.flags.add(GroupedSASTFlag("tool1", "file1", 10, "vuln1", 1, 3, 1, 5))
        self.flags.add(GroupedSASTFlag("tool2", "file2", 20, "vuln2", 1, 5, 1, 5))

    def test_add(self) -> None:
        # Arrange
        flag = GroupedSASTFlag("tool3", "file3", 30, "vuln3", 1, 7, 1, 5)

        # Act
        self.flags.add(flag)

        # Assert
        self.assertIn(flag, self.flags)

    def test_update(self) -> None:
        # Arrange
        flag3 = GroupedSASTFlag("tool3", "file3", 30, "vuln3", 1, 7, 1, 5)
        flag4 = GroupedSASTFlag("tool4", "file4", 40, "vuln4", 1, 9, 1, 5)

        # Act
        self.flags.update(SASTFlagSet({flag3, flag4}))

        # Assert
        self.assertIn(flag3, self.flags)
        self.assertIn(flag4, self.flags)

        self.assertEqual(len(self.flags), 4)

    def test_update_multiple(self) -> None:
        # Arrange
        flag1 = GroupedSASTFlag("tool1", "file1", 10, "vuln1", 1, 2, 1, 5)
        flag2 = GroupedSASTFlag("tool2", "file2", 20, "vuln2", 1, 4, 1, 5)
        flag3 = GroupedSASTFlag("tool3", "file3", 30, "vuln3", 1, 6, 1, 5)
        flag4 = GroupedSASTFlag("tool4", "file4", 40, "vuln4", 1, 3, 1, 5)
        flag5 = GroupedSASTFlag("tool5", "file5", 50, "vuln5", 1, 5, 1, 5)
        flag6 = GroupedSASTFlag("tool6", "file6", 60, "vuln6", 1, 7, 1, 5)

        flags1 = SASTFlagSet({flag1, flag2})
        flags2 = SASTFlagSet({flag3, flag4})
        flags3 = SASTFlagSet({flag5, flag6})

        expected = SASTFlagSet({flag1, flag2, flag3, flag4, flag5, flag6})

        # Act
        flags1.update(flags2, flags3)

        actual = flags1

        # Assert
        self.assertEqual(expected, actual)

    def test_remove(self) -> None:
        # Arrange
        flag = GroupedSASTFlag("tool1", "file1", 10, "vuln1", 1, 3, 1, 5)

        # Act
        self.flags.remove(flag)

        # Assert
        self.assertNotIn(flag, self.flags)

    def test_to_csv(self) -> None:
        with TemporaryDirectory() as temp_dir:
            # Arrange
            temp_file = Path(temp_dir) / "file.csv"

            # Act
            self.flags.to_csv(temp_file)

            with temp_file.open("r") as file:
                lines = [line.strip() for line in file.readlines()]

            # Assert
            self.assertEqual(len(self.flags), len(lines))
            self.assertIn(CSV_SEP.join(["tool1", "file1", "10", "vuln1", "1", "3", "1", "5"]), lines)
            self.assertIn(CSV_SEP.join(["tool2", "file2", "20", "vuln2", "1", "5", "1", "5"]), lines)

    def test_from_csv(self) -> None:
        with TemporaryDirectory() as temp_dir:
            # Arrange
            temp_file = Path(temp_dir) / "test.csv"
            lines = [
                CSV_SEP.join(["tool1", "file1", "10", "vuln1", "1", "3", "1", "5"]) + os.linesep,
                CSV_SEP.join(["tool2", "file2", "20", "vuln2", "1", "5", "1", "5"]) + os.linesep,
                CSV_SEP.join(["tool3", "file3", "30", "vuln3", "1", "7", "1", "5"]) + os.linesep,
            ]

            with temp_file.open("w") as file:
                file.writelines(lines)

            # Act
            actual = SASTFlagSet.from_csv(temp_file)

            # Assert
            expected = SASTFlagSet()
            expected.add(GroupedSASTFlag("tool1", "file1", 10, "vuln1", 1, 3, 1, 5))
            expected.add(GroupedSASTFlag("tool2", "file2", 20, "vuln2", 1, 5, 1, 5))
            expected.add(GroupedSASTFlag("tool3", "file3", 30, "vuln3", 1, 7, 1, 5))

            self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
