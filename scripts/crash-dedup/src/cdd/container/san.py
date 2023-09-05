import re
from collections import namedtuple
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional

# Stack frame information
StackFrame = namedtuple("StackFrame", ["id", "file", "function", "line"])

# Stack trace, i.e. list of stack frames
StackTrace = List[StackFrame]


def find_vtype(line: str) -> Optional[str]:
    """
    Find the vuln.-type in a sanitizer output line.
    :param line:
    :return:
    """
    if m := re.search(r"[Ee][Rr][Rr][Oo][Rr]:\s[^:]+:\s([a-zA-Z-_]+)", line):
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

    def __init__(self, vtype: str, stack_trace: StackTrace) -> None:
        self._vtype = vtype
        self._stack_trace = stack_trace

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SanitizerOutput):
            return False

        return self._vtype == o._vtype and self._stack_trace == o._stack_trace

    @classmethod
    def from_file(cls, file: Path) -> "SanitizerOutput":
        """
        Create a SanitizerOutput object from the sanitizer output file.

        :param file:
        :return:
        """
        vtype = "-"
        stack_trace = []

        state = ParseState.VTYPE

        for line in [l.strip() for l in file.read_text().splitlines()]:
            if state == ParseState.VTYPE:
                if v := find_vtype(line):
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
            raise Exception(f"Invalid sanitizer output in '{file}'!")

        return SanitizerOutput(vtype, stack_trace)
