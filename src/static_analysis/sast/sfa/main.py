import argparse
import logging
import sys
from argparse import Namespace
from os import path

from sfa.logic.filters.factory import SASTFilter, SASTOutputFilterFactory
from sfa.logic.runner import run_sast_tools
from sfa.logic.tools.factory import SASTTool, SASTToolRunnerFactory
from sfa.utils.error import log_assert


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--subject-dir", metavar="<path>", dest="subject_dir", type=str, required=True,
                        help="Directory path to the program to be analyzed.")
    parser.add_argument("-i", "--sfi-file", metavar="<path>", dest="sfi_file", type=str, required=True,
                        help="Path to the SFI program inspection file.")
    parser.add_argument("-o", "--output-file", metavar="<path>", dest="output_file", type=str, required=True,
                        help="Path to the output CSV file.")
    parser.add_argument("-x", "--exclude-tool", choices=SASTTool.values(), action="append", dest="excluded_tools",
                        default=list(), required=False, help="SAST tool(s) to be excluded from the analysis.")
    parser.add_argument("-f", "--output-filter", choices=SASTFilter.values(), action="append", dest="output_filters",
                        default=list(), required=False, help="SAST output filter(s).")
    parser.add_argument("-p", "--parallel", action="store_true", dest="exec_parallel", default=False,
                        help="Execute the SAST tools in parallel.")

    return parser.parse_args()


def sfa() -> int:
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(asctime)s SFA[%(levelname)s]: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")
    logger = logging.getLogger()

    args = parse_args()

    subject_dir = path.expanduser(args.subject_dir)
    sfi_file = path.expanduser(args.sfi_file)

    output_file = path.expanduser(args.output_file)

    selected_tools = [tool for tool in SASTTool.values() if tool not in args.excluded_tools]
    selected_filters = args.output_filters

    log_assert(path.exists(subject_dir), "Subject directory does not exist!", sys_exit=True)
    log_assert(path.exists(sfi_file), "SFI program inspection file does not exist!", sys_exit=True)
    log_assert(path.exists(path.dirname(output_file)), "Directory of output file does not exist!", sys_exit=True)
    log_assert(len(selected_tools) >= 1, "All SAST tools have been disabled!", sys_exit=True)

    logger.info("Selected SAST tools: [%s]", ", ".join(selected_tools))

    tool_factory = SASTToolRunnerFactory(subject_dir)
    filter_factory = SASTOutputFilterFactory(sfi_file)

    runners = list(map(tool_factory.get_runner, selected_tools))
    filters = list(map(filter_factory.get_filter, selected_filters))

    findings = run_sast_tools(runners, filters, args.exec_parallel)

    print(findings)

    logger.info("Analysis finished!")

    return 0


def main() -> None:
    try:
        exit(sfa())
    except KeyboardInterrupt:
        print("Execution interrupted!")


if __name__ == "__main__":
    main()
