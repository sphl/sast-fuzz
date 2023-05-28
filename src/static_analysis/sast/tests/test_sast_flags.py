import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sfa.logic import SASTToolFlags, SASTToolFlag, CSV_SEP


class TestSASTToolFlags(unittest.TestCase):
    def setUp(self):
        self.flags = SASTToolFlags()
        self.flags.add(SASTToolFlag("tool1", "file1", 10, "vuln1"))
        self.flags.add(SASTToolFlag("tool2", "file2", 20, "vuln2"))

    def test_add(self):
        # Arrange
        flag = SASTToolFlag("tool3", "file3", 30, "vuln3")

        # Act
        self.flags.add(flag)

        # Assert
        self.assertIn(flag, self.flags)

    def test_update(self):
        # Arrange
        flag3 = SASTToolFlag("tool3", "file3", 30, "vuln3")
        flag4 = SASTToolFlag("tool4", "file4", 40, "vuln4")

        # Act
        self.flags.update(SASTToolFlags({flag3, flag4}))

        # Assert
        self.assertIn(flag3, self.flags)
        self.assertIn(flag4, self.flags)

        self.assertEqual(len(self.flags), 4)

    def test_update_multiple(self):
        # Arrange
        flag1 = SASTToolFlag("tool1", "file1", 10, "vuln1")
        flag2 = SASTToolFlag("tool2", "file2", 20, "vuln2")
        flag3 = SASTToolFlag("tool3", "file3", 30, "vuln3")
        flag4 = SASTToolFlag("tool4", "file4", 40, "vuln4")
        flag5 = SASTToolFlag("tool5", "file5", 50, "vuln5")
        flag6 = SASTToolFlag("tool6", "file6", 60, "vuln6")

        flags1 = SASTToolFlags({flag1, flag2})
        flags2 = SASTToolFlags({flag3, flag4})
        flags3 = SASTToolFlags({flag5, flag6})

        expected = SASTToolFlags({flag1, flag2, flag3, flag4, flag5, flag6})

        # Act
        flags1.update(flags2, flags3)

        actual = flags1

        # Assert
        self.assertEqual(expected, actual)

    def test_remove(self):
        # Arrange
        flag = SASTToolFlag("tool1", "file1", 10, "vuln1")

        # Act
        self.flags.remove(flag)

        # Assert
        self.assertNotIn(flag, self.flags)

    def test_to_csv(self):
        with TemporaryDirectory() as temp_dir:
            # Arrange
            temp_file = Path(temp_dir) / "file.csv"

            # Act
            self.flags.to_csv(temp_file)

            with temp_file.open("r") as file:
                lines = [line.strip() for line in file.readlines()]
            temp_file.unlink()

            # Assert
            self.assertEqual(len(self.flags), len(lines))
            self.assertIn(CSV_SEP.join(["tool1", "file1", "10", "vuln1", "1", "1"]), lines)
            self.assertIn(CSV_SEP.join(["tool2", "file2", "20", "vuln2", "1", "1"]), lines)

    def test_from_csv(self):
        with TemporaryDirectory() as temp_dir:
            # Arrange
            temp_file = Path(temp_dir) / "test.csv"
            lines = [
                CSV_SEP.join(["tool1", "file1", "10", "vuln1", "1", "1"]) + os.linesep,
                CSV_SEP.join(["tool2", "file2", "20", "vuln2", "1", "1"]) + os.linesep,
                CSV_SEP.join(["tool3", "file3", "30", "vuln3", "1", "1"]) + os.linesep,
            ]

            with temp_file.open("w") as file:
                file.writelines(lines)

            # Act
            actual = SASTToolFlags.from_csv(temp_file)

            # Assert
            expected = SASTToolFlags()
            expected.add(SASTToolFlag("tool1", "file1", 10, "vuln1", 1, 1))
            expected.add(SASTToolFlag("tool2", "file2", 20, "vuln2", 1, 1))
            expected.add(SASTToolFlag("tool3", "file3", 30, "vuln3", 1, 1))

            self.assertEqual(expected, actual)

    def test_from_multiple_csvs(self):
        # Arrange
        flag1 = SASTToolFlag("tool1", "file1", 10, "vuln1")
        flag2 = SASTToolFlag("tool2", "file2", 20, "vuln2")
        flag3 = SASTToolFlag("tool3", "file3", 30, "vuln3")
        flag4 = SASTToolFlag("tool4", "file4", 40, "vuln4")

        flags1 = SASTToolFlags({flag1, flag2})
        flags2 = SASTToolFlags({flag3, flag4})

        expected = SASTToolFlags({flag1, flag2, flag3, flag4})

        with TemporaryDirectory() as temp_dir:
            csv_file1 = Path(temp_dir) / "file1.csv"
            csv_file2 = Path(temp_dir) / "file2.csv"

            flags1.to_csv(csv_file1)
            flags2.to_csv(csv_file2)

            # Act
            actual = SASTToolFlags.from_multiple_csvs([csv_file1, csv_file2])

            # Assert
            self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
