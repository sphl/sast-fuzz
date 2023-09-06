from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path

import yaml

InputConfig = namedtuple("InputConfig", ["blacklist"])


@dataclass
class AppConfig:
    """
    Application configuration.
    """

    inputConfig: InputConfig

    @classmethod
    def from_yaml(cls, file: Path) -> "AppConfig":
        """
        Load configuration from YAML file.

        :param file:
        :return:
        """

        config = yaml.safe_load(file.read_text())

        return cls(inputConfig=InputConfig(config["input_files"]["blacklist"]))
