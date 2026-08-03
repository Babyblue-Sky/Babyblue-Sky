# Stock Price Dip Alert Agent

监控 VOO / QQQM / VXF / VXUS 四支 ETF，当任意一支跌破**52周高点的 10%**时，自动发邮件提醒，方便逢低加仓。

## 工作原理

- 交易时段内（美东 9:30am-4pm，周一到周五）每小时检查一次价格
- 触发线是**动态的**：每次都用当天实时数据重新计算 52 周高点，不是写死的固定金额，所以不需要每年手动重设
- 每支股票每天最多提醒一次；如果当天已经提醒过，即使继续下跌也不会重复发信，除非到了新的一天重新触发
- 数据来源：Yahoo Finance（通过 `yfinance`），免费、不需要 API key
- 发信方式：用你自己的 Gmail 账号通过 Gmail 官方 SMTP 服务器发送，所以"已发送"里会留记录

## 一次性设置

### 1. 生成 Gmail 应用专用密码

1. 打开 [Google 账号安全设置](https://myaccount.google.com/security)，确认已开启「两步验证」
2. 搜索「应用专用密码」(App Passwords)，创建一个新的（名称随意，比如 "stock-alert-agent"）
3. 复制生成的 16 位密码，稍后要用

### 2. 添加仓库 Secrets

在这个仓库的 **Settings → Secrets and variables → Actions → New repository secret**，添加：

| Secret 名 | 值 |
|---|---|
| `GMAIL_USER` | 你的 Gmail 地址，例如 `tiana.liao74@gmail.com` |
| `GMAIL_APP_PASSWORD` | 上一步生成的 16 位应用专用密码 |
| `ALERT_TO_EMAIL` | （可选）收件地址，不填则默认发给自己（即 `GMAIL_USER`） |

### 3. 确认 Actions 已启用

仓库的 **Actions** 标签页里如果显示 workflow 被禁用，点击启用即可。

## 手动测试

在 **Actions → Stock Price Dip Alert → Run workflow** 可以随时手动触发一次，不用等到下一个整点，方便验证邮件能正常收到。

## 调整触发线

`check_prices.py` 顶部的 `DIP_THRESHOLD_PCT = 0.10` 就是回撤百分比阈值，改这一个数字即可对四支股票统一调整；`TICKERS` 列表可以增删关注的股票。

## 状态文件

`state.json` 由 workflow 自动提交更新，记录每支股票"最近一次提醒的日期"，用来实现"每天最多提醒一次"。不需要手动编辑。
