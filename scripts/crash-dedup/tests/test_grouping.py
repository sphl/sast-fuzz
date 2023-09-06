import unittest
from pathlib import Path
from typing import Set

from cdd.container.san import SanitizerOutput, StackFrame
from cdd.container.summary import DedupSummary
from cdd.grouping import group_by


def check_grouping(summary: DedupSummary, expected: Set[str]) -> bool:
    """
    Check correctness of sanitizer output grouping.

    :param summary:
    :param expected:
    :return:
    """
    bug_id_map = {info.input_id: entry.bug_id for entry in summary.summary for info in entry.elems}

    bug_id = bug_id_map[list(expected)[0]]
    actual = set([s for s in bug_id_map.keys() if bug_id_map[s] == bug_id])

    return actual == expected


class TestGrouping(unittest.TestCase):
    def setUp(self) -> None:
        self.sanitizer_files = [
            Path(__file__).parent / "data" / "sanitizer" / "test.703472",
            Path(__file__).parent / "data" / "sanitizer" / "test.703480",
            Path(__file__).parent / "data" / "sanitizer" / "test.703482",
            Path(__file__).parent / "data" / "sanitizer" / "test.703486",
            Path(__file__).parent / "data" / "sanitizer" / "test.703498",
            Path(__file__).parent / "data" / "sanitizer" / "test.703500",
            Path(__file__).parent / "data" / "sanitizer" / "test.703504",
            Path(__file__).parent / "data" / "sanitizer" / "test.703506",
            Path(__file__).parent / "data" / "sanitizer" / "test.703510",
            Path(__file__).parent / "data" / "sanitizer" / "test.703512",
        ]

    def test_group_by_all_frames(self) -> None:
        # Arrange
        sanitizer_infos = [
            SanitizerOutput("input1", "type1", [StackFrame(1, "file1", "func1", 10)]),
            SanitizerOutput("input2", "type2", [StackFrame(2, "file2", "func2", 20)]),
            SanitizerOutput("input3", "type3", [StackFrame(3, "file3", "func3", 30)]),
        ]

        # Act
        actual = group_by(sanitizer_infos, None)

        # Assert
        n = len(actual.summary)
        for i in range(n):
            for j in range(n):
                if i != j:
                    bug_id_a = actual.summary[i].bug_id
                    bug_id_b = actual.summary[j].bug_id

                    self.assertNotEqual(bug_id_a, bug_id_b)

    def test_group_by_all_frames_same_vtype(self) -> None:
        # Arrange
        sanitizer_infos = [
            SanitizerOutput("input1", "type1", [StackFrame(1, "file1", "func1", 10)]),
            SanitizerOutput("input2", "type1", [StackFrame(2, "file2", "func2", 20)]),
            SanitizerOutput("input3", "type1", [StackFrame(3, "file3", "func3", 30)]),
        ]

        # Act
        actual = group_by(sanitizer_infos, None)

        # Assert
        n = len(actual.summary)
        for i in range(n):
            for j in range(n):
                if i != j:
                    bug_id_a = actual.summary[i].bug_id
                    bug_id_b = actual.summary[j].bug_id

                    self.assertNotEqual(bug_id_a, bug_id_b)

    def test_group_by_all_frames_same_trace(self) -> None:
        # Arrange
        sanitizer_infos = [
            SanitizerOutput("input1", "type1", [StackFrame(1, "file1", "func1", 10)]),
            SanitizerOutput("input2", "type2", [StackFrame(1, "file1", "func1", 10)]),
            SanitizerOutput("input3", "type3", [StackFrame(1, "file1", "func1", 10)]),
        ]

        # Act
        actual = group_by(sanitizer_infos, None)

        # Assert
        n = len(actual.summary)
        for i in range(n):
            for j in range(n):
                if i != j:
                    bug_id_a = actual.summary[i].bug_id
                    bug_id_b = actual.summary[j].bug_id

                    self.assertNotEqual(bug_id_a, bug_id_b)

    def test_group_by_all_frames_same_group(self) -> None:
        # Arrange
        sanitizer_infos = [
            SanitizerOutput("input1", "type1", [StackFrame(1, "file1", "func1", 10)]),
            SanitizerOutput("input2", "type1", [StackFrame(1, "file1", "func1", 10)]),
            SanitizerOutput("input3", "type1", [StackFrame(1, "file1", "func1", 10)]),
        ]

        # Act
        actual = group_by(sanitizer_infos, None)

        # Assert
        self.assertEqual(len(actual.summary), 1)

        for info in sanitizer_infos:
            self.assertIn(info, actual.summary[0].elems)

    def test_group_by_all_frames_real_vulns(self) -> None:
        # Arrange
        sanitizer_infos = [SanitizerOutput.from_file(f) for f in self.sanitizer_files]

        expected = [
            {"/path/to/file01", "/path/to/file06"},
            {"/path/to/file05"},
            {"/path/to/file08", "/path/to/file15", "/path/to/file18", "/path/to/file21"},
            {"/path/to/file17"},
            {"/path/to/file14"},
            {"/path/to/file20"},
        ]

        # Act
        actual = group_by(sanitizer_infos, None)

        # Assert
        for group in expected:
            self.assertTrue(check_grouping(actual, group))

    def test_group_by_n_frames_1(self) -> None:
        # Arrange
        sanitizer_infos = [SanitizerOutput.from_file(f) for f in self.sanitizer_files]

        expected = [
            {"/path/to/file01", "/path/to/file06", "/path/to/file05"},
            {"/path/to/file08", "/path/to/file15", "/path/to/file18", "/path/to/file21"},
            {"/path/to/file17"},
            {"/path/to/file14", "/path/to/file20"},
        ]

        # Act
        actual = group_by(sanitizer_infos, 1)

        # Assert
        for group in expected:
            self.assertTrue(check_grouping(actual, group))

    def test_group_by_n_frames_5(self) -> None:
        # Arrange
        sanitizer_infos = [SanitizerOutput.from_file(f) for f in self.sanitizer_files]

        expected = [
            {"/path/to/file01", "/path/to/file06"},
            {"/path/to/file05"},
            {"/path/to/file08", "/path/to/file15", "/path/to/file18", "/path/to/file21"},
            {"/path/to/file17"},
            {"/path/to/file14", "/path/to/file20"},
        ]

        # Act
        actual = group_by(sanitizer_infos, 5)

        # Assert
        for group in expected:
            self.assertTrue(check_grouping(actual, group))

    def test_group_by_n_frames_7(self) -> None:
        # Arrange
        sanitizer_infos = [SanitizerOutput.from_file(f) for f in self.sanitizer_files]

        expected = [
            {"/path/to/file01", "/path/to/file06"},
            {"/path/to/file05"},
            {"/path/to/file08", "/path/to/file15", "/path/to/file18", "/path/to/file21"},
            {"/path/to/file17"},
            {"/path/to/file14"},
            {"/path/to/file20"},
        ]

        # Act
        actual = group_by(sanitizer_infos, 7)

        # Assert
        for group in expected:
            self.assertTrue(check_grouping(actual, group))
