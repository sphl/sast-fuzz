from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path

import yaml

# SAST tool configuration
SASTToolConfig = namedtuple("SASTToolConfig", ["path", "checks", "num_threads"], defaults=["", "", -1])


@dataclass
class AppConfig:
    """
    Application configuration.
    """

    flawfinder: SASTToolConfig
    semgrep: SASTToolConfig
    infer: SASTToolConfig
    codeql: SASTToolConfig
    clang_scan: SASTToolConfig

    @classmethod
    def from_yaml(cls, file: Path) -> "AppConfig":
        """
        Load configuration from a YAML file.

        :param file:
        :return:
        """
        config = yaml.safe_load(file.read_text())

        codeql_checks = [
            check.replace("%LIBRARY_PATH%", config["tools"]["codeql"]["lib_path"])
            for check in config["tools"]["codeql"]["checks"]
        ]

        return cls(
            flawfinder=SASTToolConfig(
                config["tools"]["flawfinder"]["path"], config["tools"]["flawfinder"]["checks"], -1
            ),
            semgrep=SASTToolConfig(
                config["tools"]["semgrep"]["path"],
                config["tools"]["semgrep"]["checks"],
                config["tools"]["semgrep"]["num_threads"],
            ),
            infer=SASTToolConfig(
                config["tools"]["infer"]["path"],
                config["tools"]["infer"]["checks"],
                config["tools"]["infer"]["num_threads"],
            ),
            codeql=SASTToolConfig(
                config["tools"]["codeql"]["path"], codeql_checks, config["tools"]["codeql"]["num_threads"]
            ),
            clang_scan=SASTToolConfig(
                config["tools"]["clang_scan"]["path"], config["tools"]["clang_scan"]["checks"], -1
            ),
        )
