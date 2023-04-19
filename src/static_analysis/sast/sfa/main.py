import argparse
from os import path

from sfa.logic.tools.factory import SASTTool, SASTToolFactory
from sfa.logic.runner import run_sast_tools


def sfa() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--subject-dir", metavar="<dir-path>", dest="subject_dir", type=str, required=True,
                        help="Directory path to the program to be analyzed.")

    args = parser.parse_args()

    subject_dir = path.expanduser(args.subject_dir)

    assert path.exists(subject_dir)

    factory = SASTToolFactory(subject_dir)
    runners = list(map(factory.get_runner, [tool for tool in SASTTool]))

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
