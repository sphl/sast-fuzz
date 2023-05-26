import unittest
from pathlib import Path

from sfa.logic import SASTToolFlag, SASTToolFlags
from sfa.logic.filter import ReachabilityFilter


class TestReachabilityFilter(unittest.TestCase):
    def setUp(self) -> None:
        self.filter = ReachabilityFilter(Path("data") / "sfi" / "quicksort.json")

    def test_filter_correct(self) -> None:
        # Arrange
        flags = SASTToolFlags()
        flags.add(SASTToolFlag("tool1", "quicksort.c", 29, "-"))
        flags.add(SASTToolFlag("tool2", "quicksort.c", 48, "-"))
        flags.add(SASTToolFlag("tool3", "quicksort.c", 60, "-"))
        flags.add(SASTToolFlag("tool4", "quicksort.c", 76, "-"))

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(flags, actual)

    def test_filter_scope_one_out(self) -> None:
        # Arrange
        flag1 = SASTToolFlag("tool1", "quicksort.c", 29, "-")
        flag2 = SASTToolFlag("tool2", "quicksort.c", 39, "-")  # Outside function scope
        flag3 = SASTToolFlag("tool3", "quicksort.c", 60, "-")
        flag4 = SASTToolFlag("tool4", "quicksort.c", 76, "-")

        flags = SASTToolFlags({flag1, flag2, flag3, flag4})

        expected = SASTToolFlags({flag1, flag3, flag4})

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)

    def test_filter_scope_all_out(self) -> None:
        # Arrange
        flag1 = SASTToolFlag("tool1", "quicksort.c", 11, "-")  # Outside function scope
        flag2 = SASTToolFlag("tool2", "quicksort.c", 39, "-")  # Outside function scope
        flag3 = SASTToolFlag("tool3", "quicksort.c", 54, "-")  # Outside function scope

        flags = SASTToolFlags({flag1, flag2, flag3})

        expected = SASTToolFlags()

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)

    def test_filter_dc(self) -> None:
        # Arrange
        flag1 = SASTToolFlag("tool1", "quicksort.c", 80, "-")  # Dead code
        flag2 = SASTToolFlag("tool2", "quicksort.c", 82, "-")  # Dead code

        flags = SASTToolFlags({flag1, flag2})

        expected = SASTToolFlags()

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)

    def test_filter_scope_dc(self) -> None:
        # Arrange
        flag1 = SASTToolFlag("tool1", "quicksort.c", 29, "-")
        flag2 = SASTToolFlag("tool2", "quicksort.c", 39, "-")  # Outside function scope
        flag3 = SASTToolFlag("tool3", "quicksort.c", 60, "-")
        flag4 = SASTToolFlag("tool4", "quicksort.c", 80, "-")  # Dead code

        flags = SASTToolFlags({flag1, flag2, flag3, flag4})

        expected = SASTToolFlags({flag1, flag3})

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)

    def test_filter_scope_dc_file(self) -> None:
        # Arrange
        flag1 = SASTToolFlag("tool1", "main.c", 29, "-")  # Wrong file
        flag2 = SASTToolFlag("tool2", "quicksort.c", 39, "-")  # Outside function scope
        flag3 = SASTToolFlag("tool3", "quicksort.c", 60, "-")
        flag4 = SASTToolFlag("tool4", "quicksort.c", 80, "-")  # Dead code

        flags = SASTToolFlags({flag1, flag2, flag3, flag4})

        expected = SASTToolFlags({flag3})

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
