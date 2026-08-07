"""Delete-by-issue handler for the review page/email's "not mine, delete" link.

Why an issue instead of a button that calls the GitHub API directly: the
review page is a public, static GitHub Pages page with no server behind it.
A button that could delete data would need a write-scoped GitHub token
embedded in that public page's JavaScript -- anyone who found the URL could
read it out and edit the repo. Routing through "open a pre-filled GitHub
issue" instead needs no embedded secret at all: GitHub's existing login
(you're already signed in as the repo owner) is the auth, and this script
-- running in the Action with its own scoped token -- does the actual edit.

Triggered by .github/workflows/vocab-delete.yml on any new issue whose title
starts with "vocab-delete:" (exactly what the delete links pre-fill).
"""

import json
import os
import re
from pathlib import Path

import requests

DATA_FILE = Path(__file__).parent / "data" / "words.json"


def main() -> None:
    title = os.environ["ISSUE_TITLE"]
    match = re.match(r"^vocab-delete:\s*(.+)$", title.strip(), re.IGNORECASE)
    word = match.group(1).strip() if match else None

    words = json.loads(DATA_FILE.read_text()) if DATA_FILE.exists() else []

    removed = False
    if word:
        before = len(words)
        words = [w for w in words if w["word"].lower() != word.lower()]
        removed = len(words) < before

    if removed:
        DATA_FILE.write_text(json.dumps(words, indent=2, ensure_ascii=False) + "\n")
        comment = f'Removed "{word}" from the word bank.'
    elif word:
        comment = f'No word matching "{word}" was found in the word bank -- nothing removed.'
    else:
        comment = f"Couldn't parse a word out of the issue title (`{title}`) -- nothing removed."

    close_issue(comment)
    print(comment)


def close_issue(comment: str) -> None:
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]  # "owner/repo", set automatically by Actions
    issue_number = os.environ["ISSUE_NUMBER"]
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}

    requests.post(
        f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments",
        headers=headers,
        json={"body": comment},
        timeout=15,
    ).raise_for_status()
    requests.patch(
        f"https://api.github.com/repos/{repo}/issues/{issue_number}",
        headers=headers,
        json={"state": "closed", "state_reason": "completed"},
        timeout=15,
    ).raise_for_status()


if __name__ == "__main__":
    main()
