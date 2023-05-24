import unittest
from pathlib import Path

from sfa.logic import SASTToolFlag, SASTToolFlags
from sfa.logic.filter import ReachabilityFilter


class TestReachabilityFilter(unittest.TestCase):
    def setUp(self) -> None:
        self.filter = ReachabilityFilter(Path("./data/sfi/quicksort.json"))

    def test_filter_correct(self) -> None:
        # Arrange
        flags = SASTToolFlags()
        flags.add(SASTToolFlag("ToolA", "quicksort.c", 29, "-"))
        flags.add(SASTToolFlag("ToolB", "quicksort.c", 48, "-"))
        flags.add(SASTToolFlag("ToolC", "quicksort.c", 60, "-"))
        flags.add(SASTToolFlag("ToolD", "quicksort.c", 76, "-"))

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(flags, actual)

    def test_filter_scope_one_out(self) -> None:
        # Arrange
        flag_1 = SASTToolFlag("ToolA", "quicksort.c", 29, "-")
        flag_2 = SASTToolFlag("ToolB", "quicksort.c", 39, "-")  # Outside function scope
        flag_3 = SASTToolFlag("ToolC", "quicksort.c", 60, "-")
        flag_4 = SASTToolFlag("ToolD", "quicksort.c", 76, "-")

        flags = SASTToolFlags({flag_1, flag_2, flag_3, flag_4})

        expected = SASTToolFlags({flag_1, flag_3, flag_4})

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)

    def test_filter_scope_all_out(self) -> None:
        # Arrange
        flag_1 = SASTToolFlag("ToolA", "quicksort.c", 11, "-")  # Outside function scope
        flag_2 = SASTToolFlag("ToolB", "quicksort.c", 39, "-")  # Outside function scope
        flag_3 = SASTToolFlag("ToolC", "quicksort.c", 54, "-")  # Outside function scope

        flags = SASTToolFlags({flag_1, flag_2, flag_3})

        expected = SASTToolFlags()

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)

    def test_filter_dc(self) -> None:
        # Arrange
        flag_1 = SASTToolFlag("ToolA", "quicksort.c", 80, "-")  # Dead code
        flag_2 = SASTToolFlag("ToolB", "quicksort.c", 82, "-")  # Dead code

        flags = SASTToolFlags({flag_1, flag_2})

        expected = SASTToolFlags()

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)

    def test_filter_scope_dc(self) -> None:
        # Arrange
        flag_1 = SASTToolFlag("ToolA", "quicksort.c", 29, "-")
        flag_2 = SASTToolFlag("ToolB", "quicksort.c", 39, "-")  # Outside function scope
        flag_3 = SASTToolFlag("ToolC", "quicksort.c", 60, "-")
        flag_4 = SASTToolFlag("ToolD", "quicksort.c", 80, "-")  # Dead code

        flags = SASTToolFlags({flag_1, flag_2, flag_3, flag_4})

        expected = SASTToolFlags({flag_1, flag_3})

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)

    def test_filter_scope_dc_file(self) -> None:
        # Arrange
        flag_1 = SASTToolFlag("ToolA", "main.c", 29, "-")  # Wrong file
        flag_2 = SASTToolFlag("ToolB", "quicksort.c", 39, "-")  # Outside function scope
        flag_3 = SASTToolFlag("ToolC", "quicksort.c", 60, "-")
        flag_4 = SASTToolFlag("ToolD", "quicksort.c", 80, "-")  # Dead code

        flags = SASTToolFlags({flag_1, flag_2, flag_3, flag_4})

        expected = SASTToolFlags({flag_3})

        # Act
        actual = self.filter.filter(flags)

        # Assert
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
