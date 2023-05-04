from dataclasses import dataclass
from typing import Set, Dict, Any, TypeAlias


# from pkg_resources import get_distribution, DistributionNotFound
#
# try:
#     # Change here if project is renamed and does not equal the package name
#     dist_name = __name__
#     __version__ = get_distribution(dist_name).version
# except DistributionNotFound:
#     __version__ = "unknown"
# finally:
#     del get_distribution, DistributionNotFound


@dataclass(frozen=True)
class SASTToolFlag:
    """Container for a SAST tool flag."""
    tool: str
    file: str
    line: int
    vuln: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool,
            "file": self.file,
            "line": self.line,
            "vuln": self.vuln
        }


SASTToolOutput: TypeAlias = Set[SASTToolFlag]
