import argparse
from os import path

from sfa.logic.runner import run_sast_tools
from sfa.logic.tools.clangsa import ClangSA
from sfa.logic.tools.codeql import CodeQL
from sfa.logic.tools.flawfinder import Flawfinder
from sfa.logic.tools.infer import Infer
from sfa.logic.tools.sanitizer import Sanitizer


def sfa() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--subject-dir", metavar="<dir-path>", dest="subject_dir", type=str, required=True,
                        help="Directory path to the program to be analyzed.")

    args = parser.parse_args()

    subject_dir = path.expanduser(args.subject_dir)

    assert path.exists(subject_dir)

    sast_tools = [
        Flawfinder(subject_dir),
        Infer(subject_dir),
        CodeQL(subject_dir),
        ClangSA(subject_dir),
        Sanitizer(subject_dir)
    ]

    findings = run_sast_tools(sast_tools)

    print(findings)

    return 0


def main() -> None:
    try:
        exit(sfa())
    except KeyboardInterrupt:
        print("Execution interrupted!")


if __name__ == "__main__":
    main()
