"""Generate the weekly/monthly vocab review and email it.

Also backfills any word that was saved without a definition — the extension
only ever does a live Merriam-Webster lookup for type="word" (idioms and any
word MW can't find are saved with an empty definition on purpose, so no
dictionary/AI key has to live in the browser extension). This script fills
those in server-side, using MW first and an optional Claude fallback for
anything MW doesn't have, before building the review.

Usage: python generate_review.py weekly|monthly
"""

import html
import json
import os
import re
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests

AGENT_DIR = Path(__file__).parent
DATA_FILE = AGENT_DIR / "data" / "words.json"
REVIEW_LOG_FILE = AGENT_DIR / "data" / "review_log.json"
PAGE_FILE = AGENT_DIR.parent / "docs" / "vocab-review" / "index.html"

GITHUB_OWNER = "Babyblue-Sky"
GITHUB_REPO = "Babyblue-Sky"


def delete_issue_url(word: str) -> str:
    # Opens a pre-filled "New issue" form -- .github/workflows/vocab-delete.yml
    # picks it up from the title and removes the word. No write-scoped token
    # needed on the public review page/email for this (see delete_word.py).
    title = quote(f"vocab-delete: {word}")
    body = quote(f'Requesting removal of "{word}" from the word bank -- saved by mistake.')
    return f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/issues/new?title={title}&body={body}"


def load_words() -> list:
    return json.loads(DATA_FILE.read_text()) if DATA_FILE.exists() else []


def save_words(words: list) -> None:
    DATA_FILE.write_text(json.dumps(words, indent=2, ensure_ascii=False) + "\n")


# ---------- DICTIONARY LOOKUP (backfill only) ----------

def fetch_mw(word: str, dict_name: str, key: str) -> object:
    url = f"https://dictionaryapi.com/api/v3/references/{dict_name}/json/{word}"
    res = requests.get(url, params={"key": key}, timeout=15)
    res.raise_for_status()
    return res.json()


def is_usable_mw_entry(data: object) -> bool:
    return isinstance(data, list) and bool(data) and isinstance(data[0], dict) and "meta" in data[0]


def extract_audio_url(entry: dict) -> str:
    try:
        audio = entry["hwi"]["prs"][0]["sound"]["audio"]
    except (KeyError, IndexError):
        return ""
    if audio.startswith("bix"):
        subdir = "bix"
    elif audio.startswith("gg"):
        subdir = "gg"
    elif audio[0].isdigit():
        subdir = "number"
    else:
        subdir = audio[0]
    return f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{subdir}/{audio}.mp3"


def lookup_merriam_webster(word: str) -> dict | None:
    learners_key = os.environ.get("MW_LEARNERS_KEY", "")
    collegiate_key = os.environ.get("MW_COLLEGIATE_KEY", "")
    if not learners_key or not collegiate_key:
        return None

    data = fetch_mw(word, "learners", learners_key)
    used_learners = is_usable_mw_entry(data)
    if not used_learners:
        data = fetch_mw(word, "collegiate", collegiate_key)
    if not is_usable_mw_entry(data):
        return None

    entry = data[0]
    definition = (entry.get("shortdef") or [""])[0]

    example = ""
    try:
        for dt in entry["def"][0]["sseq"][0][0][1]["dt"]:
            if dt[0] == "vis":
                example = re.sub(r"\{it\}|\{/it\}", "", dt[1][0]["t"])
                break
    except (KeyError, IndexError):
        pass

    audio_url = extract_audio_url(entry)
    if not audio_url and used_learners:
        collegiate = fetch_mw(word, "collegiate", collegiate_key)
        if is_usable_mw_entry(collegiate):
            audio_url = extract_audio_url(collegiate[0])

    return {"definition": definition, "example": example, "audioUrl": audio_url}


def lookup_via_claude(term: str, is_idiom: bool) -> dict | None:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    prompt = (
        f'Define the English idiom/expression "{term}" in one simple sentence, then give one '
        'natural example sentence using it. Respond ONLY as JSON: {"definition": "...", "example": "..."}'
        if is_idiom else
        f'Define the English word "{term}" simply, like a learner\'s dictionary would, then give one '
        'natural example sentence using it. Respond ONLY as JSON: {"definition": "...", "example": "..."}'
    )
    res = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={"model": "claude-sonnet-4-6", "max_tokens": 300, "messages": [{"role": "user", "content": prompt}]},
        timeout=30,
    )
    res.raise_for_status()
    text = res.json()["content"][0]["text"]
    text = re.sub(r"```json|```", "", text).strip()
    parsed = json.loads(text)
    return {"definition": parsed["definition"], "example": parsed.get("example", ""), "audioUrl": ""}


def backfill_missing_definitions(words: list) -> bool:
    changed = False
    for w in words:
        if w.get("definition"):
            continue
        try:
            result = None if w["type"] == "idiom" else lookup_merriam_webster(w["word"])
            if result is None:
                result = lookup_via_claude(w["word"], w["type"] == "idiom")
            if result:
                w["definition"] = result["definition"]
                w["example"] = result["example"]
                w["audioUrl"] = result["audioUrl"]
                changed = True
        except Exception as e:  # noqa: BLE001 - one bad lookup shouldn't sink the whole run
            print(f"[backfill] {w['word']}: {e}", file=sys.stderr)
    return changed


# ---------- SELECT WORDS DUE FOR THIS REVIEW ----------

def _parse(iso: str) -> datetime:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def words_for_session(words: list, session_type: str, now: datetime) -> list:
    if session_type == "monthly":
        return [w for w in words if _parse(w["dateSaved"]).year == now.year and _parse(w["dateSaved"]).month == now.month]
    cutoff = now - timedelta(days=7)
    return [w for w in words if _parse(w["dateSaved"]) >= cutoff]


def is_second_to_last_day_of_month(now: datetime) -> bool:
    next_month = now.replace(day=28) + timedelta(days=4)
    last_day = (next_month.replace(day=1) - timedelta(days=1)).day
    return now.day == last_day - 1


# ---------- OUTPUT: EMAIL DIGEST + STATIC REVIEW PAGE ----------

def build_email_html(session_type: str, due_words: list, page_url: str | None) -> str:
    label = "Weekly" if session_type == "weekly" else "Monthly"
    rows = []
    for w in due_words:
        audio = f' <a href="{html.escape(w["audioUrl"])}">🔊 audio</a>' if w.get("audioUrl") else ""
        example = f'<div style="color:#8A8578;font-style:italic;margin-top:2px;">{html.escape(w["example"])}</div>' if w.get("example") else ""
        delete_link = f'<a href="{html.escape(delete_issue_url(w["word"]))}" style="font-size:11px;color:#B5AF9E;">✕ not mine, delete</a>'
        rows.append(f"""
          <div style="margin-bottom:18px;">
            <div style="display:flex;justify-content:space-between;align-items:baseline;">
              <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#B5AF9E;">{html.escape(w["type"])}</div>
              {delete_link}
            </div>
            <div style="font-size:18px;font-weight:700;">{html.escape(w["word"])}{audio}</div>
            <div style="margin-top:4px;">{html.escape(w["definition"]) or "(no definition found)"}</div>
            {example}
          </div>""")

    link = f'<p><a href="{html.escape(page_url)}">Open the interactive review →</a></p>' if page_url else ""
    return f"""
      <div style="font-family:Georgia,'Times New Roman',serif;color:#2B2A25;max-width:480px;">
        <h2>{label} Vocab Review — {len(due_words)} word{"s" if len(due_words) != 1 else ""}</h2>
        {link}
        {"".join(rows)}
      </div>"""


def build_review_page_html(session_type: str, due_words: list) -> str:
    words_json = json.dumps(
        [{"word": w["word"], "type": w["type"], "definition": w["definition"], "example": w["example"], "audioUrl": w.get("audioUrl", "")} for w in due_words]
    ).replace("</", "<\\/")

    return f"""<!DOCTYPE html>
<html>
<head>
<base target="_top">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vocabulary Review</title>
<style>
  body {{ font-family: Georgia, 'Times New Roman', serif; background: #F7F5F0; margin: 0; padding: 32px 20px; color: #2B2A25; display: flex; justify-content: center; }}
  .wrap {{ width: 100%; max-width: 420px; }}
  .eyebrow {{ font-family: -apple-system, sans-serif; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #8A8578; display: flex; justify-content: space-between; margin-bottom: 10px; }}
  .progress-track {{ height: 5px; background: #E7E3D8; border-radius: 3px; overflow: hidden; margin-bottom: 28px; }}
  .progress-fill {{ height: 100%; background: #3D5A4C; border-radius: 3px; transition: width 0.4s ease; }}
  .card {{ background: white; border: 1px solid #E7E3D8; border-radius: 16px; padding: 32px; min-height: 200px; cursor: pointer; box-shadow: 0 1px 4px rgba(0,0,0,0.04); position: relative; }}
  .btn-delete {{ position: absolute; top: 14px; right: 14px; font-family: -apple-system, sans-serif; font-size: 11px; color: #B5AF9E; text-decoration: none; }}
  .btn-delete:hover {{ color: #B5484A; }}
  .card h1 {{ font-size: 30px; margin: 0 0 6px 0; }}
  .card h2 {{ font-size: 22px; margin: 0 0 6px 0; }}
  .hint {{ color: #B5AF9E; font-size: 13px; font-style: italic; margin-top: 16px; }}
  .type-tag {{ font-family: -apple-system, sans-serif; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #B5AF9E; margin-bottom: 6px; }}
  .definition {{ font-size: 16px; line-height: 1.5; margin: 8px 0; }}
  .example {{ font-size: 14px; color: #8A8578; font-style: italic; border-left: 2px solid #E7E3D8; padding-left: 12px; }}
  .buttons {{ display: flex; gap: 12px; margin-top: 18px; }}
  button {{ font-family: -apple-system, sans-serif; flex: 1; padding: 12px; border-radius: 10px; border: none; font-size: 14px; font-weight: 600; cursor: pointer; }}
  .btn-learning {{ background: white; border: 1px solid #D9A05B; color: #9C6B2E; }}
  .btn-known {{ background: #3D5A4C; color: white; }}
  .btn-audio {{ background: none; border: none; font-size: 16px; cursor: pointer; margin-left: 6px; flex: none; padding: 0; }}
  .done {{ text-align: center; padding: 40px 20px; }}
  .empty {{ text-align: center; color: #8A8578; padding: 40px 20px; font-family: -apple-system, sans-serif; }}
</style>
</head>
<body>
<div class="wrap" id="app"></div>
<script>
  const words = {words_json};
  const sessionType = "{session_type}";
  let index = 0, flipped = false, known = 0, learning = 0;

  function deleteUrl(word) {{
    const title = encodeURIComponent('vocab-delete: ' + word);
    const body = encodeURIComponent('Requesting removal of "' + word + '" from the word bank -- saved by mistake.');
    return 'https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/issues/new?title=' + title + '&body=' + body;
  }}

  function render() {{
    const app = document.getElementById('app');
    if (words.length === 0) {{
      app.innerHTML = '<div class="empty">No words to review for this ' + sessionType + ' session.</div>';
      return;
    }}
    if (index >= words.length) {{
      app.innerHTML = '<div class="card done"><h2>Review complete</h2><p>' + known + ' known &middot; ' + learning + ' still learning</p></div>';
      return;
    }}
    const w = words[index];
    const pct = Math.round((index / words.length) * 100);
    app.innerHTML =
      '<div class="eyebrow"><span>' + (sessionType === 'monthly' ? 'Monthly Review' : 'Weekly Review') + '</span><span>' + (index + 1) + ' / ' + words.length + '</span></div>' +
      '<div class="progress-track"><div class="progress-fill" style="width:' + pct + '%"></div></div>' +
      '<div class="card" onclick="flip()">' +
        '<a class="btn-delete" target="_blank" rel="noopener" href="' + deleteUrl(w.word) + '" onclick="event.stopPropagation()">\\u2715 not mine, delete</a>' +
        (!flipped
          ? '<h1>' + w.word + '</h1><div class="hint">Tap to reveal definition</div>'
          : '<div class="type-tag">' + w.type + '</div>' +
            '<h2>' + w.word + (w.audioUrl ? ' <button class="btn-audio" onclick="event.stopPropagation(); playAudio(\\'' + w.audioUrl + '\\')">\\ud83d\\udd0a</button>' : '') + '</h2>' +
            '<div class="definition">' + (w.definition || '(no definition found)') + '</div>' +
            (w.example ? '<div class="example">' + w.example + '</div>' : '')
        ) +
      '</div>' +
      (flipped
        ? '<div class="buttons"><button class="btn-learning" onclick="rate(false)">Still learning</button><button class="btn-known" onclick="rate(true)">Know it</button></div>'
        : '');
  }}

  function flip() {{ flipped = true; render(); }}
  function rate(isKnown) {{ if (isKnown) known++; else learning++; index++; flipped = false; render(); }}
  function playAudio(url) {{ new Audio(url).play(); }}

  render();
</script>
</body>
</html>
"""


def refresh_calendar_access_token() -> str | None:
    client_id = os.environ.get("GOOGLE_CALENDAR_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CALENDAR_CLIENT_SECRET", "")
    refresh_token = os.environ.get("GOOGLE_CALENDAR_REFRESH_TOKEN", "")
    if not (client_id and client_secret and refresh_token):
        return None
    res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=15,
    )
    res.raise_for_status()
    return res.json()["access_token"]


def create_calendar_reminder(session_type: str, due_count: int, page_url: str | None, now: datetime) -> None:
    try:
        access_token = refresh_calendar_access_token()
    except Exception as e:  # noqa: BLE001 - a broken calendar token shouldn't sink an otherwise-successful run
        print(f"[calendar] couldn't refresh access token: {e}", file=sys.stderr)
        return
    if not access_token:
        print("Google Calendar not configured (missing GOOGLE_CALENDAR_* secrets) — skipping calendar reminder.")
        return

    # Mirrors the old Apps Script reminder times: 10am for the weekly review,
    # 6pm for the monthly one, same day the review runs.
    tz = ZoneInfo("America/New_York")
    local_now = now.astimezone(tz)
    hour = 10 if session_type == "weekly" else 18
    start = local_now.replace(hour=hour, minute=0, second=0, microsecond=0)
    end = start + timedelta(minutes=30)

    label = "Weekly" if session_type == "weekly" else "Monthly"
    description = f"{due_count} word{'s' if due_count != 1 else ''} due for review."
    if page_url:
        description += f"\n\nOpen the review: {page_url}"

    event = {
        "summary": f"{label} Vocab Review \U0001F4DA",
        "description": description,
        "start": {"dateTime": start.isoformat(), "timeZone": "America/New_York"},
        "end": {"dateTime": end.isoformat(), "timeZone": "America/New_York"},
    }
    try:
        res = requests.post(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers={"Authorization": f"Bearer {access_token}", "content-type": "application/json"},
            json=event,
            timeout=15,
        )
        res.raise_for_status()
    except Exception as e:  # noqa: BLE001 - same rationale as above
        print(f"[calendar] couldn't create event: {e}", file=sys.stderr)
        return
    print(f"Created calendar reminder for {start.isoformat()}.")


def send_email(subject: str, html_body: str) -> None:
    user = os.environ["GMAIL_USER"].strip()
    password = os.environ["GMAIL_APP_PASSWORD"].strip()
    to_addr = os.environ.get("ALERT_TO_EMAIL", "").strip() or user

    msg = MIMEText(html_body, "html")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(user, [to_addr], msg.as_string())


def log_review(session_type: str, due_words: list, session_id: str) -> None:
    log = json.loads(REVIEW_LOG_FILE.read_text()) if REVIEW_LOG_FILE.exists() else []
    log.append({"date": datetime.now(timezone.utc).isoformat(), "type": session_type, "words": [w["word"] for w in due_words]})
    REVIEW_LOG_FILE.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n")
    for w in due_words:
        w.setdefault("reviewedIn", []).append(session_id)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ("weekly", "monthly"):
        print("Usage: python generate_review.py weekly|monthly [--force]", file=sys.stderr)
        sys.exit(1)
    session_type = sys.argv[1]
    force = "--force" in sys.argv[2:]
    now = datetime.now(timezone.utc)

    # The monthly job is scheduled to run daily and no-ops until the right day
    # (mirrors the old "check every day, fire once" trigger) -- --force skips
    # this for manual/workflow_dispatch runs.
    if session_type == "monthly" and not force and not is_second_to_last_day_of_month(now):
        print(f"Not the monthly review day yet ({now.date().isoformat()}), skipping.")
        return

    words = load_words()
    if backfill_missing_definitions(words):
        save_words(words)

    due = words_for_session(words, session_type, now)
    if not due:
        print(f"No words due for {session_type} review.")
        return

    session_id = now.strftime("%G-W%V") if session_type == "weekly" else now.strftime("%Y-%m")

    page_html = build_review_page_html(session_type, due)
    PAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    PAGE_FILE.write_text(page_html)

    pages_base_url = os.environ.get("PAGES_BASE_URL", "").rstrip("/")
    page_url = f"{pages_base_url}/vocab-review/" if pages_base_url else None

    subject = f"{'Weekly' if session_type == 'weekly' else 'Monthly'} Vocab Review — {len(due)} word{'s' if len(due) != 1 else ''}"
    send_email(subject, build_email_html(session_type, due, page_url))
    create_calendar_reminder(session_type, len(due), page_url, now)

    log_review(session_type, due, session_id)
    save_words(words)
    print(f"Sent {session_type} review for {len(due)} words.")


if __name__ == "__main__":
    main()
