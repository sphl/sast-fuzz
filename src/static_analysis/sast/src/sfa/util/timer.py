import time
from typing import Any, Callable, Tuple


def get_exec_time(func: Callable) -> Tuple[Any, float]:
    """
    Return the execution time of a given function.

    :param func:
    :return:
    """
    t1 = time.time()
    results = func()
    t2 = time.time()

    return results, (t2 - t1)
