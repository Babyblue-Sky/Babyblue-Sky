# Vocab Review Agent (v2 — GitHub-native)

Same idea as before — double-click a word while browsing, get it back weeks
later as a spaced-review reminder on your calendar (plus an email digest) —
rebuilt on a stack that doesn't depend on manually clicking the right
dropdown in a web editor to deploy. Everything
here is either a file in this repo or a GitHub Actions run, both of which are
directly inspectable (`git log`, Actions run logs) instead of living inside a
Google Apps Script black box.

## How it works

- **Chrome extension** (`extension/`) — double-click a word, or select a
  phrase and press Ctrl/Cmd+Shift+S. It looks the word up in Merriam-Webster
  directly from the browser and commits it to `data/words.json` in this repo
  via the GitHub API. No server in between.
- **`data/words.json`** — the word bank. This *is* the database; it's just a
  JSON file, so you can always open it and read exactly what's stored.
- **`generate_review.py`** — run by GitHub Actions weekly (Sundays) and
  monthly (2nd-to-last day of the month). It backfills any definition the
  extension couldn't fetch client-side (idioms, or words Merriam-Webster
  didn't have — using an optional Claude fallback), emails a digest of the
  words due for review, creates a Google Calendar reminder (same idea as the
  old Apps Script version — an actual event on your calendar, not just an
  email), and writes a self-contained interactive review page (flip the
  card, mark known/still learning) to `docs/vocab-review/index.html` for
  GitHub Pages.
- **`.github/workflows/vocab-review.yml`** — the schedule + the email-sending
  job. Reuses the same Gmail secrets as `stock-price-alert-agent`.

## One-time setup

### 1. Merriam-Webster keys

Same free keys as before (dictionaryapi.com/register/index) — Learner's +
Collegiate. You'll paste these in two places: the extension's `config.js`
(for instant lookups in the browser) and as repo secrets (so the Action can
backfill anything the browser missed).

### 2. A GitHub token for the extension

Create a **fine-grained personal access token** at
github.com/settings/tokens?type=beta, scoped to **only this repository**,
with **Contents: Read and write** permission and nothing else. This is the
one secret that lives in the browser extension, so keeping its scope this
narrow means the worst case if it ever leaked is someone editing this one
repo's files — not your account.

### 3. Configure the extension

On your computer (not on github.com — this file holds real secrets and must
never be committed), copy `extension/config.example.js` to
`extension/config.js` in the same folder, then fill in:
- `MW_LEARNERS_KEY`, `MW_COLLEGIATE_KEY`
- `GITHUB_TOKEN` (from step 2)
- `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_BRANCH` (defaults already point at
  this repo's `main` branch — if you're testing before this branch merges,
  temporarily point `GITHUB_BRANCH` at the feature branch instead)

`config.js` is gitignored on purpose, so there's no risk of it accidentally
ending up in a commit.

Then `chrome://extensions` → Developer mode → **Load unpacked** → select the
`extension/` folder.

### 4. Repo secrets (Settings → Secrets and variables → Actions)

Add:
- `MW_LEARNERS_KEY`, `MW_COLLEGIATE_KEY` — same values as step 1
- `ANTHROPIC_API_KEY` — optional, only needed if you want idioms / MW-misses
  backfilled automatically. Stays server-side only (unlike the old setup,
  this key never has to touch the browser at all).

`GMAIL_USER`, `GMAIL_APP_PASSWORD`, `ALERT_TO_EMAIL` should already exist
from `stock-price-alert-agent` — this workflow reuses them, nothing new to
set up there.

### 5. Google Calendar reminders

This needs a one-time OAuth authorization, done from your own computer (not
the browser extension, not GitHub) — a script in this folder walks you
through it:

```
pip install google-auth-oauthlib
python get_calendar_refresh_token.py /path/to/downloaded_client.json
```

Full instructions, including the Google Cloud Console steps to get that
`client.json` file, are in the docstring at the top of
`get_calendar_refresh_token.py`. It ends by printing three values — add them
as repo secrets: `GOOGLE_CALENDAR_CLIENT_ID`, `GOOGLE_CALENDAR_CLIENT_SECRET`,
`GOOGLE_CALENDAR_REFRESH_TOKEN`.

Skipping this is fine too — the review email still goes out either way, you
just won't get a calendar event alongside it.

### 6. (Optional) GitHub Pages, for the interactive flip-card review page

Settings → Pages → Source: **Deploy from a branch** → `main` / `/docs`. Then
add a repo **variable** (not secret) `VOCAB_PAGES_BASE_URL` set to your Pages
URL (e.g. `https://babyblue-sky.github.io/Babyblue-Sky`), so the review email
includes a working link to it. Skipping this step is fine — the review email
already contains the full list of due words with definitions either way, you
just won't get the tap-to-reveal card interface.

### 7. Test it

Actions tab → **Vocab Review** → **Run workflow** → pick `weekly`, check
`force`, run. Check the Action's log directly for exactly what happened — no
guessing whether a deploy went through.

## Why this instead of the Apps Script version

The old version's failure mode was fundamentally undiagnosable from outside a
browser session on your Google account — deployments, caching, and execution
all happened inside a system neither of us could query. Here, every piece
that used to be an opaque manual step is either a `git push` (extension
code), a file in the repo (word bank, review log), or a GitHub Actions run
with a log I can read directly. If something breaks, the fix is "read the
log, read the file, push a fix" instead of "screenshot the editor and guess."
