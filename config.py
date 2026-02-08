"""
Configuration for the GitHub comment script.
Edit these or use environment variables.
"""
import os

# Your GitHub repo: "username/repo-name"
# Override with env: GITHUB_REPO
GITHUB_REPO = os.environ.get("GITHUB_REPO", "Naddaa2000/Asaam-chatbot")

# Personal Access Token with 'repo' scope.
# Override with env: GITHUB_TOKEN (recommended, do not commit tokens)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "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")

# Issue number to add comments to. If 0, script will create a new issue.
# Override with env: GITHUB_ISSUE_NUMBER
ISSUE_NUMBER = int(os.environ.get("GITHUB_ISSUE_NUMBER", "0"))
