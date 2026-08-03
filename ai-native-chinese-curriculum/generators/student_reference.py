"""
Generation Layer renderer (Blueprint v1.0, Layer 3): student-facing Unit
reference page.

Reads the Content Layer (Markdown + YAML in mandarin-1.2/) for one Unit and
renders a static HTML "Unit reference page" for students. This is a
reference/search tool, not a portal: no login, no device sync, no progress
tracking. It's deliberately richer than generators/family_overview.py:
full vocabulary (searchable), full story/content text where the source data
has it, the real Cycle-by-cycle teaching flow, and any Quizlet/YouTube/
worksheet links exactly as captured in the source Markdown.

This renderer never invents a link, a translation, or filler content for a
stub. If the Content Layer doesn't have something yet (e.g. a story's Text /
Media section is still "> 待补充"), the page says so plainly instead of
guessing — same rule as family_overview.py's design notes: 宁可省略，不要瞎翻.

Dates are a known trap (see 08-curriculum-intelligence.md and
family_overview.py's design notes): the Cycle dates in 02-teaching/*.md are
whatever calendar date the *previous* school year's slides happened to fall
on, and will drift for the current cohort. Unlike the family overview (which
drops specific dates entirely), this page keeps them because they show the
real order/pacing a student can study from — but the Teaching Flow section
opens with an explicit disclaimer, and Assessment entries never repeat
`administered` dates; they point to Schoology instead.

Usage: python3 student_reference.py <unit_dir> <output_html_path>
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
    """Extract text under a '## heading...' line (heading may be a prefix
    of the full line, since some files append parenthetical notes to the
    same heading) up to the next '## '."""
    m = re.search(
        rf"^## {re.escape(heading)}.*?\n(.*?)(?=^## |\Z)", body, re.S | re.M
    )
    return m.group(1).strip() if m else ""


def bullet_list(section_text):
    return [
        line.lstrip("-").strip()
        for line in section_text.splitlines()
        if line.strip().startswith("-")
    ]


def esc(s):
    return html.escape(str(s or ""))


_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_CODE = re.compile(r"`([^`]+)`")


def inline_md(text):
    """Minimal inline Markdown -> HTML: links, bold, code. Escapes first,
    so this is safe against raw HTML in source files."""
    text = esc(text)
    text = _LINK.sub(
        lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>',
        text,
    )
    text = _BOLD.sub(lambda m: f"<strong>{m.group(1)}</strong>", text)
    text = _CODE.sub(lambda m: f"<code>{m.group(1)}</code>", text)
    return text


_PENDING_MARKERS = ("待补充", "TODO", "尚未上传", "待确认")


def is_pending(section_text):
    t = section_text.strip()
    if not t:
        return True
    return t.startswith(">") and any(m in t for m in _PENDING_MARKERS)


def render_blocks(text):
    """Render a chunk of body Markdown (bullet lists, blockquotes,
    paragraphs) to HTML. Not a general Markdown parser — just what the
    Content Layer's fixed sub-headings (Overview / Text-Media / Activities /
    Extensions / Teacher Notes) actually contain. Groups run by *line kind*
    (list / quote / paragraph) rather than by blank-line-separated blocks,
    since source files often put a lead-in sentence directly above a bullet
    list with no blank line between them."""
    out = []
    buf, buf_kind = [], None

    def flush():
        if not buf:
            return
        if buf_kind == "list":
            items = "".join(f"<li>{inline_md(l)}</li>" for l in buf)
            out.append(f'<ul class="md-list">{items}</ul>')
        elif buf_kind == "quote":
            out.append(f'<p class="md-quote">{inline_md(" ".join(buf))}</p>')
        else:
            out.append(f"<p>{inline_md(' '.join(buf))}</p>")

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush()
            buf.clear()
            buf_kind = None
            continue
        if line.startswith("|"):
            flush()
            buf.clear()
            buf_kind = None
            continue  # tables are handled by the dedicated vocab parser
        if line.startswith("-"):
            kind, content = "list", line[1:].strip()
        elif line.startswith(">"):
            kind, content = "quote", line.lstrip(">").strip()
        else:
            kind, content = "para", line
        if kind != buf_kind:
            flush()
            buf.clear()
            buf_kind = kind
        buf.append(content)
    flush()
    return "\n".join(out)


def section_html(body, heading, pending_label="内容整理中 · Content coming soon"):
    text = body_section(body, heading)
    if is_pending(text):
        return f'<p class="pending">{esc(pending_label)}</p>'
    rendered = render_blocks(text)
    return rendered if rendered else f'<p class="pending">{esc(pending_label)}</p>'


def vocab_rows_from_text(text, source_label):
    rows = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3:
            continue
        zh, py, en = cells
        if zh in ("中文", "---") or set(zh) <= {"-"}:
            continue
        rows.append({"zh": zh, "py": py, "en": en, "source": source_label or ""})
    return rows


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
        return "摸底测验 Diagnostic", "gold", False
    if "project" in t or "performance task" in t:
        return "项目 Project", "jade", True
    if "summative" in t:
        return "阶段测验 Summative", "vermilion", False
    return esc(assessment_type), "plum", False


def pill(label, color):
    return f'<span class="pill pill-{color}">{esc(label)}</span>'


def status_pill(status):
    return "" if status in ("canonical", "draft") else pill("编写中 In Progress", "muted")


def vocab_table_html(rows, with_source=True):
    if not rows:
        return ""
    head = "<tr><th>中文</th><th>拼音</th><th>English</th>" + ("<th>来源 Source</th>" if with_source else "") + "</tr>"
    body_rows = []
    for r in rows:
        search_key = esc(f"{r['zh']} {r['py']} {r['en']} {r['source']}".lower())
        cells = f"<td class='zh'>{esc(r['zh'])}</td><td>{esc(r['py']) or '—'}</td><td>{esc(r['en']) or '—'}</td>"
        if with_source:
            cells += f"<td class='src'>{esc(r['source'])}</td>"
        body_rows.append(f'<tr data-search="{search_key}">{cells}</tr>')
    return f"<table>{head}{''.join(body_rows)}</table>"


def content_card(fm, body, type_map, type_key, extra_sections=()):
    label, color = type_map.get(fm.get(type_key), (fm.get(type_key) or "", "plum"))
    own_vocab = vocab_rows_from_text(body_section(body, "Vocabulary"), None)
    vocab_html = ""
    if own_vocab:
        rows_html = "".join(
            f"<tr><td class='zh'>{esc(r['zh'])}</td><td>{esc(r['py']) or '—'}</td><td>{esc(r['en']) or '—'}</td></tr>"
            for r in own_vocab
        )
        vocab_html = (
            "<h4>生词 Vocabulary</h4>"
            f"<div class='vocab-wrap'><table><tr><th>中文</th><th>拼音</th><th>English</th></tr>{rows_html}</table></div>"
        )
    search_key = esc(f"{fm.get('title')} {fm.get('english')} {fm.get('pinyin')} {label}".lower())
    extra_html = "".join(
        f"<h4>{esc(h)}</h4>{section_html(body, key)}" for h, key in extra_sections
    )
    return f"""
    <article class="card" data-type="{esc(fm.get(type_key))}" data-search="{search_key}">
      <div class="bar"><span class="zh">{esc(fm.get('title'))}</span><span class="en">{esc(fm.get('english'))}</span></div>
      <div class="card-body">
        <div class="badges">{pill(label, color)}{status_pill(fm.get('status'))}</div>
        {f"<p class='pinyin'>{esc(fm.get('pinyin'))}</p>" if fm.get('pinyin') else ""}
        <h4>概述 Overview</h4>
        {section_html(body, "Overview")}
        {vocab_html}
        <h4>正文 / 媒体 Text &amp; Media</h4>
        {section_html(body, "Text / Media")}
        <h4>课堂活动 Activities</h4>
        {section_html(body, "Activities")}
        <h4>延伸 Extensions</h4>
        {section_html(body, "Extensions")}
        {extra_html}
      </div>
    </article>"""


_DAY_BLOCK = re.compile(r"(?m)^### (.+?)\n(.*?)(?=^### |\Z)", re.S)


def cycle_card(fm, body):
    timeline = body_section(body, "教学内容时间线")
    days_html = "".join(
        f'<div class="day"><div class="day-label">{esc(h.strip())}</div>{render_blocks(b)}</div>'
        for h, b in _DAY_BLOCK.findall(timeline)
    )
    vocab_note = body_section(body, "涉及的核心词汇")
    notes = body_section(body, "备注")
    return f"""
    <article class="card">
      <div class="bar"><span class="zh">{esc(fm.get('cycle'))}</span>
        <span class="en date-ref">{esc(fm.get('date_range'))} · 去年参考日期 last year's reference dates</span></div>
      <div class="card-body">
        <div class="timeline">{days_html}</div>
        {f"<h4>本 Cycle 涉及的核心词汇/句型</h4>{render_blocks(vocab_note)}" if vocab_note.strip() else ""}
        {f"<h4>备注 Notes</h4>{render_blocks(notes)}" if notes.strip() else ""}
      </div>
    </article>"""


def assessment_card(fm, body):
    label, color, is_project = classify_assessment(fm.get("assessment_type"))
    search_key = esc(f"{fm.get('title')} {label}".lower())
    if is_project:
        sections = "".join(
            f"<h4>{esc(h)}</h4>{section_html(body, key)}"
            for h, key in [
                ("驱动问题 Driving Question", "Driving Question"),
                ("任务说明 Instructions", "Instructions"),
                ("评分标准 Rubric", "Rubric"),
                ("参考资源 Resources", "Resources"),
                ("范例 Examples", "Examples"),
            ]
        )
        return f"""
        <article class="card" data-search="{search_key}">
          <div class="bar"><span class="zh">{esc(fm.get('title'))}</span></div>
          <div class="card-body">
            <div class="badges">{pill(label, color)}{status_pill(fm.get('status'))}</div>
            {sections}
          </div>
        </article>"""
    return f"""
    <article class="card compact" data-search="{search_key}">
      <div class="bar"><span class="zh">{esc(fm.get('title'))}</span></div>
      <div class="card-body">
        <div class="badges">{pill(label, color)}{status_pill(fm.get('status'))}</div>
        <p class="pending">具体安排与提交方式请在 Schoology 查看 · See Schoology for schedule and submission.</p>
      </div>
    </article>"""


def render(unit_dir, course_title="Mandarin 1.2"):
    overview_fm, overview_body = load_frontmatter(f"{unit_dir}/01-overview.md")
    objectives = bullet_list(body_section(overview_body, "Learning Objectives"))
    objectives_en = bullet_list(body_section(overview_body, "Learning Objectives (English)"))
    language_forms = overview_fm.get("language_forms") or []

    def entries(dir_glob):
        out = []
        for path in sorted(glob.glob(dir_glob)):
            if path.endswith("README.md"):
                continue
            out.append(load_frontmatter(path))
        return out

    content_entries = entries(f"{unit_dir}/03-content/*.md")
    culture_entries = entries(f"{unit_dir}/04-culture/*.md")
    assessment_entries = entries(f"{unit_dir}/06-assessment/*.md")
    cycle_entries = entries(f"{unit_dir}/02-teaching/cycle-*.md")

    vocab_fm, vocab_body = load_frontmatter(f"{unit_dir}/05-resources/vocabulary-my-day.md")
    master_vocab = vocab_rows_from_text(vocab_body, vocab_fm.get("title") or "生词表 Vocabulary List")
    for fm, body in content_entries + culture_entries:
        master_vocab += vocab_rows_from_text(body_section(body, "Vocabulary"), fm.get("title"))

    content_html = "\n".join(content_card(fm, body, CONTENT_TYPE, "content_type") for fm, body in content_entries)
    culture_html = "\n".join(content_card(fm, body, CULTURE_TYPE, "culture_type") for fm, body in culture_entries)
    cycle_html = "\n".join(cycle_card(fm, body) for fm, body in cycle_entries)
    assessment_html = "\n".join(assessment_card(fm, body) for fm, body in assessment_entries)

    objectives_html = "\n".join(
        f"<li><span class='zh'>{esc(zh)}</span>" + (f"<span class='en'>{esc(en)}</span>" if en else "") + "</li>"
        for zh, en in zip(objectives, objectives_en + [""] * len(objectives))
    )
    grammar_html = "\n".join(f"<li>{esc(g)}</li>" for g in language_forms)

    today = datetime.date.today().isoformat()

    return TEMPLATE.format(
        course=esc(course_title),
        unit_label=esc(overview_fm.get("unit")),
        big_idea_zh=esc((overview_fm.get("big_idea") or "").split("(")[0].strip()),
        big_idea_en=esc(overview_fm.get("big_idea", "").split("(", 1)[-1].rstrip(")")),
        objectives_html=objectives_html,
        grammar_html=grammar_html,
        vocab_html=vocab_table_html(master_vocab, with_source=True),
        content_html=content_html,
        culture_html=culture_html,
        cycle_html=cycle_html,
        assessment_html=assessment_html,
        generated_date=today,
    )


TEMPLATE = """<title>{course} · {unit_label} Student Reference 学生检索页面</title>
<style>
:root {{
  --bg: #F3EFE3; --surface: #FFFFFF; --ink: #221F1A; --muted: #6E6656; --line: #221F1A;
  --bar: #3E5D66; --bar-ink: #FBF6EA;
  --c-plum: #6A4E9E; --c-jade: #2F7A56; --c-gold: #B4791C; --c-vermilion: #B0402F; --c-teal: #1E7A88; --c-muted: #8A8272;
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
body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: var(--font-latin), var(--font-kai); line-height: 1.6; }}
.page {{ max-width: 860px; margin: 0 auto; padding: 2.4rem 1.4rem 5rem; }}
.hero {{ border-radius: 14px; padding: 2.2rem 1.9rem 1.9rem; margin-bottom: 1rem; background: var(--bar); color: var(--bar-ink); }}
.eyebrow {{ font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.14em; font-size: 0.72rem; opacity: 0.92; }}
h1 {{ margin: 0.5rem 0 0.1rem; font-size: clamp(2rem, 5.5vw, 2.7rem); font-weight: 400; text-wrap: balance; }}
.hero .en-title {{ font-family: var(--font-latin); font-weight: 800; text-transform: uppercase; letter-spacing: 0.03em; font-size: clamp(0.9rem, 2.2vw, 1.05rem); opacity: 0.95; margin: 0 0 0.9rem; }}
.hero .subtitle {{ font-family: var(--font-latin); font-size: 0.95rem; opacity: 0.95; margin: 0 0 1.1rem; max-width: 56ch; }}
.search-wrap {{ margin-top: 0.4rem; }}
#search {{
  width: 100%; padding: 0.75rem 1rem; border-radius: 8px; border: none; font-size: 1rem;
  font-family: var(--font-latin), var(--font-kai); background: var(--surface); color: var(--ink);
}}
.search-hint {{ font-family: var(--font-latin); font-size: 0.75rem; opacity: 0.85; margin: 0.4rem 0 0; }}
nav.jump {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0 0 1.6rem; }}
nav.jump a {{
  font-family: var(--font-latin); font-size: 0.82rem; font-weight: 700; text-decoration: none; color: var(--ink);
  border: 1.5px solid var(--line); border-radius: 999px; padding: 0.3rem 0.85rem;
}}
section {{ margin-bottom: 2rem; }}
section > h2 {{ font-size: 1.3rem; margin: 0 0 0.9rem; display: flex; align-items: baseline; gap: 0.5rem; }}
section > h2 .en {{ font-family: var(--font-latin); font-weight: 700; font-size: 0.65em; color: var(--muted); }}
.section-note {{ font-family: var(--font-latin); color: var(--muted); font-size: 0.82rem; margin: -0.4rem 0 1rem; }}
.card {{ background: var(--surface); border: 2px solid var(--line); border-radius: 10px; margin-bottom: 1.1rem; overflow: hidden; }}
.card .bar {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.5rem; padding: 0.65rem 1.1rem; background: var(--bar); color: var(--bar-ink); font-weight: 800; font-size: 1.15rem; }}
.card .bar .en {{ font-family: var(--font-latin); font-weight: 700; font-size: 0.68em; opacity: 0.92; color: var(--bar-ink); }}
.card .bar .date-ref {{ opacity: 0.85; }}
.card-body {{ padding: 1.1rem 1.3rem 1.3rem; }}
.card-body h4 {{ font-family: var(--font-latin); text-transform: uppercase; letter-spacing: 0.04em; font-size: 0.78rem; color: var(--muted); margin: 1.1rem 0 0.4rem; }}
.card-body h4:first-of-type {{ margin-top: 0.2rem; }}
.badges {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.3rem; }}
.pinyin {{ font-family: var(--font-latin); color: var(--muted); font-size: 0.88rem; margin: 0.2rem 0 0.6rem; }}
.pill {{ font-family: var(--font-mono), var(--font-kai); font-size: 0.68rem; letter-spacing: 0.02em; border-radius: 4px; padding: 0.15rem 0.5rem; white-space: nowrap; border: 1.5px solid currentColor; }}
.pill-plum {{ color: var(--c-plum); }} .pill-jade {{ color: var(--c-jade); }} .pill-gold {{ color: var(--c-gold); }}
.pill-vermilion {{ color: var(--c-vermilion); }} .pill-teal {{ color: var(--c-teal); }} .pill-muted {{ color: var(--c-muted); }}
.pending {{ font-family: var(--font-latin); color: var(--muted); font-style: italic; font-size: 0.9rem; margin: 0; }}
.md-quote {{ font-family: var(--font-latin); color: var(--muted); font-size: 0.92rem; margin: 0; }}
ul.md-list {{ margin: 0; padding-left: 1.2rem; font-size: 0.95rem; }}
ul.md-list li {{ margin-bottom: 0.3rem; }}
.vocab-wrap {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }}
table th, table td {{ text-align: left; padding: 0.35rem 0.5rem; border-bottom: 1px solid var(--bg); font-size: 0.92rem; }}
table th {{ color: var(--muted); font-weight: 700; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; font-family: var(--font-latin); }}
table td.zh {{ font-weight: 700; }}
table td.src {{ font-family: var(--font-latin); color: var(--muted); font-size: 0.82rem; }}
.timeline {{ display: flex; flex-direction: column; gap: 0.9rem; }}
.day {{ border-left: 3px solid var(--bar); padding-left: 0.9rem; }}
.day-label {{ font-family: var(--font-latin); font-weight: 800; font-size: 0.82rem; color: var(--bar); margin-bottom: 0.25rem; }}
ol.objectives {{ margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 0.5rem; }}
ol.objectives li {{ font-size: 0.98rem; }}
ol.objectives .en {{ display: block; font-family: var(--font-latin); color: var(--bar-ink); opacity: 0.85; font-size: 0.8em; margin-top: 0.1rem; }}
ul.grammar {{ margin: 0; padding-left: 1.2rem; font-family: var(--font-latin); font-size: 0.92rem; }}
footer {{ font-family: var(--font-latin); color: var(--muted); font-size: 0.78rem; text-align: center; margin-top: 2.5rem; }}
[data-search].is-hidden {{ display: none !important; }}
</style>

<div class="page">
  <div class="hero">
    <div class="eyebrow">{course} · {unit_label} · Student Reference 学生检索页面</div>
    <h1>{big_idea_zh}</h1>
    <p class="en-title">{big_idea_en}</p>
    <p class="subtitle">A searchable reference for this unit — vocabulary, story text, the real Cycle-by-cycle
      flow, and assessment info. Not a portal: no login, no progress tracking. For due dates and submitting
      work, use Schoology.</p>
    <div class="search-wrap">
      <input id="search" type="text" placeholder="搜索生词、故事、Cycle… Search vocabulary, stories, cycles…" autocomplete="off">
      <p class="search-hint">Searches vocabulary (中文/拼音/English), stories, and culture content on this page.</p>
    </div>
  </div>

  <nav class="jump">
    <a href="#vocabulary">生词表 Vocabulary</a>
    <a href="#content">学习内容 Content</a>
    <a href="#culture">文化 Culture</a>
    <a href="#teaching-flow">课堂进度 Teaching Flow</a>
    <a href="#assessments">单元考核 Assessments</a>
  </nav>

  <section id="vocabulary">
    <h2>生词表 <span class="en">Vocabulary</span></h2>
    <p class="section-note">All vocabulary introduced in this unit, combined from every story, culture item,
      and the unit word list. Use the search box above to filter.</p>
    <div class="vocab-wrap">{vocab_html}</div>
    <h4 style="font-family: var(--font-latin); text-transform: uppercase; letter-spacing: 0.04em; font-size: 0.78rem; color: var(--muted); margin: 1.2rem 0 0.4rem;">语法 / 语言形式 Grammar &amp; Language Forms</h4>
    <ul class="grammar">{grammar_html}</ul>
  </section>

  <section id="objectives">
    <h2>学习目标 <span class="en">Learning Objectives</span></h2>
    <div class="card"><div class="card-body"><ol class="objectives">{objectives_html}</ol></div></div>
  </section>

  <section id="content">
    <h2>学习内容 <span class="en">Content</span></h2>
    {content_html}
  </section>

  <section id="culture">
    <h2>文化 <span class="en">Culture</span></h2>
    {culture_html}
  </section>

  <section id="teaching-flow">
    <h2>课堂进度 <span class="en">Teaching Flow</span></h2>
    <p class="section-note">Cycle dates are the reference dates from when this unit was last taught — this
      year's actual calendar will differ. Check Schoology for this year's schedule.</p>
    {cycle_html}
  </section>

  <section id="assessments">
    <h2>单元考核 <span class="en">Assessments</span></h2>
    {assessment_html}
  </section>

  <footer>Auto-generated from the curriculum database · {generated_date} · updates automatically as the data changes</footer>
</div>

<script>
(function() {{
  var input = document.getElementById('search');
  var searchables = Array.prototype.slice.call(document.querySelectorAll('[data-search]'));
  input.addEventListener('input', function() {{
    var q = input.value.trim().toLowerCase();
    searchables.forEach(function(el) {{
      var match = !q || (el.getAttribute('data-search') || '').indexOf(q) !== -1;
      el.classList.toggle('is-hidden', !match);
    }});
  }});
}})();
</script>
"""

if __name__ == "__main__":
    unit_dir = sys.argv[1]
    out_path = sys.argv[2]
    html_out = render(unit_dir)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"wrote {out_path}")
