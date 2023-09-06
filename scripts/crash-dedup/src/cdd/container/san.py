import re
from collections import namedtuple
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional, Tuple

# Stack frame information
StackFrame = namedtuple("StackFrame", ["id", "file", "function", "line"])

# Stack trace, i.e. list of stack frames
StackTrace = List[StackFrame]


def find_input(line: str) -> Optional[str]:
    """
    Find the original input filepath in a sanitizer output line.

    :param line:
    :return:
    """
    if m := re.search(r"INPUT_FILE:\s(.+)", line):
        return str(m.group(1))
    else:
        return None


def find_vtype(line: str) -> Optional[str]:
    """
    Find the vuln.-type in a sanitizer output line.

    :param line:
    :return:
    """
    if m := re.search(r"ERROR:\s[^:]+:\s([a-zA-Z-_]+)", line):
        return str(m.group(1)).lower()
    else:
        return None


def find_frame(line: str) -> Optional[StackFrame]:
    """
    Find the stack frame information in a sanitizer output line.

    :param line:
    :return:
    """
    if m := re.search(r"#([0-9]+).*in\s([a-zA-Z0-9_]+)\s([^:]+):([0-9]+)", line):
        return StackFrame(int(m.group(1)), Path(m.group(3)).name, m.group(2), int(m.group(4)))

    if m := re.search(r"#([0-9]+).*in\s([a-zA-Z0-9_]+)", line):
        return StackFrame(int(m.group(1)), "-", m.group(2), -1)
    else:
        return None


class ParseState(Enum):
    """
    Sanitizer output parse state.
    """

    VTYPE = auto()
    FRAME = auto()
    TRACE = auto()
    VALID = auto()


class SanitizerOutput:
    """
    Sanitizer output container.
    """

    def __init__(self, input_id: str, vtype: str, stack_trace: StackTrace) -> None:
        self.input_id = input_id
        self.vtype = vtype
        self.stack_trace = stack_trace

    def sorting_key(self, n_frames: Optional[int] = None) -> Tuple:
        """
        Get sorting key for grouping sanitizer outputs.

        :param n_frames:
        :return:
        """
        return self.vtype, self.stack_trace if n_frames is None else self.stack_trace[:n_frames]

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SanitizerOutput):
            return False

        return self.vtype == o.vtype and self.stack_trace == o.stack_trace

    @classmethod
    def from_file(cls, sanitizer_file: Path) -> "SanitizerOutput":
        """
        Create a SanitizerOutput object from the sanitizer output file.

        :param sanitizer_file:
        :return:
        """
        input_id = ""
        vtype = "-"
        stack_trace = []

        state = ParseState.VTYPE

        for line in [l.strip() for l in sanitizer_file.read_text().splitlines()]:
            if state == ParseState.VTYPE:
                if i := find_input(line):
                    input_id = i
                elif v := find_vtype(line):
                    vtype = v
                    state = ParseState.FRAME

            elif state == ParseState.FRAME:
                if f := find_frame(line):
                    stack_trace.append(f)
                    state = ParseState.TRACE

            elif state == ParseState.TRACE:
                if f := find_frame(line):
                    stack_trace.append(f)
                elif len(line) == 0:
                    state = ParseState.VALID
                    break
                else:
                    break

        if state != ParseState.VALID:
            raise Exception(f"Invalid sanitizer output in '{sanitizer_file}'!")

        return SanitizerOutput(input_id, vtype, stack_trace)