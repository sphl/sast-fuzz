import unittest
from pathlib import Path
from typing import Set, Tuple
from sfa.logic.grouping import CONCAT_CHAR, SASTToolFlag, SASTToolFlags, BasicBlockGrouping


def unfold(flags: SASTToolFlags) -> Set[Tuple]:
    """
    Unfold SAST flags into a set of tuples (whose elements are partially also converted into sets) to avoid flaky tests
    due to ordering issues in 'flag.tool' and 'flag.vuln'.

    :param flags:
    :return:
    """
    return {
        (
            frozenset(flag.tool.split(CONCAT_CHAR)),
            flag.file,
            flag.line,
            frozenset(flag.vuln.split(CONCAT_CHAR)),
            flag.n_flags,
            flag.n_tools,
        )
        for flag in flags
    }


class TestBasicBlockGrouping(unittest.TestCase):
    def setUp(self):
        self.grouping = BasicBlockGrouping(Path("data") / "sfi" / "quicksort.json")

    def test_group_same_bb(self):
        # Arrange
        flags = SASTToolFlags()
        flags.add(SASTToolFlag("tool1", "quicksort.c", 67, "vuln1"))  # Block 16
        flags.add(SASTToolFlag("tool2", "quicksort.c", 70, "vuln2"))  # Block 16
        flags.add(SASTToolFlag("tool3", "quicksort.c", 73, "vuln3"))  # Block 16

        expected = SASTToolFlags()
        expected.add(SASTToolFlag("tool1-tool2-tool3", "quicksort.c", 65, "vuln1:67-vuln2:70-vuln3:73", 3, 3))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))

    def test_group_two_bbs(self):
        # Arrange
        flags = SASTToolFlags()
        flags.add(SASTToolFlag("tool1", "quicksort.c", 67, "vuln1"))  # Block 16
        flags.add(SASTToolFlag("tool2", "quicksort.c", 19, "vuln2"))  # Block 1
        flags.add(SASTToolFlag("tool3", "quicksort.c", 73, "vuln3"))  # Block 16

        expected = SASTToolFlags()
        expected.add(SASTToolFlag("tool1-tool3", "quicksort.c", 65, "vuln1:67-vuln3:73", 2, 2))
        expected.add(SASTToolFlag("tool2", "quicksort.c", 13, "vuln2:19", 1, 1))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))

    def test_group_three_bbs(self):
        # Arrange
        flags = SASTToolFlags()
        flags.add(SASTToolFlag("tool1", "quicksort.c", 47, "vuln1"))  # Block 9
        flags.add(SASTToolFlag("tool2", "quicksort.c", 19, "vuln2"))  # Block 1
        flags.add(SASTToolFlag("tool3", "quicksort.c", 73, "vuln3"))  # Block 16

        expected = SASTToolFlags()
        expected.add(SASTToolFlag("tool1", "quicksort.c", 45, "vuln1:47", 1, 1))
        expected.add(SASTToolFlag("tool2", "quicksort.c", 13, "vuln2:19", 1, 1))
        expected.add(SASTToolFlag("tool3", "quicksort.c", 65, "vuln3:73", 1, 1))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))

    def test_group_same_tool(self):
        # Arrange
        flags = SASTToolFlags()
        flags.add(SASTToolFlag("tool1", "quicksort.c", 67, "vuln1"))  # Block 16
        flags.add(SASTToolFlag("tool2", "quicksort.c", 19, "vuln2"))  # Block 1
        flags.add(SASTToolFlag("tool1", "quicksort.c", 73, "vuln3"))  # Block 16

        expected = SASTToolFlags()
        expected.add(SASTToolFlag("tool1", "quicksort.c", 65, "vuln1:67-vuln3:73", 2, 1))
        expected.add(SASTToolFlag("tool2", "quicksort.c", 13, "vuln2:19", 1, 1))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))

    def test_group_same_vuln(self):
        # Arrange
        flags = SASTToolFlags()
        flags.add(SASTToolFlag("tool1", "quicksort.c", 67, "vuln1"))  # Block 16
        flags.add(SASTToolFlag("tool2", "quicksort.c", 19, "vuln2"))  # Block 1
        flags.add(SASTToolFlag("tool3", "quicksort.c", 67, "vuln1"))  # Block 16

        expected = SASTToolFlags()
        expected.add(SASTToolFlag("tool1-tool3", "quicksort.c", 65, "vuln1:67", 1, 2))
        expected.add(SASTToolFlag("tool2", "quicksort.c", 13, "vuln2:19", 1, 1))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))

    def test_group_scope_func(self):
        # Arrange
        flags = SASTToolFlags()
        flags.add(SASTToolFlag("tool1", "quicksort.c", 54, "vuln1"))  # Outside of function(s)
        flags.add(SASTToolFlag("tool2", "quicksort.c", 19, "vuln2"))  # Block 1
        flags.add(SASTToolFlag("tool3", "quicksort.c", 67, "vuln3"))  # Block 16

        expected = SASTToolFlags()
        expected.add(SASTToolFlag("tool2", "quicksort.c", 13, "vuln2:19", 1, 1))
        expected.add(SASTToolFlag("tool3", "quicksort.c", 65, "vuln3:67", 1, 1))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))

    def test_group_scope_file(self):
        # Arrange
        flags = SASTToolFlags()
        flags.add(SASTToolFlag("tool1", "main.c", 67, "vuln1"))  # Wrong file
        flags.add(SASTToolFlag("tool2", "quicksort.c", 19, "vuln2"))  # Block 1
        flags.add(SASTToolFlag("tool3", "quicksort.c", 73, "vuln3"))  # Block 16

        expected = SASTToolFlags()
        expected.add(SASTToolFlag("tool3", "quicksort.c", 65, "vuln3:73", 1, 1))
        expected.add(SASTToolFlag("tool2", "quicksort.c", 13, "vuln2:19", 1, 1))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))


if __name__ == "__main__":
    unittest.main()
