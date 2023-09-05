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

    logging.debug(f"Command: {cmd_str}")

    proc_info = subprocess.run(
        cmd_str, shell=True, cwd=cmd_cwd, env=cmd_env, capture_output=True, text=True, encoding="utf-8"
    )  # nosec

    if proc_info.stderr:
        logging.debug(proc_info.stderr)

    return proc_info.stdout


def run_program_with_sanitizer(shell_cmd: str, input_file: Path, sanitizer_dir: Path) -> None:
    """
    Run a program/command and store the sanitizer output in the output directory.

    :param shell_cmd:
    :param input_file:
    :param sanitizer_dir:
    :return:
    """
    env = {
        **os.environ.copy(),
        **{"ASAN_OPTIONS": f"allocator_may_return_null=1:log_path={sanitizer_dir}/{input_file.name}"},
    }

    run_shell_command(shell_cmd.replace("@@", str(input_file)), env=env)


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

            # Try again with map() ...
            res = pool.map(func, items)

    return res
