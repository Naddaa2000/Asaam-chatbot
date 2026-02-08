#!/usr/bin/env python3
"""
Add 15-25 comments to a single issue on your GitHub repo.
Easy to manage: all comments go to one issue (create one if needed).

Setup:
  1. Create a GitHub Personal Access Token with 'repo' scope.
  2. Set GITHUB_TOKEN and GITHUB_REPO (env or in config.py).
  3. pip install -r requirements.txt
  4. python add_comments.py
"""
import random
import sys

from github import Github

import config
from comments_data import COMMENTS


def get_or_create_issue(repo):
    """Use existing issue or create one titled 'Script comments'."""
    if config.ISSUE_NUMBER and config.ISSUE_NUMBER > 0:
        return repo.get_issue(config.ISSUE_NUMBER)
    for issue in repo.get_issues(state="open"):
        if issue.title == "Script comments":
            return issue
    return repo.create_issue(
        title="Script comments",
        body="Comments added by add_comments.py. You can close this issue anytime.",
    )


def main():
    token = config.GITHUB_TOKEN
    repo_name = config.GITHUB_REPO

    if not token:
        print("Error: Set GITHUB_TOKEN (env or in config.py).")
        sys.exit(1)
    if not repo_name or "YOUR_USERNAME" in repo_name:
        print("Error: Set GITHUB_REPO to your 'username/repo' (env or config.py).")
        sys.exit(1)

    count = random.randint(15, 25)
    gh = Github(token)

    try:
        repo = gh.get_repo(repo_name)
    except Exception as e:
        print(f"Error: Could not access repo '{repo_name}'. {e}")
        sys.exit(1)

    issue = get_or_create_issue(repo)
    print(f"Adding {count} comments to issue #{issue.number} ({issue.title})")

    for i in range(count):
        body = random.choice(COMMENTS)
        try:
            issue.create_comment(body)
            print(f"  {i + 1}/{count}: {body!r}")
        except Exception as e:
            print(f"  Failed: {e}")
            break

    print("Done.")


if __name__ == "__main__":
    main()
