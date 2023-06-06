import logging
import multiprocessing as mp
import os
import subprocess  # nosec
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union


def run_shell_command(
    cmd: Union[str, List[str]], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None
) -> str:
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

    logging.debug(f"Command: '{cmd_str}'")

    proc_info = subprocess.run(
        cmd_str, shell=True, cwd=cmd_cwd, env=cmd_env, capture_output=True, text=True, encoding="utf-8"
    )  # nosec

    if proc_info.stderr:
        logging.debug(proc_info.stderr)

    return proc_info.stdout


def run_with_multiproc(func: Callable, items: List, n_jobs: int = mp.cpu_count() - 1) -> List:
    """
    Run a function for each element in an iterable with multi-processing.

    :param func:
    :param items:
    :param n_jobs:
    :return:
    """
    with mp.Pool(n_jobs) as pool:
        try:
            res: List = pool.starmap(func, items)

        except TypeError as err:
            logging.info(err)

            # Try again with map() instead of starmap()
            res = pool.map(func, items)

    return res
