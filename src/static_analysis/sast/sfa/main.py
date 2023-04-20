import argparse
from os import path

from sfa.logic.runner import run_sast_tools
from sfa.logic.tools.factory import SASTTool, SASTToolFactory


def sfa() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--subject-dir", metavar="<path>", dest="subject_dir", type=str, required=True,
                        help="Directory path to the program to be analyzed.")
    parser.add_argument("-o", "--output-file", metavar="<path>", dest="output_file", type=str, required=True,
                        help="Path to the output CSV file.")
    parser.add_argument("-x", "--exclude-tool", choices=SASTTool.values(), action="append", dest="excluded_tools",
                        default=list(), required=False, help="SAST tool(s) to be excluded from the analysis.")

    args = parser.parse_args()

    subject_dir = path.expanduser(args.subject_dir)
    output_file = path.expanduser(args.output_file)

    selected_tools = [tool for tool in SASTTool.values() if tool not in args.excluded_tools]

    assert path.exists(subject_dir), "ERROR: Subject directory does not exist!"
    assert path.exists(path.dirname(output_file)), "ERROR: Directory of output file does not exist!"
    assert len(selected_tools) >= 1, "ERROR: All SAST tools have been disabled!"

    factory = SASTToolFactory(subject_dir)
    runners = list(map(factory.get_runner, selected_tools))

    findings = run_sast_tools(runners)

    print(findings)

    return 0


def main() -> None:
    try:
        exit(sfa())
    except KeyboardInterrupt:
        print("Execution interrupted!")


if __name__ == "__main__":
    main()
