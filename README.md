# GitHub Comment Script

Adds **15–25 comments** to a single issue on one of your GitHub repos each time you run it. All comments go to one issue so it’s easy to manage.

## Setup

1. **GitHub token**  
   Create a [Personal Access Token](https://github.com/settings/tokens) with **repo** scope.  
   Do not commit the token; use an environment variable.

2. **Install**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure** (pick one):
   - **Environment variables** (recommended):
     - `GITHUB_TOKEN` – your token  
     - `GITHUB_REPO` – `username/repo` (e.g. `nadda/my-project`)
   - Or edit `config.py` and set `GITHUB_REPO` and `GITHUB_TOKEN` (avoid committing the token).

## Run

```bash
# With env vars
export GITHUB_TOKEN=ghp_xxxx
export GITHUB_REPO=your-username/your-repo
python add_comments.py
```

Or set `GITHUB_REPO` and `GITHUB_TOKEN` in `config.py` and run:

```bash
python add_comments.py
```

Each run adds 15–25 comments to one issue. The first run creates an issue titled **"Script comments"** if you don’t set `GITHUB_ISSUE_NUMBER`; later runs use that same issue.

## Customize

- **Which issue:** Set `ISSUE_NUMBER` in `config.py` or `GITHUB_ISSUE_NUMBER` in the environment to post to that issue instead of creating/finding "Script comments".
- **Comment text:** Edit the `COMMENTS` list in `comments_data.py`.
