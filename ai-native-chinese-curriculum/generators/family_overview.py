"""
Generation Layer prototype (Blueprint v1.0, Layer 3).

Reads the Content Layer (Markdown + YAML in mandarin-1.2/) for one Unit and
renders a family-facing "Unit Overview" HTML page. This is a renderer, not a
data store: nothing here is canonical, it only reads and projects.

Design notes (v4, per teacher review round 3):
- Visual language borrows the "bordered card + solid color header bar"
  structure common to unit-planning templates, not any one template's
  literal design. All five header bars (and the hero) share ONE muted
  accent color — variety lives at the item level (pills), not the
  structural level, per feedback that too many distinct hues read as
  "花哨" (gaudy) and clashed with the page background.
- Header bar text is deliberately one type-scale step larger than the
  content inside its section, so headings read as headings.
- Headings: 学习目标 Learning Objectives / 学习材料 Learning Materials /
  文化 Culture / 单元考核 Unit Assessments / 核心词汇语法 Key Vocabulary
  & Grammar. No "Transfer Goal" section — folded into Unit Assessments,
  where the final project already lives as a Performance Task entry.
- Body content under each heading is English (the audience is non-native
  Chinese speakers); Chinese titles/vocab stay Chinese+pinyin+English
  since that IS the content being taught, not explanatory prose.
- All Chinese text renders in Kaiti (楷体) via font-family fallback: list
  Kaiti variants before the CJK gothic/sans fallback so browsers pick it
  for CJK codepoints while Latin text keeps the sans stack untouched.

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
    t = (assessment_type or "").lower()
    if "diagnostic" in t:
        return "摸底测验 Diagnostic", "gold", "单元初 Start of Unit"
    if "project" in t or "performance task" in t:
        return "项目 Project", "jade", "单元末 End of Unit"
    if "summative" in t:
        return "阶段测验 Summative", "vermilion", "单元末 End of Unit"
    return esc(assessment_type), "plum", ""


def pill(label, color):
    return f'<span class="pill pill-{color}">{esc(label)}</span>'


def status_pill(status):
    return "" if status in ("canonical", "draft") else pill("编写中 In Progress", "muted")


def render(unit_dir, course_title="Mandarin 1.2"):
    overview_fm, overview_body = load_frontmatter(f"{unit_dir}/01-overview.md")
    objectives_en = bullet_list(body_section(overview_body, "Learning Objectives (English)"))
    language_forms = overview_fm.get("language_forms") or []
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

    grammar_html = "\n".join(f"<li>{esc(g)}</li>" for g in language_forms)

    today = datetime.date.today().isoformat()

    return TEMPLATE.format(
        course=esc(course_title),
        unit_label=esc(overview_fm.get("unit")),
        big_idea_zh=esc((overview_fm.get("big_idea") or "").split("(")[0].strip()),
        big_idea_en=esc(overview_fm.get("big_idea", "").split("(", 1)[-1].rstrip(")")),
        objectives_html="\n".join(f"<li>{esc(o)}</li>" for o in objectives_en),
        content_html=content_html,
        culture_html=culture_html,
        assessment_html=assessment_html,
        grammar_html=grammar_html,
        vocab_html=vocab_html,
        generated_date=today,
    )


TEMPLATE = """<title>{course} · {unit_label} Family Overview 家长概览</title>
<style>
:root {{
  --bg: #F3EFE3;
  --surface: #FFFFFF;
  --ink: #221F1A;
  --muted: #6E6656;
  --line: #221F1A;
  --bar: #3E5D66;
  --bar-ink: #FBF6EA;
  --c-plum: #6A4E9E;
  --c-jade: #2F7A56;
  --c-gold: #B4791C;
  --c-vermilion: #B0402F;
  --c-teal: #1E7A88;
  --c-muted: #8A8272;
  --font-latin: -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  --font-kai: "Kaiti SC", "STKaiti", "KaiTi", "AR PL KaitiM GB", "BiauKai", serif;
  --font-mono: ui-monospace, "SFMono-Regular", "Liberation Mono", monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #171913; --surface: #1F2219; --ink: #EDE7DC; --muted: #A9A28F; --line: #E9E3D4;
    --bar: #4C7079; --bar-ink: #FBF6EA;
    --c-plum: #B7A0EC; --c-jade: #7FCBA6; --c-gold: #E5B75E; --c-vermilion: #E38271; --c-teal: #6FC7D6; --c-muted: #B5AC98;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #171913; --surface: #1F2219; --ink: #EDE7DC; --muted: #A9A28F; --line: #E9E3D4;
  --bar: #4C7079; --bar-ink: #FBF6EA;
  --c-plum: #B7A0EC; --c-jade: #7FCBA6; --c-gold: #E5B75E; --c-vermilion: #E38271; --c-teal: #6FC7D6; --c-muted: #B5AC98;
}}
:root[data-theme="light"] {{
  --bg: #F3EFE3; --surface: #FFFFFF; --ink: #221F1A; --muted: #6E6656; --line: #221F1A;
  --bar: #3E5D66; --bar-ink: #FBF6EA;
  --c-plum: #6A4E9E; --c-jade: #2F7A56; --c-gold: #B4791C; --c-vermilion: #B0402F; --c-teal: #1E7A88; --c-muted: #8A8272;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: var(--font-latin), var(--font-kai);
  line-height: 1.6;
}}
.page {{ max-width: 760px; margin: 0 auto; padding: 2.4rem 1.4rem 5rem; }}
.hero {{
  border-radius: 14px;
  padding: 2.4rem 1.9rem 2rem;
  margin-bottom: 1.6rem;
  background: var(--bar);
  color: var(--bar-ink);
}}
.eyebrow {{
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.72rem;
  opacity: 0.92;
}}
h1 {{
  margin: 0.5rem 0 0.1rem;
  font-size: clamp(2.1rem, 6vw, 2.9rem);
  font-weight: 400;
  text-wrap: balance;
}}
.hero .en-title {{
  font-family: var(--font-latin);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  font-size: clamp(0.95rem, 2.4vw, 1.15rem);
  opacity: 0.95;
  margin: 0 0 0.9rem;
}}
.hero .subtitle {{ font-family: var(--font-latin); font-size: 0.98rem; opacity: 0.95; margin: 0; max-width: 48ch; }}

section {{
  background: var(--surface);
  border: 2px solid var(--line);
  border-radius: 10px;
  margin-bottom: 1.3rem;
  overflow: hidden;
}}
.bar {{
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  padding: 0.7rem 1.2rem;
  background: var(--bar);
  color: var(--bar-ink);
  font-weight: 800;
  font-size: 1.25rem;
}}
.bar .en {{ font-family: var(--font-latin); font-weight: 700; font-size: 0.72em; opacity: 0.92; color: var(--bar-ink); }}
.sec-body {{ padding: 1.3rem 1.4rem 1.4rem; }}

ul.list {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.7rem; font-size: 0.95rem; }}
ul.list li {{ display: flex; flex-wrap: wrap; align-items: center; gap: 0.55rem; }}
.zh {{ font-weight: 700; }}
.en {{ color: var(--muted); font-size: 0.92em; font-family: var(--font-latin); }}
.pill {{
  font-family: var(--font-mono), var(--font-kai);
  font-size: 0.68rem;
  letter-spacing: 0.02em;
  border-radius: 4px;
  padding: 0.15rem 0.5rem;
  white-space: nowrap;
  border: 1.5px solid currentColor;
}}
.pill-plum {{ color: var(--c-plum); }}
.pill-jade {{ color: var(--c-jade); }}
.pill-gold {{ color: var(--c-gold); }}
.pill-vermilion {{ color: var(--c-vermilion); }}
.pill-teal {{ color: var(--c-teal); }}
.pill-muted {{ color: var(--c-muted); }}
.phase {{ font-family: var(--font-latin); font-size: 0.8rem; color: var(--muted); }}

ol.objectives {{ margin: 0; padding-left: 1.2rem; font-family: var(--font-latin); font-size: 0.95rem; }}
ol.objectives li {{ margin-bottom: 0.5rem; }}

.grammar-note {{ font-family: var(--font-latin); color: var(--muted); font-size: 0.8rem; margin: 1rem 0 0.4rem; text-transform: uppercase; letter-spacing: 0.05em; }}
ul.grammar {{ margin: 0; padding-left: 1.2rem; font-family: var(--font-latin); color: var(--ink); font-size: 0.95rem; }}
ul.grammar li {{ margin-bottom: 0.3rem; }}

table {{ width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }}
table th, table td {{ text-align: left; padding: 0.35rem 0.5rem; border-bottom: 1px solid var(--bg); font-size: 0.92rem; }}
table th {{ color: var(--muted); font-weight: 700; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; font-family: var(--font-latin); }}
.vocab-wrap {{ overflow-x: auto; }}

footer {{ font-family: var(--font-latin); color: var(--muted); font-size: 0.78rem; text-align: center; margin-top: 2.5rem; }}
</style>

<div class="page">
  <div class="hero">
    <div class="eyebrow">{course} · {unit_label}</div>
    <h1>{big_idea_zh}</h1>
    <p class="en-title">{big_idea_en}</p>
    <p class="subtitle">What we're learning this unit, and how we'll check it's landing — for families and anyone following along.</p>
  </div>

  <section>
    <div class="bar">学习目标 <span class="en">Learning Objectives</span></div>
    <div class="sec-body">
      <ol class="objectives">
        {objectives_html}
      </ol>
    </div>
  </section>

  <section>
    <div class="bar">学习材料 <span class="en">Learning Materials</span></div>
    <div class="sec-body">
      <ul class="list">
        {content_html}
      </ul>
    </div>
  </section>

  <section>
    <div class="bar">文化 <span class="en">Culture</span></div>
    <div class="sec-body">
      <ul class="list">
        {culture_html}
      </ul>
    </div>
  </section>

  <section>
    <div class="bar">单元考核 <span class="en">Unit Assessments</span></div>
    <div class="sec-body">
      <ul class="list">
        {assessment_html}
      </ul>
    </div>
  </section>

  <section>
    <div class="bar">核心词汇语法 <span class="en">Key Vocabulary &amp; Grammar</span></div>
    <div class="sec-body">
      <div class="vocab-wrap">
        <table>
          <tr><th>中文</th><th>拼音</th><th>English</th></tr>
          {vocab_html}
        </table>
      </div>
      <p class="grammar-note">Grammar &amp; language forms</p>
      <ul class="grammar">
        {grammar_html}
      </ul>
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
