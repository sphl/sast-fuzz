import unittest
from pathlib import Path
from typing import Set, Tuple

from sfa.logic import GroupedSASTFlag, SASTFlag, SASTFlagSet
from sfa.logic.grouping import CONCAT_CHAR, BasicBlockGrouping
from sfa.util.fs import get_parent


def unfold(flags: SASTFlagSet) -> Set[Tuple]:
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
            flag.n_flg_lines,
            flag.n_all_lines,
            flag.n_run_tools,
            flag.n_all_tools,
        )
        for flag in flags
        if isinstance(flag, GroupedSASTFlag)
    }


class TestBasicBlockGrouping(unittest.TestCase):
    def setUp(self) -> None:
        inspec_file = get_parent(Path(__file__), 2) / "data" / "sfi" / "quicksort.json"
        self.grouping = BasicBlockGrouping(inspec_file)

    def test_group_same_bb(self) -> None:
        # Arrange
        flags = SASTFlagSet()
        flags.add(SASTFlag("tool1", "quicksort.c", 67, "vuln1"))  # Block 16
        flags.add(SASTFlag("tool2", "quicksort.c", 70, "vuln2"))  # Block 16
        flags.add(SASTFlag("tool3", "quicksort.c", 73, "vuln3"))  # Block 16

        expected = SASTFlagSet()
        expected.add(GroupedSASTFlag("tool1-tool2-tool3", "quicksort.c", 65, "vuln1:67-vuln2:70-vuln3:73", 3, 8, 3, 3))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))

    def test_group_two_bbs(self) -> None:
        # Arrange
        flags = SASTFlagSet()
        flags.add(SASTFlag("tool1", "quicksort.c", 67, "vuln1"))  # Block 16
        flags.add(SASTFlag("tool2", "quicksort.c", 19, "vuln2"))  # Block 1
        flags.add(SASTFlag("tool3", "quicksort.c", 73, "vuln3"))  # Block 16

        expected = SASTFlagSet()
        expected.add(GroupedSASTFlag("tool1-tool3", "quicksort.c", 65, "vuln1:67-vuln3:73", 2, 8, 2, 3))
        expected.add(GroupedSASTFlag("tool2", "quicksort.c", 13, "vuln2:19", 1, 4, 1, 3))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))

    def test_group_three_bbs(self) -> None:
        # Arrange
        flags = SASTFlagSet()
        flags.add(SASTFlag("tool1", "quicksort.c", 47, "vuln1"))  # Block 9
        flags.add(SASTFlag("tool2", "quicksort.c", 19, "vuln2"))  # Block 1
        flags.add(SASTFlag("tool3", "quicksort.c", 73, "vuln3"))  # Block 16

        expected = SASTFlagSet()
        expected.add(GroupedSASTFlag("tool1", "quicksort.c", 45, "vuln1:47", 1, 4, 1, 3))
        expected.add(GroupedSASTFlag("tool2", "quicksort.c", 13, "vuln2:19", 1, 4, 1, 3))
        expected.add(GroupedSASTFlag("tool3", "quicksort.c", 65, "vuln3:73", 1, 8, 1, 3))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))

    def test_group_same_tool(self) -> None:
        # Arrange
        flags = SASTFlagSet()
        flags.add(SASTFlag("tool1", "quicksort.c", 67, "vuln1"))  # Block 16
        flags.add(SASTFlag("tool2", "quicksort.c", 19, "vuln2"))  # Block 1
        flags.add(SASTFlag("tool1", "quicksort.c", 73, "vuln3"))  # Block 16

        expected = SASTFlagSet()
        expected.add(GroupedSASTFlag("tool1", "quicksort.c", 65, "vuln1:67-vuln3:73", 2, 8, 1, 2))
        expected.add(GroupedSASTFlag("tool2", "quicksort.c", 13, "vuln2:19", 1, 4, 1, 2))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))

    def test_group_same_vuln(self) -> None:
        # Arrange
        flags = SASTFlagSet()
        flags.add(SASTFlag("tool1", "quicksort.c", 67, "vuln1"))  # Block 16
        flags.add(SASTFlag("tool2", "quicksort.c", 19, "vuln2"))  # Block 1
        flags.add(SASTFlag("tool3", "quicksort.c", 67, "vuln1"))  # Block 16

        expected = SASTFlagSet()
        expected.add(GroupedSASTFlag("tool1-tool3", "quicksort.c", 65, "vuln1:67", 1, 8, 2, 3))
        expected.add(GroupedSASTFlag("tool2", "quicksort.c", 13, "vuln2:19", 1, 4, 1, 3))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))

    def test_group_diff_vuln_same_line(self) -> None:
        # Arrange
        flags = SASTFlagSet()
        flags.add(SASTFlag("tool1", "quicksort.c", 67, "vuln1"))  # Block 16
        flags.add(SASTFlag("tool2", "quicksort.c", 19, "vuln2"))  # Block 1
        flags.add(SASTFlag("tool3", "quicksort.c", 67, "vuln3"))  # Block 16

        expected = SASTFlagSet()
        expected.add(GroupedSASTFlag("tool1-tool3", "quicksort.c", 65, "vuln1:67-vuln3:67", 1, 8, 2, 3))
        expected.add(GroupedSASTFlag("tool2", "quicksort.c", 13, "vuln2:19", 1, 4, 1, 3))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))

    def test_group_scope_func(self) -> None:
        # Arrange
        flags = SASTFlagSet()
        flags.add(SASTFlag("tool1", "quicksort.c", 54, "vuln1"))  # Outside of function(s)
        flags.add(SASTFlag("tool2", "quicksort.c", 19, "vuln2"))  # Block 1
        flags.add(SASTFlag("tool3", "quicksort.c", 67, "vuln3"))  # Block 16

        expected = SASTFlagSet()
        expected.add(GroupedSASTFlag("tool2", "quicksort.c", 13, "vuln2:19", 1, 4, 1, 3))
        expected.add(GroupedSASTFlag("tool3", "quicksort.c", 65, "vuln3:67", 1, 8, 1, 3))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))

    def test_group_scope_file(self) -> None:
        # Arrange
        flags = SASTFlagSet()
        flags.add(SASTFlag("tool1", "main.c", 67, "vuln1"))  # Wrong file
        flags.add(SASTFlag("tool2", "quicksort.c", 19, "vuln2"))  # Block 1
        flags.add(SASTFlag("tool3", "quicksort.c", 73, "vuln3"))  # Block 16

        expected = SASTFlagSet()
        expected.add(GroupedSASTFlag("tool2", "quicksort.c", 13, "vuln2:19", 1, 4, 1, 3))
        expected.add(GroupedSASTFlag("tool3", "quicksort.c", 65, "vuln3:73", 1, 8, 1, 3))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))


if __name__ == "__main__":
    unittest.main()
