import multiprocessing as mp

SHELL = "/bin/bash"
"""Path to the shell program."""

BUILD_SCRIPT_NAME = "build.sh"
"""Name of the subjects' build script."""

FLAWFINDER = "/opt/flawfinder-2.0.19/flawfinder.py"
"""Path to the Flawfinder analyzer."""

FLAWFINDER_RULE_SET = ["--falsepositive", "--minlevel=3", "--neverignore"]
"""Flags/rules of Flawfinder."""

INFER = "/opt/infer-1.1.0/bin/infer"
"""Path to the Infer analyzer."""

INFER_RULE_SET = [
    "--no-default-checkers",
    "--biabduction",
    "--bufferoverrun",
    # "--liveness",
    "--pulse",
    # "--quandary",
    # "--racerd",
    "--siof",
    # "--starvation",
    "--uninit"
]
"""Flags/rules of Infer."""

INFER_NUM_THREADS = mp.cpu_count() - 1
"""Number of threads used by Infer."""
