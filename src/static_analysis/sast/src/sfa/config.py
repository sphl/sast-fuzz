from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import yaml


def run_sanity_checks(config: Dict) -> None:
    """
    Run sanity checks on the configuration.

    :param config:
    :return:
    """
    # TODO: Add check for Flawfinder
    for tool in ["semgrep", "infer", "codeql", "clang_scan"]:
        tool_path = Path(config["tools"][tool]["path"])
        if not tool_path.exists():
            raise Exception(f"SAST tool '{tool}' not found at '{tool_path}'!")


@dataclass
class AppConfig:
    """
    Application configuration.
    """

    FLAWFINDER: str = field(init=False, default="")
    FLAWFINDER_CHECKS: List[str] = field(init=False, default_factory=lambda: [])
    SEMGREP: str = field(init=False, default="")
    SEMGREP_CHECKS: List[str] = field(init=False, default_factory=lambda: [])
    SEMGREP_NUM_THREADS: int = field(init=False, default=-1)
    INFER: str = field(init=False, default="")
    INFER_CHECKS: List[str] = field(init=False, default_factory=lambda: [])
    INFER_NUM_THREADS: int = field(init=False, default=-1)
    CODEQL: str = field(init=False, default="")
    CODEQL_CHECKS: List[str] = field(init=False, default_factory=lambda: [])
    CODEQL_NUM_THREADS: int = field(init=False, default=-1)
    CLANG_SCAN: str = field(init=False, default="")
    CLANG_SCAN_CHECKS: List[str] = field(init=False, default_factory=lambda: [])

    def load_from_file(self, config_file: Path) -> None:
        """
        Load configuration from a YAML file.

        :param config_file:
        :return:
        """
        config = yaml.safe_load(config_file.read_text())

        run_sanity_checks(config)

        self.FLAWFINDER = config["tools"]["flawfinder"]["path"]
        self.FLAWFINDER_CHECKS = config["tools"]["flawfinder"]["checks"]
        self.SEMGREP = config["tools"]["semgrep"]["path"]
        self.SEMGREP_CHECKS = config["tools"]["semgrep"]["checks"]
        self.SEMGREP_NUM_THREADS = config["tools"]["semgrep"]["num_threads"]
        self.INFER = config["tools"]["infer"]["path"]
        self.INFER_CHECKS = config["tools"]["infer"]["checks"]
        self.INFER_NUM_THREADS = config["tools"]["infer"]["num_threads"]
        self.CODEQL = config["tools"]["codeql"]["path"]
        self.CODEQL_CHECKS = [
            check.replace("%LIBRARY_PATH%", config["tools"]["codeql"]["lib_path"])
            for check in config["tools"]["codeql"]["checks"]
        ]
        self.CODEQL_NUM_THREADS = config["tools"]["codeql"]["num_threads"]
        self.CLANG_SCAN = config["tools"]["clang_scan"]["path"]
        self.CLANG_SCAN_CHECKS = config["tools"]["clang_scan"]["checks"]


# Global SFA configuration
app_config = AppConfig()
