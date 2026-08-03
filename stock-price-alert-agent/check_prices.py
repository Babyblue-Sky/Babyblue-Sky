"""Check VOO/QQQM/VXF/VXUS for a dip below their 52-week high and email an alert.

Triggers when a ticker's current price is at least DIP_THRESHOLD_PCT below its
trailing 52-week high. The threshold is percentage-based (not a fixed dollar
amount) so it keeps working as these funds trend upward over time -- no yearly
manual re-calibration needed.
"""

import json
import os
import smtplib
import sys
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path
from zoneinfo import ZoneInfo

import yfinance as yf

TICKERS = ["VOO", "QQQM", "VXF", "VXUS"]
DIP_THRESHOLD_PCT = 0.10
STATE_FILE = Path(__file__).parent / "state.json"
MARKET_TZ = ZoneInfo("America/New_York")


def market_is_open_now(now_et: datetime) -> bool:
    if now_et.weekday() >= 5:
        return False
    market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now_et <= market_close


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def send_email(subject: str, body: str) -> None:
    user = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    to_addr = os.environ.get("ALERT_TO_EMAIL", user)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(user, [to_addr], msg.as_string())


def check_ticker(ticker: str):
    hist = yf.Ticker(ticker).history(period="1y")
    if hist.empty:
        print(f"[{ticker}] no data returned, skipping", file=sys.stderr)
        return None
    high_52w = float(hist["High"].max())
    current = float(hist["Close"].iloc[-1])
    drop_pct = (high_52w - current) / high_52w
    return current, high_52w, drop_pct


def main() -> None:
    now_et = datetime.now(MARKET_TZ)
    if not market_is_open_now(now_et):
        print(f"Market closed at {now_et.isoformat()}, skipping check.")
        return

    today_str = now_et.date().isoformat()
    state = load_state()
    alerts = []

    for ticker in TICKERS:
        result = check_ticker(ticker)
        if result is None:
            continue
        current, high_52w, drop_pct = result
        print(f"[{ticker}] price={current:.2f} 52w_high={high_52w:.2f} drop={drop_pct:.1%}")

        if drop_pct >= DIP_THRESHOLD_PCT and state.get(ticker) != today_str:
            alerts.append((ticker, current, high_52w, drop_pct))
            state[ticker] = today_str

    if alerts:
        lines = [f"以下 ETF 已跌破 52 周高点的 {DIP_THRESHOLD_PCT:.0%}：", ""]
        for ticker, current, high_52w, drop_pct in alerts:
            lines.append(
                f"- {ticker}: 现价 ${current:.2f}，52周高点 ${high_52w:.2f}，回撤 {drop_pct:.1%}"
            )
        lines.append("")
        lines.append(f"检查时间（美东）：{now_et.strftime('%Y-%m-%d %H:%M %Z')}")
        body = "\n".join(lines)
        subject = f"股价提醒：{', '.join(a[0] for a in alerts)} 跌破 -{DIP_THRESHOLD_PCT:.0%} 触发线"
        send_email(subject, body)
        print(f"Sent alert email for: {[a[0] for a in alerts]}")
    else:
        print("No new dips to alert on.")

    save_state(state)


if __name__ == "__main__":
    main()
