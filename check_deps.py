#!/usr/bin/env python
"""Script to download Python packages and search them for a regex

Requires pip, ag, zip, and tar on the system path.
"""

import argparse
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from pathlib import Path
from subprocess import CalledProcessError, run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        desc="Script to download and search Python packages listed in a text file",
    )
    parser.add_argument(
        "--file", required=True, help="csv file with the names of packages to check"
    )
    parser.add_argument(
        "--regex", required=True, help="Regular expression to run on each package"
    )
    parser.add_argument(
        "--concurrency",
        "-j",
        type=int,
        default=1,
        help="Number of concurrent processing threads",
    )
    return parser.parse_args()


def report_error(proc, package, topic):
    print(
        f"Problem {topic} {package}\n"
        f"stdout:\n{proc.stdout}\n"
        f"stderr:\n{proc.stderr}\n"
    )


def check_package(package, regex) -> bool:
    print(f"Processing {package}")
    path = Path(tempfile.mkdtemp())
    try:
        proc = run(
            ["pip", "download", "--no-deps", package],
            cwd=path,
            check=False,
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            report_error(proc, package, "downloading")
            return False

        for pkg_file in path.iterdir():
            if pkg_file.suffix == ".whl":
                proc = run(
                    ["unzip", pkg_file],
                    cwd=path,
                    check=True,
                    text=True,
                    capture_output=True,
                )
                if proc.returncode != 0:
                    report_error(proc, package, "unpacking")
                    return False
                break
            elif pkg_file.name.endswith(".tar.gz"):
                proc = run(
                    ["tar", "xf", pkg_file],
                    cwd=path,
                    check=True,
                    text=True,
                    capture_output=True,
                )
                if proc.returncode != 0:
                    report_error(proc, package, "unpacking")
                    return False
                break
        else:
            print(f"No package file found for {package}: {list(path.iterdir())}")
            return False

        proc = run(
            ["ag", regex, "--max-count=1"],
            cwd=path,
            text=True,
            capture_output=True,
        )

        if proc.returncode not in {0, 1}:
            report_error(proc, package, "searching")
            return False
    finally:
        shutil.rmtree(path)

    # No output means no match
    return bool(proc.stdout)


def main():
    """Main loop"""
    args = parse_args()
    packages = Path(args.file).read_text().splitlines()
    # Assume package name is first column in csv
    packages = [p.partition(",")[0] for p in packages]

    if args.concurrency > 1:
        with ThreadPoolExecutor(args.concurrency) as executor:
            hits = executor.map(check_package, packages, repeat(args.regex))
    else:
        hits = [check_package(p, args.regex) for p in packages]

    results = [p for p, h in zip(packages, hits) if h]

    print("\nMatches:")
    print("\n".join(results))


if __name__ == "__main__":
    main()
