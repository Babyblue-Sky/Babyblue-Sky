# Stock Price Dip Alert Agent

Watches VOO / QQQM / VXF / VXUS and emails an alert the moment any of them drops **10% below its 52-week high**, so it's easier to buy the dip.

## How it works

- Checks prices hourly during market hours (9:30am-4pm ET, Monday-Friday)
- The trigger is **dynamic**: it recomputes the 52-week high from live data on every run instead of using a fixed dollar amount, so it keeps working as the funds trend upward with no yearly manual reset
- Each ticker is alerted at most once per day; once it has fired, it won't fire again the same day even if the price keeps falling — it resets the next day
- Data source: Yahoo Finance via `yfinance`, free, no API key required
- Delivery: sent from your own Gmail account through Gmail's SMTP server, so a copy lands in "Sent"

## One-time setup

### 1. Generate a Gmail App Password

1. Open [Google Account security settings](https://myaccount.google.com/security) and make sure 2-Step Verification is turned on
2. Search for "App Passwords" and create a new one (any name works, e.g. "stock-alert-agent")
3. Copy the generated 16-character password — you'll need it next

### 2. Add repository secrets

In this repo, go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret name | Value |
|---|---|
| `GMAIL_USER` | Your Gmail address, e.g. `your-name@gmail.com` |
| `GMAIL_APP_PASSWORD` | The 16-character App Password from the previous step |
| `ALERT_TO_EMAIL` | (Optional) recipient address; defaults to `GMAIL_USER` if omitted |

### 3. Make sure Actions is enabled

If the **Actions** tab shows the workflow as disabled, click to enable it.

## Manual testing

Go to **Actions → Stock Price Dip Alert → Run workflow** to trigger a run on demand instead of waiting for the next scheduled hour — useful for confirming the email actually arrives.

## Adjusting the trigger

`DIP_THRESHOLD_PCT = 0.10` at the top of `check_prices.py` is the drawdown threshold applied to all four tickers — change that one number to adjust it. The `TICKERS` list can be edited to add or remove symbols.

## State file

`state.json` is committed automatically by the workflow and records the last alert date per ticker, which is how the "at most once per day" rule is enforced. No need to edit it by hand.
