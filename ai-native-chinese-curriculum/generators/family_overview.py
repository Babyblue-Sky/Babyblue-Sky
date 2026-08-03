"""
Generation Layer prototype (Blueprint v1.0, Layer 3).

Reads the Content Layer (Markdown + YAML in mandarin-1.2/) for one Unit and
renders a family-facing "Unit Overview" HTML page. This is a renderer, not a
data store: nothing here is canonical, it only reads and projects.

Design notes (v2, per teacher review):
- Bilingual section headings; one-line explanations are English-only
  (audience is non-native-Chinese-speaking families/students).
- Where a Chinese gloss would be inaccurate or ambiguous (e.g. "Transfer
  Goal" is UbD jargon with no settled Chinese term), the heading stays
  English-only rather than guessing.
- No literal per-lesson dates: only a rough phase ("Start of Unit" /
  "End of Unit"), since day-to-day pacing drifts every year.
- Colored pill labels per type, reused across Content/Culture/Assessment
  so the same visual language marks "what kind of thing is this" everywhere.

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


# type -> (bilingual label, pill color token)
CONTENT_TYPE = {
    "story": ("故事 Story", "plum"),
    "news": ("新闻 News", "teal"),
    "song": ("歌曲 Song", "gold"),
    "video": ("视频 Video", "teal"),
    "audio": ("音频 Audio", "teal"),
}
CULTURE_TYPE = {
    "reading": ("阅读 Reading", "vermilion"),
    "craft": ("手工 Craft", "jade"),
    "project": ("项目 Project", "gold"),
    "field-trip": ("校外活动 Field Trip", "teal"),
    "other": ("文化活动 Activity", "plum"),
}


def classify_assessment(assessment_type):
    """Map a free-text assessment_type onto a (bilingual label, color, phase)."""
    t = (assessment_type or "").lower()
    if "diagnostic" in t:
        return "摸底测验 Diagnostic", "gold", "单元初 · Start of Unit"
    if "project" in t or "performance task" in t:
        return "项目 Project", "jade", "单元末 · End of Unit"
    if "summative" in t:
        return "阶段测验 Summative", "vermilion", "单元末 · End of Unit"
    return esc(assessment_type), "plum", ""


def pill(label, color):
    return f'<span class="pill pill-{color}">{esc(label)}</span>'


def status_pill(status):
    return "" if status in ("canonical", "draft") else pill("编写中 In Progress", "muted")


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
        f"{pill(*CONTENT_TYPE.get(c.get('content_type'), (c.get('content_type'), 'plum')))}"
        f"{status_pill(c.get('status'))}</li>"
        for c in content_items
    )

    culture_html = "\n".join(
        f'<li><span class="zh">{esc(c.get("title"))}</span>'
        f"{pill(*CULTURE_TYPE.get(c.get('culture_type'), (c.get('culture_type'), 'plum')))}"
        f"{status_pill(c.get('status'))}</li>"
        for c in culture_items
    )

    assessment_html = "\n".join(
        (lambda label, color, phase: (
            f'<li><span class="zh">{esc(a.get("title"))}</span>'
            f"{pill(label, color)}"
            + (f'<span class="phase">{esc(phase)}</span>' if phase else "")
            + f"{status_pill(a.get('status'))}</li>"
        ))(*classify_assessment(a.get("assessment_type")))
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


TEMPLATE = """<title>{course} · {unit_label} Family Overview 家长概览</title>
<style>
:root {{
  --bg: #F7F2E7;
  --surface: #FFFFFF;
  --ink: #2A241E;
  --muted: #8A8272;
  --line: #E8E1D2;
  --c-plum: #5B4B8A;
  --c-jade: #3F7A5E;
  --c-gold: #A97A1F;
  --c-vermilion: #B0402F;
  --c-teal: #2E7F8A;
  --c-muted: #8A8272;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #1B180F;
    --surface: #242019;
    --ink: #F1EAD9;
    --muted: #B5AC98;
    --line: #3A3428;
    --c-plum: #A996E8;
    --c-jade: #7ECBA6;
    --c-gold: #E0B45C;
    --c-vermilion: #E38271;
    --c-teal: #7AC9D6;
    --c-muted: #B5AC98;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #1B180F; --surface: #242019; --ink: #F1EAD9; --muted: #B5AC98; --line: #3A3428;
  --c-plum: #A996E8; --c-jade: #7ECBA6; --c-gold: #E0B45C; --c-vermilion: #E38271; --c-teal: #7AC9D6; --c-muted: #B5AC98;
}}
:root[data-theme="light"] {{
  --bg: #F7F2E7; --surface: #FFFFFF; --ink: #2A241E; --muted: #8A8272; --line: #E8E1D2;
  --c-plum: #5B4B8A; --c-jade: #3F7A5E; --c-gold: #A97A1F; --c-vermilion: #B0402F; --c-teal: #2E7F8A; --c-muted: #8A8272;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, "Segoe UI", "PingFang SC", "Noto Sans SC", "Helvetica Neue", sans-serif;
  line-height: 1.6;
}}
.page {{ max-width: 720px; margin: 0 auto; padding: 0 1.5rem 5rem; }}
.hero {{
  margin: 0 -1.5rem 2rem;
  padding: 2.6rem 1.8rem 2.2rem;
  background:
    linear-gradient(120deg, rgba(20,14,8,0.45) 0%, rgba(20,14,8,0.2) 42%, rgba(20,14,8,0) 68%),
    linear-gradient(100deg, #F3A46B 0%, #F0C25E 26%, #7FBFA8 55%, #4E6FA8 78%, #2C2560 100%);
  color: #FBF6EA;
}}
@media (min-width: 760px) {{ .hero {{ margin: 0 0 2rem; border-radius: 10px; }} }}
.eyebrow {{
  font-family: ui-monospace, "Liberation Mono", monospace;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.72rem;
  opacity: 0.9;
}}
h1 {{
  font-family: Georgia, "Liberation Serif", "Noto Serif SC", serif;
  font-size: clamp(1.8rem, 4.2vw, 2.5rem);
  margin: 0.5rem 0 0.3rem;
  text-wrap: balance;
  text-shadow: 0 1px 12px rgba(0,0,0,0.18);
}}
.subtitle {{ font-size: 1rem; opacity: 0.95; margin: 0; max-width: 46ch; }}
section {{
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 1.4rem 1.6rem;
  margin-bottom: 1.1rem;
}}
section h2 {{
  font-family: Georgia, "Liberation Serif", "Noto Serif SC", serif;
  font-size: 1.15rem;
  margin: 0 0 0.9rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid var(--line);
}}
section h2 .en {{ color: var(--muted); font-weight: 400; font-size: 0.9em; }}
ul.list {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.7rem; }}
ul.list li {{ display: flex; flex-wrap: wrap; align-items: center; gap: 0.55rem; }}
.zh {{ font-weight: 600; }}
.en {{ color: var(--muted); font-size: 0.92rem; }}
.pill {{
  font-family: ui-monospace, "Liberation Mono", monospace;
  font-size: 0.68rem;
  letter-spacing: 0.03em;
  border-radius: 4px;
  padding: 0.15rem 0.5rem;
  white-space: nowrap;
  border: 1px solid currentColor;
}}
.pill-plum {{ color: var(--c-plum); }}
.pill-jade {{ color: var(--c-jade); }}
.pill-gold {{ color: var(--c-gold); }}
.pill-vermilion {{ color: var(--c-vermilion); }}
.pill-teal {{ color: var(--c-teal); }}
.pill-muted {{ color: var(--c-muted); }}
.phase {{ font-size: 0.8rem; color: var(--muted); }}
ol.objectives {{ margin: 0; padding-left: 1.2rem; }}
ol.objectives li {{ margin-bottom: 0.4rem; }}
.transfer p {{ margin: 0 0 0.5rem; }}
.transfer .note {{ color: var(--muted); font-size: 0.88rem; }}
table {{ width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }}
table th, table td {{ text-align: left; padding: 0.35rem 0.5rem; border-bottom: 1px solid var(--line); font-size: 0.92rem; }}
table th {{ color: var(--muted); font-weight: 600; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; }}
.vocab-wrap {{ overflow-x: auto; }}
footer {{ color: var(--muted); font-size: 0.78rem; text-align: center; margin-top: 2.5rem; }}
</style>

<div class="page">
  <div class="hero">
    <div class="eyebrow">{course} · {unit_label}</div>
    <h1>{big_idea}</h1>
    <p class="subtitle">What we're learning this unit, and how we'll check it's landing — for families and anyone following along.</p>
  </div>

  <section>
    <h2>学习目标 <span class="en">Learning Objectives</span></h2>
    <ol class="objectives">
      {objectives_html}
    </ol>
  </section>

  <section>
    <h2>阅读材料 <span class="en">Stories &amp; Texts</span></h2>
    <ul class="list">
      {content_html}
    </ul>
  </section>

  <section>
    <h2>文化 <span class="en">Culture</span></h2>
    <ul class="list">
      {culture_html}
    </ul>
  </section>

  <section>
    <h2>评量 <span class="en">Assessments</span></h2>
    <ul class="list">
      {assessment_html}
    </ul>
  </section>

  <section class="transfer">
    <h2>Transfer Goal</h2>
    <p>{transfer_goal}</p>
    <p class="note">What students should be able to do with this beyond the unit itself.</p>
  </section>

  <section>
    <h2>核心词汇 <span class="en">Key Vocabulary</span></h2>
    <div class="vocab-wrap">
      <table>
        <tr><th>中文</th><th>拼音</th><th>English</th></tr>
        {vocab_html}
      </table>
    </div>
  </section>

  <footer>Auto-generated from the curriculum database · {generated_date} · updates automatically as the data changes</footer>
</div>
"""

if __name__ == "__main__":
    unit_dir = sys.argv[1]
    out_path = sys.argv[2]
    html_out = render(unit_dir)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"wrote {out_path}")
