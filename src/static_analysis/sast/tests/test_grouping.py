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

    def test_group(self):
        # Arrange
        flags = SASTToolFlags()
        flags.add(SASTToolFlag("tool1", "quicksort.c", 67, "vuln1"))
        flags.add(SASTToolFlag("tool2", "quicksort.c", 19, "vuln2"))
        flags.add(SASTToolFlag("tool3", "quicksort.c", 73, "vuln3"))

        expected = SASTToolFlags()
        expected.add(SASTToolFlag("tool1-tool3", "quicksort.c", 65, "tool1:vuln1:67-tool3:vuln3:73", 2, 2))
        expected.add(SASTToolFlag("tool2", "quicksort.c", 13, "tool2:vuln2:19", 1, 1))

        # Act
        actual = self.grouping.group(flags)

        # Assert
        self.assertEqual(unfold(expected), unfold(actual))


if __name__ == "__main__":
    unittest.main()
