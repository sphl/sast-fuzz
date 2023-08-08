import unittest
from pathlib import Path
from typing import Set

from sfa.utils.fs import copy_dir, find_files

from tempfile import TemporaryDirectory


class TestFSUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.root_dir = Path(__file__).parent / "data" / "files"

    def test_copy_dir(self) -> None:
        with TemporaryDirectory() as temp_dir:
            # Arrange
            src_dir = Path(temp_dir) / "src"
            dst_dir = Path(temp_dir) / "dst"

            src_dir.mkdir()

            temp_file = src_dir / "test.txt"
            temp_file.touch()

            expected = dst_dir

            # Act
            actual = copy_dir(src_dir, dst_dir, overwrite=False, extend_dst=False)

            # Assert
            self.assertEqual(expected, actual)

            self.assertTrue(actual.exists())
            self.assertTrue((actual / temp_file.name).exists())

    def test_copy_dir_exception(self) -> None:
        with TemporaryDirectory() as temp_dir:
            # Arrange
            src_dir = Path(temp_dir) / "src"
            dst_dir = Path(temp_dir) / "dst"

            src_dir.mkdir()
            dst_dir.mkdir()

            # Act + Assert
            self.assertRaises(FileExistsError, copy_dir, src_dir, dst_dir, overwrite=False, extend_dst=False)

    def test_copy_dir_extend_dst(self) -> None:
        with TemporaryDirectory() as temp_dir:
            # Arrange
            src_dir = Path(temp_dir) / "src"
            dst_dir = Path(temp_dir) / "dst"

            src_dir.mkdir()
            dst_dir.mkdir()

            temp_file = src_dir / "test.txt"
            temp_file.touch()

            expected = dst_dir / src_dir.name

            # Act
            actual = copy_dir(src_dir, dst_dir, extend_dst=True)

            # Assert
            self.assertEqual(expected, actual)

            self.assertTrue(actual.exists())
            self.assertTrue((actual / temp_file.name).exists())

    def test_find_files_no_rec_no_exts(self) -> None:
        # Arrange
        expected = {self.root_dir / "test.json"}

        # Act
        actual = find_files(self.root_dir, rec=False)

        # Assert
        self.assertEqual(expected, actual)

    def test_find_files_no_rec_one_ext(self) -> None:
        # Arrange
        expected: Set[Path] = set()

        # Act
        actual = find_files(self.root_dir, exts=[".pdf"], rec=False)

        # Assert
        self.assertEqual(expected, actual)

    def test_find_files_rec_no_exts(self) -> None:
        # Arrange
        expected = {self.root_dir / "dir" / "test.csv", self.root_dir / "test.json"}

        # Act
        actual = find_files(self.root_dir, rec=True)

        # Assert
        self.assertEqual(expected, actual)

    def test_find_files_rec_mult_exts(self) -> None:
        # Arrange
        expected = {self.root_dir / "test.json"}

        # Act
        actual = find_files(self.root_dir, exts=[".pdf", ".json"], rec=True)

        # Assert
        self.assertEqual(expected, actual)

    def test_find_files_rec_one_ext_csv(self) -> None:
        # Arrange
        expected = {self.root_dir / "dir" / "test.csv"}

        # Act
        actual = find_files(self.root_dir, exts=[".csv"], rec=True)

        # Assert
        self.assertEqual(expected, actual)

    def test_find_files_rec_one_ext_pdf(self) -> None:
        # Arrange
        expected: Set[Path] = set()

        # Act
        actual = find_files(self.root_dir, exts=[".pdf"], rec=True)

        # Assert
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
