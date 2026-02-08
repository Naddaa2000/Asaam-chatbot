#!/usr/bin/env python3
"""
Add 15-40 Git contributions (commits + push) to a repo.
Run from inside the repo, or pass the repo path as first argument or CONTRIB_REPO_PATH.
Uses random delays between each push (not all at once).
"""
import os
import random
import subprocess
import sys
import time
from datetime import datetime, timezone

CONTRIB_FILE = "contributions.txt"
COUNT_MIN, COUNT_MAX = 15, 40
DELAY_MIN, DELAY_MAX = 30, 300  # seconds between pushes


def run_cmd(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(result.stderr or result.stdout, end="")
        result.check_returncode()
    return result


def main():
    repo_path = None
    if len(sys.argv) > 1:
        repo_path = os.path.abspath(sys.argv[1])
    else:
        repo_path = os.environ.get("CONTRIB_REPO_PATH")
        if repo_path:
            repo_path = os.path.abspath(os.path.expanduser(repo_path))

    if repo_path:
        if not os.path.isdir(repo_path):
            print(f"Error: Not a directory: {repo_path}")
            sys.exit(1)
        run_cmd(f"git -C {repr(repo_path)} rev-parse --is-inside-work-tree", check=True)
        contrib_path = os.path.join(repo_path, CONTRIB_FILE)
        git_prefix = f"git -C {repr(repo_path)}"
    else:
        run_cmd("git rev-parse --is-inside-work-tree", check=True)
        contrib_path = CONTRIB_FILE
        git_prefix = "git"

    count = random.randint(COUNT_MIN, COUNT_MAX)
    print(f"Adding {count} contributions (commits + push) with random delays...")

    for i in range(count):
        with open(contrib_path, "a") as f:
            f.write(f"{datetime.now(timezone.utc).isoformat()} contribution {i + 1}/{count}\n")
        run_cmd(f"{git_prefix} add {CONTRIB_FILE}")
        run_cmd(f'{git_prefix} commit -m "contribution {i + 1}/{count}"')
        push_result = run_cmd(f"{git_prefix} push", check=False)
        if push_result.returncode != 0 and ("rejected" in (push_result.stderr or "") or "non-fast-forward" in (push_result.stderr or "").lower()):
            run_cmd(f"{git_prefix} push --force-with-lease")
        elif push_result.returncode != 0:
            push_result.check_returncode()
        gap = random.uniform(DELAY_MIN, DELAY_MAX)
        print(f"  {i + 1}/{count} pushed. Next in {gap:.0f}s")
        if i < count - 1:
            time.sleep(gap)

    print("Done.")


if __name__ == "__main__":
    main()
