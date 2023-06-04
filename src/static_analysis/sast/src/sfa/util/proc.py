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

    try:
        proc_info = subprocess.run(
            cmd_str, shell=True, cwd=cmd_cwd, env=cmd_env, capture_output=True, text=True, encoding="utf-8"
        )  # nosec

        if proc_info.stderr:
            logging.info(proc_info.stderr)

        return proc_info.stdout

    except subprocess.CalledProcessError as e:
        logging.error(e)

        raise Exception(f"Failed to run command '{cmd_str}'!")


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
            results: List = pool.starmap(func, items)

        except TypeError as e:
            try:
                results = pool.map(func, items)

            except TypeError as e:
                logging.error(e)
                raise Exception("Failed to run function in parallel!")

    return results
