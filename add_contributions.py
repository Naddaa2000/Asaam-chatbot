#!/usr/bin/env python3
"""
Long-running contribution bot.
Commits Monday–Friday, 9 AM – 7 PM PKT (Pakistan Standard Time) only.
Each day it picks a random number of contributions (15-40) and spreads them
across the work window with random delays.

Run from inside the repo, or pass the repo path as first argument or CONTRIB_REPO_PATH env var.
"""
import os
import random
import subprocess
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

CONTRIB_FILE = "contributions.txt"
COUNT_MIN, COUNT_MAX = 15, 40

PKT = ZoneInfo("Asia/Karachi")
WORK_START_HOUR = 9   # 9 AM PKT
WORK_END_HOUR = 19    # 7 PM PKT
WORK_DAYS = range(0, 5)  # Monday=0 … Friday=4


def run_cmd(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(result.stderr or result.stdout, end="", flush=True)
        result.check_returncode()
    return result


def now_pkt():
    return datetime.now(PKT)


def is_work_window(dt=None):
    """Return True if dt falls on Mon-Fri between 9 AM and 7 PM PST."""
    dt = dt or now_pkt()
    return dt.weekday() in WORK_DAYS and WORK_START_HOUR <= dt.hour < WORK_END_HOUR



def seconds_until_next_window():
    """Calculate seconds until the next valid work window opens."""
    dt = now_pkt()

    # Find the next weekday at WORK_START_HOUR
    candidate = dt.replace(hour=WORK_START_HOUR, minute=0, second=0, microsecond=0)

    # If we're before today's window and today is a workday, use today
    if dt.weekday() in WORK_DAYS and dt.hour < WORK_START_HOUR:
        pass  # candidate is already correct (today at 9 AM)
    else:
        # Move to the next day
        candidate += timedelta(days=1)
        # Skip weekends
        while candidate.weekday() not in WORK_DAYS:
            candidate += timedelta(days=1)

    wait = (candidate - dt).total_seconds()
    return max(wait, 0)


def seconds_until_window_ends():
    """Seconds remaining in the current work window."""
    dt = now_pkt()
    end_today = dt.replace(hour=WORK_END_HOUR, minute=0, second=0, microsecond=0)
    return max((end_today - dt).total_seconds(), 0)


def resolve_repo():
    """Determine the repo path and return (contrib_path, git_prefix)."""
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
        return os.path.join(repo_path, CONTRIB_FILE), f"git -C {repr(repo_path)}"
    else:
        run_cmd("git rev-parse --is-inside-work-tree", check=True)
        return CONTRIB_FILE, "git"


def do_contribution(contrib_path, git_prefix, index, total):
    """Create one commit and push it."""
    ts = now_pkt().strftime("%Y-%m-%d %H:%M:%S %Z")
    with open(contrib_path, "a") as f:
        f.write(f"{ts} contribution {index}/{total}\n")
    run_cmd(f"{git_prefix} add {CONTRIB_FILE}")
    run_cmd(f'{git_prefix} commit -m "contribution {index}/{total}"')
    push_result = run_cmd(f"{git_prefix} push", check=False)
    if push_result.returncode != 0:
        stderr = push_result.stderr or ""
        if "rejected" in stderr or "non-fast-forward" in stderr.lower():
            run_cmd(f"{git_prefix} push --force-with-lease")
        else:
            push_result.check_returncode()


def run_daily_session(contrib_path, git_prefix):
    """Spread a random number of contributions across the remaining work window."""
    remaining_secs = seconds_until_window_ends()
    if remaining_secs < 120:
        print("[info] Less than 2 minutes left in today's window, skipping.", flush=True)
        return

    count = random.randint(COUNT_MIN, COUNT_MAX)
    # Evenly space commits across the remaining window, with some jitter
    base_gap = remaining_secs / count
    print(
        f"[{now_pkt().strftime('%Y-%m-%d %H:%M %Z')}] "
        f"Planning {count} contributions over ~{remaining_secs/60:.0f} min "
        f"(~{base_gap:.0f}s apart)",
        flush=True,
    )

    for i in range(1, count + 1):
        if not is_work_window():
            print("[info] Work window ended, stopping for today.", flush=True)
            break

        do_contribution(contrib_path, git_prefix, i, count)
        print(f"  [{now_pkt().strftime('%H:%M')}] {i}/{count} pushed.", flush=True)

        if i < count:
            # Random delay: 50%-150% of the base gap, at least 30s
            jitter = random.uniform(0.5, 1.5)
            gap = max(base_gap * jitter, 30)
            # Don't sleep past the end of the window
            gap = min(gap, seconds_until_window_ends())
            if gap > 0:
                time.sleep(gap)

    print(f"[{now_pkt().strftime('%Y-%m-%d %H:%M %Z')}] Daily session done.", flush=True)


def main():
    contrib_path, git_prefix = resolve_repo()
    print(
        f"Contribution bot started. Schedule: Mon-Fri {WORK_START_HOUR}:00–{WORK_END_HOUR}:00 PKT",
        flush=True,
    )

    while True:
        if is_work_window():
            run_daily_session(contrib_path, git_prefix)

        # Sleep until the next window
        wait = seconds_until_next_window()
        if wait > 0:
            next_open = now_pkt() + timedelta(seconds=wait)
            print(
                f"[{now_pkt().strftime('%Y-%m-%d %H:%M %Z')}] "
                f"Sleeping until {next_open.strftime('%A %Y-%m-%d %H:%M %Z')} "
                f"({wait/3600:.1f}h)",
                flush=True,
            )
            time.sleep(wait)
        else:
            # Tiny sleep to avoid a tight loop at boundary
            time.sleep(5)


if __name__ == "__main__":
    main()
