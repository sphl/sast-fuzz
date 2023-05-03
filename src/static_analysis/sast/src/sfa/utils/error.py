import inspect
import logging
from os import path
from typing import Optional


def log_assert(condition: bool, message: Optional[str] = None, logger: logging.Logger = logging.getLogger(),
               sys_exit: bool = False) -> None:
    """Wrapper for logging failed assertions.

    :param condition: Assertion condition
    :param message: Error message
    :param logger: System logger
    :param sys_exit: Exit system, or raise exception
    :return: None
    """
    try:
        assert condition
    except AssertionError as err:
        if message is None:
            # Construct an error message from the calling frame
            last_stack = inspect.stack()[-3]
            file, line = last_stack[1:3]

            message = f"Assertion failed @ {path.basename(file)}:{line}"

        logger.error(message)

        if sys_exit:
            exit(1)
        else:
            raise err
