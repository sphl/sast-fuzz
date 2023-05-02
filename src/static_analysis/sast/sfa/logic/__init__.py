from dataclasses import dataclass
from typing import Set, TypeAlias


@dataclass(frozen=True)
class SASTToolFlag:
    """Container for SAST tool flag information."""
    tool_name: str
    file_name: str
    code_line: int
    vuln_type: str


SASTToolOutput: TypeAlias = Set[SASTToolFlag]
