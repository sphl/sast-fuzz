from pathlib import Path

import yaml

FLAWFINDER = ""
FLAWFINDER_CHECKS = []
INFER = ""
INFER_CHECKS = []
INFER_NUM_THREADS = -1
CODEQL = ""
CODEQL_CHECKS = []
CODEQL_NUM_THREADS = -1
CLANG_SCAN = ""
CLANG_SCAN_CHECKS = []


def load_config(config_file: Path) -> None:
    """
    Load the configuration from the YAML file.

    :param config_file:
    :return:
    """
    global FLAWFINDER
    global FLAWFINDER_CHECKS
    global INFER
    global INFER_CHECKS
    global INFER_NUM_THREADS
    global CODEQL
    global CODEQL_CHECKS
    global CODEQL_NUM_THREADS
    global CLANG_SCAN
    global CLANG_SCAN_CHECKS

    config = yaml.safe_load(config_file.read_text())

    FLAWFINDER = config["tools"]["flawfinder"]["path"]
    FLAWFINDER_CHECKS = config["tools"]["flawfinder"]["checks"]
    INFER = config["tools"]["infer"]["path"]
    INFER_CHECKS = config["tools"]["infer"]["checks"]
    INFER_NUM_THREADS = config["tools"]["infer"]["num_threads"]
    CODEQL = config["tools"]["codeql"]["path"]
    CODEQL_CHECKS = config["tools"]["codeql"]["checks"]
    CODEQL_NUM_THREADS = config["tools"]["codeql"]["num_threads"]
    CLANG_SCAN = config["tools"]["clang_scan"]["path"]
    CLANG_SCAN_CHECKS = config["tools"]["clang_scan"]["checks"]
