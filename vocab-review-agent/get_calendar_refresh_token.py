"""One-time script: get a Google Calendar OAuth refresh token for the
Vocab Review Agent's GitHub Action.

Run this ONCE, on your own computer -- it needs to open a browser window for
you to approve access, so it can't run inside GitHub Actions.

Setup before running (all one-time, in Google Cloud Console):
1. console.cloud.google.com -> create a project (or reuse one)
2. APIs & Services -> Library -> enable "Google Calendar API"
3. APIs & Services -> OAuth consent screen -> User Type: External.
   Publishing status "Testing" is fine -- add your own Google account under
   "Test users" so it can authorize without Google's app-review process.
4. APIs & Services -> Credentials -> Create Credentials -> OAuth client ID
   -> Application type: Desktop app -> Create
5. Download the JSON for that client (download icon next to it in the list)

Then, locally:
    pip install google-auth-oauthlib
    python get_calendar_refresh_token.py /path/to/downloaded_client.json

A browser window opens -- sign in and approve. Three values get printed at
the end; paste them into the GitHub repo's Settings -> Secrets and variables
-> Actions as:
    GOOGLE_CALENDAR_CLIENT_ID
    GOOGLE_CALENDAR_CLIENT_SECRET
    GOOGLE_CALENDAR_REFRESH_TOKEN
"""

import json
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

# Scoped to only creating/managing events -- this script (and the GitHub
# Action that uses the resulting token) never needs to read the rest of your
# calendar.
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python get_calendar_refresh_token.py /path/to/client_secret.json", file=sys.stderr)
        sys.exit(1)

    client_secret_path = sys.argv[1]
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
    # access_type=offline + prompt=consent guarantee a refresh_token comes
    # back even if you've authorized this app before.
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    if not creds.refresh_token:
        print("No refresh token came back -- try again (Google only issues one on first consent).", file=sys.stderr)
        sys.exit(1)

    with open(client_secret_path) as f:
        client_config = json.load(f)["installed"]

    print("\nAdd these three as GitHub repo secrets (Settings -> Secrets and variables -> Actions):\n")
    print(f"GOOGLE_CALENDAR_CLIENT_ID = {client_config['client_id']}")
    print(f"GOOGLE_CALENDAR_CLIENT_SECRET = {client_config['client_secret']}")
    print(f"GOOGLE_CALENDAR_REFRESH_TOKEN = {creds.refresh_token}")


if __name__ == "__main__":
    main()
