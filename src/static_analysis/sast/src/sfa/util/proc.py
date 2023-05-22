import logging
import multiprocessing as mp
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Iterable, Callable, Optional


def run_shell_command(cmd: str | List[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None) -> str:
    """
    Run command as shell sub-process.

    :param cmd:
    :param cwd:
    :param env:
    :return:
    """
    cmd_str = cmd if type(cmd) is str else " ".join(cmd)
    cmd_cwd = cwd or Path.cwd()
    cmd_env = env or os.environ.copy()

    assert cmd_cwd.exists()

    logging.debug(f"Running command: '{cmd_str}'")

    try:
        return subprocess.run(
            cmd_str, shell=True, cwd=cmd_cwd, env=cmd_env, capture_output=True, text=True, encoding="utf-8"
        ).stdout

    except subprocess.CalledProcessError as e:
        logging.error(e)

        raise Exception(f"Failed to run command '{cmd_str}'!")


def get_cpu_count() -> int:
    """
    Get amount of CPUs available for multi-processing.

    :return:
    """
    return mp.cpu_count()


def run_with_multi_processing(func: Callable, iterable: Iterable, n_jobs: int = get_cpu_count() - 1) -> List:
    """
    Run a function for each element in an iterable with multi-processing.

    :param func:
    :param iterable:
    :param n_jobs:
    :return:
    """
    with mp.Pool(n_jobs) as pool:
        try:
            results: List = pool.starmap(func, iterable)

        except TypeError as e:
            try:
                results = pool.map(func, iterable)

            except TypeError as e:
                logging.error(e)
                raise Exception("Failed to run function in parallel!")

    return results
