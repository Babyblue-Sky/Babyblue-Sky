"""
Generation Layer prototype (Blueprint v1.0, Layer 3).

Reads the Content Layer (Markdown + YAML in mandarin-1.2/) for one Unit and
renders a family-facing "Unit Overview" HTML page. This is a renderer, not a
data store: nothing here is canonical, it only reads and projects.

Usage: python3 family_overview.py <unit_dir> <output_html_path>
"""
import re
import sys
import glob
import html
import datetime
import yaml


def load_frontmatter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    fm = yaml.safe_load(m.group(1)) or {}
    return fm, m.group(2)


def body_section(body, heading):
    """Extract the text under a '## heading' up to the next '##'."""
    m = re.search(
        rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", body, re.S | re.M
    )
    return m.group(1).strip() if m else ""


def bullet_list(section_text):
    return [
        line.lstrip("-").strip()
        for line in section_text.splitlines()
        if line.strip().startswith("-")
    ]


def load_entries(dir_glob, skip="README.md"):
    entries = []
    for path in sorted(glob.glob(dir_glob)):
        if path.endswith(skip):
            continue
        fm, body = load_frontmatter(path)
        entries.append(fm)
    return entries


def vocab_rows(path, limit=12):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    rows = []
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3 or cells[0] in ("中文", "---"):
            continue
        if set(cells[0]) <= {"-"}:
            continue
        rows.append(cells)
        if len(rows) >= limit:
            break
    return rows


def esc(s):
    return html.escape(str(s or ""))


def status_note(status):
    return "" if status in ("canonical", "draft") else " · 内容陆续补充中"


def render(unit_dir, course_title="Mandarin 1.2"):
    overview_fm, overview_body = load_frontmatter(f"{unit_dir}/01-overview.md")
    objectives = bullet_list(body_section(overview_body, "Learning Objectives"))
    content_items = load_entries(f"{unit_dir}/03-content/*.md")
    culture_items = load_entries(f"{unit_dir}/04-culture/*.md")
    assessment_items = load_entries(f"{unit_dir}/06-assessment/*.md")
    vocab = vocab_rows(f"{unit_dir}/05-resources/vocabulary-my-day.md")

    content_html = "\n".join(
        f'<li><span class="zh">{esc(c.get("title"))}</span>'
        f'<span class="en">{esc(c.get("english"))}</span>'
        f'<span class="tag">{esc(status_note(c.get("status")))}</span></li>'
        for c in content_items
    )

    culture_type_labels = {
        "reading": "阅读 · Reading",
        "craft": "手工/技艺 · Craft",
        "project": "项目 · Project",
        "field-trip": "校外活动 · Field Trip",
        "other": "文化活动 · Activity",
    }
    culture_html = "\n".join(
        f'<li><span class="zh">{esc(c.get("title"))}</span>'
        f'<span class="pill">{esc(culture_type_labels.get(c.get("culture_type"), c.get("culture_type")))}</span>'
        f'<span class="tag">{esc(status_note(c.get("status")))}</span></li>'
        for c in culture_items
    )

    assessment_html = "\n".join(
        f'<li><span class="zh">{esc(a.get("title"))}</span>'
        f'<span class="pill">{esc(a.get("assessment_type"))}</span>'
        + (f'<span class="date">{esc(a.get("administered"))}</span>' if a.get("administered") else "")
        + f'<span class="tag">{esc(status_note(a.get("status")))}</span></li>'
        for a in assessment_items
    )

    vocab_html = "\n".join(
        f"<tr><td>{esc(zh)}</td><td>{esc(py) or '—'}</td><td>{esc(en)}</td></tr>"
        for zh, py, en in vocab
    )

    today = datetime.date.today().isoformat()

    return TEMPLATE.format(
        course=esc(course_title),
        unit_label=esc(overview_fm.get("unit")),
        big_idea=esc(overview_fm.get("big_idea")),
        objectives_html="\n".join(f"<li>{esc(o)}</li>" for o in objectives),
        transfer_goal=esc(overview_fm.get("transfer_goal")),
        content_html=content_html,
        culture_html=culture_html,
        assessment_html=assessment_html,
        vocab_html=vocab_html,
        generated_date=today,
    )


TEMPLATE = """<title>{course} · {unit_label} 家长概览</title>
<style>
:root {{
  --bg: #EEF0E6;
  --surface: #FBFAF4;
  --ink: #21231C;
  --muted: #5B6055;
  --accent: #A93B2E;
  --jade: #46664A;
  --line: #D8D6C6;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #15160F;
    --surface: #1C1D15;
    --ink: #E7E4D6;
    --muted: #A3A692;
    --accent: #E2705F;
    --jade: #7FA57F;
    --line: #34362A;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #15160F; --surface: #1C1D15; --ink: #E7E4D6;
  --muted: #A3A692; --accent: #E2705F; --jade: #7FA57F; --line: #34362A;
}}
:root[data-theme="light"] {{
  --bg: #EEF0E6; --surface: #FBFAF4; --ink: #21231C;
  --muted: #5B6055; --accent: #A93B2E; --jade: #46664A; --line: #D8D6C6;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, "Segoe UI", "PingFang SC", "Noto Sans SC", "Helvetica Neue", sans-serif;
  line-height: 1.6;
}}
.page {{
  max-width: 720px;
  margin: 0 auto;
  padding: 3rem 1.5rem 5rem;
}}
.eyebrow {{
  font-family: ui-monospace, "Liberation Mono", monospace;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.72rem;
  color: var(--accent);
}}
h1 {{
  font-family: Georgia, "Liberation Serif", "Noto Serif SC", serif;
  font-size: clamp(1.7rem, 4vw, 2.3rem);
  margin: 0.4rem 0 0.2rem;
  text-wrap: balance;
}}
.bigidea {{
  color: var(--muted);
  font-size: 1.05rem;
  margin: 0 0 2.2rem;
}}
section {{
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 1.4rem 1.6rem;
  margin-bottom: 1.2rem;
}}
section h2 {{
  font-family: Georgia, "Liberation Serif", "Noto Serif SC", serif;
  font-size: 1.15rem;
  margin: 0 0 0.9rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid var(--line);
}}
ul.list {{
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}}
ul.list li {{
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.6rem;
}}
.zh {{ font-weight: 600; }}
.en {{ color: var(--muted); font-size: 0.92rem; }}
.pill {{
  font-family: ui-monospace, "Liberation Mono", monospace;
  font-size: 0.68rem;
  letter-spacing: 0.04em;
  color: var(--jade);
  border: 1px solid var(--jade);
  border-radius: 3px;
  padding: 0.1rem 0.4rem;
}}
.date {{ font-family: ui-monospace, "Liberation Mono", monospace; font-size: 0.8rem; color: var(--muted); }}
.tag {{ font-size: 0.82rem; color: var(--muted); font-style: italic; }}
ol.objectives {{ margin: 0; padding-left: 1.2rem; }}
ol.objectives li {{ margin-bottom: 0.4rem; }}
.transfer {{
  border-left: 3px solid var(--accent);
  padding-left: 0.9rem;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  font-variant-numeric: tabular-nums;
}}
table th, table td {{
  text-align: left;
  padding: 0.35rem 0.5rem;
  border-bottom: 1px solid var(--line);
  font-size: 0.92rem;
}}
table th {{ color: var(--muted); font-weight: 600; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; }}
.vocab-wrap {{ overflow-x: auto; }}
footer {{
  color: var(--muted);
  font-size: 0.78rem;
  text-align: center;
  margin-top: 2.5rem;
}}
</style>

<div class="page">
  <div class="eyebrow">{course} · {unit_label}</div>
  <h1>{big_idea}</h1>
  <p class="bigidea">这学期我们在学什么，以及会用什么方式检验学习成果——供家长参考。</p>

  <section>
    <h2>学习目标</h2>
    <ol class="objectives">
      {objectives_html}
    </ol>
  </section>

  <section>
    <h2>本单元的故事 / 阅读材料</h2>
    <ul class="list">
      {content_html}
    </ul>
  </section>

  <section>
    <h2>文化板块</h2>
    <ul class="list">
      {culture_html}
    </ul>
  </section>

  <section>
    <h2>评量安排</h2>
    <ul class="list">
      {assessment_html}
    </ul>
  </section>

  <section class="transfer">
    <h2>期末项目 / Transfer Goal</h2>
    <p>{transfer_goal}</p>
  </section>

  <section>
    <h2>核心词汇预览</h2>
    <div class="vocab-wrap">
      <table>
        <tr><th>中文</th><th>拼音</th><th>English</th></tr>
        {vocab_html}
      </table>
    </div>
  </section>

  <footer>此页面由课程数据库自动生成 · {generated_date} · 内容随课程数据更新</footer>
</div>
"""

if __name__ == "__main__":
    unit_dir = sys.argv[1]
    out_path = sys.argv[2]
    html_out = render(unit_dir)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"wrote {out_path}")
