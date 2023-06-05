import unittest
from pathlib import Path

from sfa.logic import SASTFlag, SASTFlagSet
from sfa.logic.filter import ReachabilityFilter
from sfa.util.fs import get_parent


class TestReachabilityFilter(unittest.TestCase):
    def setUp(self) -> None:
        inspec_file = get_parent(Path(__file__), 2) / "data" / "sfi" / "quicksort.json"
        self.filter = ReachabilityFilter(inspec_file)

    def test_filter_correct(self) -> None:
        # Arrange
        flags = SASTFlagSet()
        flags.add(SASTFlag("tool1", "quicksort.c", 29, "-"))
        flags.add(SASTFlag("tool2", "quicksort.c", 48, "-"))
        flags.add(SASTFlag("tool3", "quicksort.c", 60, "-"))
        flags.add(SASTFlag("tool4", "quicksort.c", 76, "-"))

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(flags, actual)

    def test_filter_scope_one_out(self) -> None:
        # Arrange
        flag1 = SASTFlag("tool1", "quicksort.c", 29, "-")
        flag2 = SASTFlag("tool2", "quicksort.c", 39, "-")  # Outside function scope
        flag3 = SASTFlag("tool3", "quicksort.c", 60, "-")
        flag4 = SASTFlag("tool4", "quicksort.c", 76, "-")

        flags = SASTFlagSet({flag1, flag2, flag3, flag4})

        expected = SASTFlagSet({flag1, flag3, flag4})

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)

    def test_filter_scope_all_out(self) -> None:
        # Arrange
        flag1 = SASTFlag("tool1", "quicksort.c", 11, "-")  # Outside function scope
        flag2 = SASTFlag("tool2", "quicksort.c", 39, "-")  # Outside function scope
        flag3 = SASTFlag("tool3", "quicksort.c", 54, "-")  # Outside function scope

        flags = SASTFlagSet({flag1, flag2, flag3})

        expected = SASTFlagSet()

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)

    def test_filter_dc(self) -> None:
        # Arrange
        flag1 = SASTFlag("tool1", "quicksort.c", 80, "-")  # Dead code
        flag2 = SASTFlag("tool2", "quicksort.c", 82, "-")  # Dead code

        flags = SASTFlagSet({flag1, flag2})

        expected = SASTFlagSet()

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)

    def test_filter_scope_dc(self) -> None:
        # Arrange
        flag1 = SASTFlag("tool1", "quicksort.c", 29, "-")
        flag2 = SASTFlag("tool2", "quicksort.c", 39, "-")  # Outside function scope
        flag3 = SASTFlag("tool3", "quicksort.c", 60, "-")
        flag4 = SASTFlag("tool4", "quicksort.c", 80, "-")  # Dead code

        flags = SASTFlagSet({flag1, flag2, flag3, flag4})

        expected = SASTFlagSet({flag1, flag3})

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)

    def test_filter_scope_dc_file(self) -> None:
        # Arrange
        flag1 = SASTFlag("tool1", "main.c", 29, "-")  # Wrong file
        flag2 = SASTFlag("tool2", "quicksort.c", 39, "-")  # Outside function scope
        flag3 = SASTFlag("tool3", "quicksort.c", 60, "-")
        flag4 = SASTFlag("tool4", "quicksort.c", 80, "-")  # Dead code

        flags = SASTFlagSet({flag1, flag2, flag3, flag4})

        expected = SASTFlagSet({flag3})

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
