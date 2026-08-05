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

Not live: this script renders a snapshot of whatever is currently in the
Content Layer. It does NOT watch or sync from the teacher's SMART Notebook
slides — a new day's slides only show up here after going through the
Import Pipeline (Extractor -> AI Classifier -> Human Review, see
blueprint-v1.0.md's Import Pipeline section) into the canonical Markdown, and then re-running this
script. Re-run it any time after the database changes to refresh the page.

There's no standalone "master vocabulary table" section — per teacher
feedback (2026-08-03) it duplicated the per-story/per-culture-item
vocabulary tables inside the Content and Culture cards and made the page
too long. Search still finds any vocabulary word: each card's own word list
is folded into that card's `data-search` key, so searching a word surfaces
the story/culture item that teaches it (with full context), not an
isolated row. A compact search box also lives in the sticky nav bar so it
stays reachable while scrolled down, in sync with the hero search box.

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
opens with an explicit disclaimer. Assessment entries never show their
`administered` date (2026-08-05: teacher explicitly asked for all specific
calendar dates off the page, portfolio-vs-student-facing is a separate
question from date-drift) — same trap, same fix as everywhere else here.

Usage: python3 student_reference.py <unit_dir> <output_html_path>
"""
import os
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

# Cross-references between Content Layer files (e.g. "[...](../06-assessment/
# diagnostic-test.md)") make sense in the source Markdown, where they're real,
# clickable GitHub links. They are NOT real links in this page's output: it's
# a single static HTML file, so a relative path into the git repo's .md
# source resolves to nothing wherever this page is actually opened from. Since
# populate_link_targets() below, we know which of those files ended up as a
# card *on this same page* (every card gets an `id="item-<stem>"`) — for
# those, rewrite the link into a working same-page anchor. For anything else
# (e.g. a Resources file this page never renders), drop the link and keep
# just the text, rather than leave a link that always dead-ends.
_LINK_TARGETS = {}


def populate_link_targets(*entry_groups):
    for entries in entry_groups:
        for _, _, stem in entries:
            _LINK_TARGETS[stem] = f"item-{stem}"


def inline_md(text):
    """Minimal inline Markdown -> HTML: links, bold, code. Escapes first,
    so this is safe against raw HTML in source files."""
    text = esc(text)

    def link(m):
        label, href = m.group(1), m.group(2)
        if href.endswith(".md"):
            stem = os.path.splitext(os.path.basename(href))[0]
            anchor = _LINK_TARGETS.get(stem)
            return f'<a href="#{anchor}">{label}</a>' if anchor else label
        return f'<a href="{href}" target="_blank" rel="noopener">{label}</a>'

    text = _LINK.sub(link, text)
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
    Extensions / Teacher Notes) actually contain, plus the free-form section
    prose that assessment files use (see render_markdown_body). Numbered
    lines (e.g. assessment questions) are deliberately left as plain
    paragraphs rather than parsed into an `<ol>`: some source files write a
    real one-item-per-line list, others cram several "N. ..." items onto one
    line as flowing enumeration (e.g. "1. 昨天　2. 姐姐　3. 中国..." in
    diagnostic-test.md) — a single numbered-line heuristic can't tell those
    apart without mangling one of them, so both just render as text, intact.
    Groups run by *line kind* (list / quote / paragraph) rather than by
    blank-line-separated blocks, since source files often put a lead-in
    sentence directly above a bullet list with no blank line between them."""
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


def render_markdown_body(body):
    """Render a whole body's worth of '## heading' sections generically —
    used where, unlike Content/Culture cards, there's no fixed known set of
    sub-headings to look up by name (each assessment file's sections vary:
    Listening/Reading/Writing/Speaking, or 词/句子/说一说, etc.). Drops the
    leading '# Title' line (the card's own <h2> bar already carries the
    title) and renders every '## heading' found, in source order, plus any
    preamble text before the first one."""
    text = re.sub(r"^\s*#\s+.*\n", "", body, count=1)
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    out = []
    preamble = render_blocks(parts[0])
    if preamble:
        out.append(preamble)
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        content = parts[i + 1] if i + 1 < len(parts) else ""
        out.append(f"<h4>{esc(heading)}</h4>{render_blocks(content)}")
    return "\n".join(out)


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
    if "quiz" in t:
        return "随堂测验 Quiz", "teal", False
    return esc(assessment_type), "plum", False


def pill(label, color):
    return f'<span class="pill pill-{color}">{esc(label)}</span>'


def status_pill(status):
    return "" if status in ("canonical", "draft") else pill("编写中 In Progress", "muted")


def content_card(fm, body, stem, type_map, type_key, extra_sections=()):
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
    # Fold this item's own vocabulary into its search key (there's no
    # standalone vocab table anymore — see 08-curriculum-intelligence.md,
    # so searching a word needs to surface the story/culture card that
    # teaches it, with full context, rather than an isolated row).
    vocab_terms = " ".join(f"{r['zh']} {r['py']} {r['en']}" for r in own_vocab)
    search_key = esc(f"{fm.get('title')} {fm.get('english')} {fm.get('pinyin')} {label} {vocab_terms}".lower())
    extra_html = "".join(
        f"<h4>{esc(h)}</h4>{section_html(body, key)}" for h, key in extra_sections
    )
    return f"""
    <article class="card" id="item-{esc(stem)}" data-type="{esc(fm.get(type_key))}" data-search="{search_key}">
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


def student_work_card(fm, body, stem):
    """Deliberately has no student-name field anywhere in its schema — not
    just "don't fill it in," there's structurally nowhere to put one, so a
    future entry can't leak a name by accident. Teacher confirmed (2026-08-04)
    these are past students' work with identifying info already stripped
    before upload, no photos; this function still shouldn't grow a name
    field even so, since the point is the work is the artifact, not who
    made it."""
    search_key = esc(f"{fm.get('title')} {fm.get('medium')}".lower())
    return f"""
    <article class="card" id="item-{esc(stem)}" data-search="{search_key}">
      <div class="bar"><span class="zh">{esc(fm.get('title'))}</span></div>
      <div class="card-body">
        <div class="badges">{pill(esc(fm.get('medium') or 'Student Work'), 'jade')}{status_pill(fm.get('status'))}</div>
        {f"<p class='pinyin'>{esc(fm.get('responds_to'))}</p>" if fm.get('responds_to') else ""}
        <h4>说明 Description</h4>
        {section_html(body, "Description")}
        <h4>亮点 Highlights</h4>
        {section_html(body, "Highlights")}
      </div>
    </article>"""


def slides_embed_html(embed_url):
    """A Cycle's real classroom deck, embedded — the deck itself is now the
    detail; this page only needs to orient a visitor, not restate it. Needs
    the deck's Google Slides "Publish to web" embed URL (Slides docstring:
    File > Share > Publish to web), not a plain sharing link — those don't
    embed. No URL yet -> a quiet placeholder, not a missing-content warning,
    since not every Cycle will have one immediately."""
    if not embed_url:
        return ('<div class="slides-placeholder">Slides preview coming soon '
                '· 课堂 Slides 预览待补</div>')
    return (f'<div class="slides-embed"><iframe src="{esc(embed_url)}" '
            f'loading="lazy" allowfullscreen></iframe></div>')


def cycle_card(fm, body):
    """One short overview paragraph plus the real classroom Slides embedded
    below it, not a day-by-day log. Per teacher feedback (2026-08-04, third
    round): even the trimmed Do-Now/Objective/Main-Activities-per-lesson
    format still read as too long, and since the actual deck is now
    embedded directly (see slides_embed_html), restating its contents in
    prose is redundant — the summary's only job is to orient a visitor
    before they look at the deck."""
    overview = body_section(body, "Overview")
    return f"""
    <article class="card">
      <div class="bar"><span class="zh">{esc(fm.get('cycle'))}</span></div>
      <div class="card-body">
        {render_blocks(overview)}
        {slides_embed_html(fm.get('slides_embed_url'))}
      </div>
    </article>"""


def assessment_card(fm, body, stem):
    """Full test content, not just a Schoology pointer — this page is a
    personal curriculum-design portfolio (2026-08-04 repositioning), not a
    student-facing tool, so there's no one left to accidentally hand an
    answer key to. Teacher confirmed (2026-08-05) real Diagnostic/Quiz/
    Summative content can render directly; PROJECT_STATUS.md 2026-08-04 note
    calling this out as "quiz content never rendered" is now stale.
    Deliberately never renders `administered` (or any other specific
    calendar date) — same date-drift reasoning as everywhere else on this
    page (see module docstring): a school-year-specific date is stale the
    moment a new cohort starts, so it's kept in the Content Layer as source
    metadata only, never displayed."""
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
        <article class="card" id="item-{esc(stem)}" data-search="{search_key}">
          <div class="bar"><span class="zh">{esc(fm.get('title'))}</span></div>
          <div class="card-body">
            <div class="badges">{pill(label, color)}{status_pill(fm.get('status'))}</div>
            {sections}
          </div>
        </article>"""
    return f"""
    <article class="card" id="item-{esc(stem)}" data-search="{search_key}">
      <div class="bar"><span class="zh">{esc(fm.get('title'))}</span></div>
      <div class="card-body">
        <div class="badges">{pill(label, color)}{status_pill(fm.get('status'))}</div>
        {render_markdown_body(body)}
      </div>
    </article>"""


# Per-unit accent rotation (Blueprint Layer 3 styling concern, not Content
# Layer data): analogous Morandi tones so units read as one family, not a
# rainbow. Each pair is (fill, ink-on-fill) — most fills are light enough for
# dark ink text; the two darker ones (陈酒红/暮光绿) get cream text instead.
UNIT_HERO_COLORS = [
    ("#E38C7A", "#2E2924"),  # 伯爵橙
    ("#A77979", "#F8F1E0"),  # 陈酒红
    ("#9C9E89", "#F8F1E0"),  # 暮光绿
    ("#99A4BC", "#2E2924"),  # 梦幻蓝
    ("#B3B3A3", "#2E2924"),  # 青城灰
]


def render(unit_dir, course_title="Mandarin 1.2", hero=UNIT_HERO_COLORS[0]):
    overview_fm, overview_body = load_frontmatter(f"{unit_dir}/01-overview.md")
    objectives = bullet_list(body_section(overview_body, "Learning Objectives"))
    objectives_en = bullet_list(body_section(overview_body, "Learning Objectives (English)"))
    language_forms = overview_fm.get("language_forms") or []

    def entries(dir_glob):
        out = []
        for path in sorted(glob.glob(dir_glob)):
            if path.endswith("README.md"):
                continue
            fm, body = load_frontmatter(path)
            stem = os.path.splitext(os.path.basename(path))[0]
            out.append((fm, body, stem))
        return out

    content_entries = entries(f"{unit_dir}/03-content/*.md")
    culture_entries = entries(f"{unit_dir}/04-culture/*.md")
    assessment_entries = entries(f"{unit_dir}/06-assessment/*.md")
    cycle_entries = entries(f"{unit_dir}/02-teaching/cycle-*.md")
    student_work_entries = entries(f"{unit_dir}/09-student-work/*.md")

    # Populate before rendering any card, so links in Teaching Flow (rendered
    # last) can resolve to cards that appear earlier on the page too.
    populate_link_targets(content_entries, culture_entries, assessment_entries)

    content_html = "\n".join(content_card(fm, body, stem, CONTENT_TYPE, "content_type") for fm, body, stem in content_entries)
    culture_html = "\n".join(content_card(fm, body, stem, CULTURE_TYPE, "culture_type") for fm, body, stem in culture_entries)
    cycle_html = "\n".join(cycle_card(fm, body) for fm, body, _ in cycle_entries)
    assessment_html = "\n".join(assessment_card(fm, body, stem) for fm, body, stem in assessment_entries)
    student_work_html = (
        "\n".join(student_work_card(fm, body, stem) for fm, body, stem in student_work_entries)
        or '<p class="pending">内容整理中 · Student work coming soon</p>'
    )

    objectives_html = "\n".join(
        f"<li><span class='zh'>{esc(zh)}</span>" + (f"<span class='en'>{esc(en)}</span>" if en else "") + "</li>"
        for zh, en in zip(objectives, objectives_en + [""] * len(objectives))
    )
    grammar_html = "\n".join(f"<li>{esc(g)}</li>" for g in language_forms)

    today = datetime.date.today().isoformat()

    return TEMPLATE.format(
        bar=hero[0],
        bar_ink=hero[1],
        course=esc(course_title),
        unit_label=esc(overview_fm.get("unit")),
        big_idea_zh=esc((overview_fm.get("big_idea") or "").split("(")[0].strip()),
        big_idea_en=esc(overview_fm.get("big_idea", "").split("(", 1)[-1].rstrip(")")),
        objectives_html=objectives_html,
        grammar_html=grammar_html,
        content_html=content_html,
        culture_html=culture_html,
        cycle_html=cycle_html,
        assessment_html=assessment_html,
        student_work_html=student_work_html,
        generated_date=today,
    )


TEMPLATE = """<title>{course} · {unit_label} Curriculum Archive 课程归档</title>
<style>
:root {{
  /* Morandi palette (teacher-specified) — bg/surface/ink/muted/line shift between
     light/dark below; --bar (per-unit accent) and the pill fills stay the same
     pastel Morandi hex in both themes on purpose, since a light swatch with dark
     ink text reads fine as a self-contained chip regardless of the page around it. */
  --bg: #F8F1E0; --surface: #FCF9F3; --ink: #2E2924; --muted: #8C8272; --line: #2E2924;
  --bar: {bar}; --bar-ink: {bar_ink};
  --c-plum: #DCCFCB; --c-jade: #BCCBB2; --c-gold: #F1E1D0; --c-vermilion: #E2CECE; --c-teal: #BCC2D4; --c-muted: #D8D6D9;
  --pill-ink: #2E2924;
  --font-latin: -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  --font-kai: "Kaiti SC", "STKaiti", "KaiTi", "AR PL KaitiM GB", "BiauKai", serif;
  --font-mono: ui-monospace, "SFMono-Regular", "Liberation Mono", monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg: #201B17; --surface: #2B2521; --ink: #ECE4D8; --muted: #C7BCA8; --line: #ECE4D8; }}
}}
:root[data-theme="dark"] {{ --bg: #201B17; --surface: #2B2521; --ink: #ECE4D8; --muted: #C7BCA8; --line: #ECE4D8; }}
:root[data-theme="light"] {{ --bg: #F8F1E0; --surface: #FCF9F3; --ink: #2E2924; --muted: #8C8272; --line: #2E2924; }}
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
nav.jump {{
  position: sticky; top: 0; z-index: 10;
  display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem;
  margin: 0 -1.4rem 1.6rem; padding: 0.7rem 1.4rem;
  background: var(--bg); border-bottom: 2px solid var(--line);
}}
nav.jump a {{
  font-family: var(--font-latin); font-size: 0.82rem; font-weight: 700; text-decoration: none; color: var(--ink);
  border: 1.5px solid var(--line); border-radius: 999px; padding: 0.3rem 0.85rem; white-space: nowrap;
}}
#search-sticky {{
  flex: 1 1 160px; min-width: 120px; padding: 0.4rem 0.8rem; border-radius: 999px; border: 1.5px solid var(--line);
  font-size: 0.85rem; font-family: var(--font-latin), var(--font-kai); background: var(--surface); color: var(--ink);
}}
section {{ margin-bottom: 2rem; }}
section > h2 {{ font-size: 1.3rem; margin: 0 0 0.9rem; display: flex; align-items: baseline; gap: 0.5rem; }}
section > h2 .en {{ font-family: var(--font-latin); font-weight: 700; font-size: 0.65em; color: var(--muted); }}
.section-note {{ font-family: var(--font-latin); color: var(--muted); font-size: 0.82rem; margin: -0.4rem 0 1rem; }}
.card {{ background: var(--surface); border: 2px solid var(--line); border-radius: 10px; margin-bottom: 1.1rem; overflow: hidden; }}
.card .bar {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.5rem; padding: 0.65rem 1.1rem; background: var(--bar); color: var(--bar-ink); font-weight: 800; font-size: 1.15rem; }}
.card .bar .en {{ font-family: var(--font-latin); font-weight: 700; font-size: 0.68em; opacity: 0.92; color: var(--bar-ink); }}
.card-body {{ padding: 1.1rem 1.3rem 1.3rem; }}
.card-body h4 {{ font-family: var(--font-latin); text-transform: uppercase; letter-spacing: 0.04em; font-size: 0.78rem; color: var(--muted); margin: 1.1rem 0 0.4rem; }}
.card-body h4:first-of-type {{ margin-top: 0.2rem; }}
.badges {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.3rem; }}
.pinyin {{ font-family: var(--font-latin); color: var(--muted); font-size: 0.88rem; margin: 0.2rem 0 0.6rem; }}
.pill {{ font-family: var(--font-mono), var(--font-kai); font-size: 0.68rem; letter-spacing: 0.02em; border-radius: 4px; padding: 0.2rem 0.55rem; white-space: nowrap; color: var(--pill-ink); font-weight: 700; }}
.pill-plum {{ background: var(--c-plum); }} .pill-jade {{ background: var(--c-jade); }} .pill-gold {{ background: var(--c-gold); }}
.pill-vermilion {{ background: var(--c-vermilion); }} .pill-teal {{ background: var(--c-teal); }} .pill-muted {{ background: var(--c-muted); }}
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
.slides-embed {{ position: relative; width: 100%; padding-top: 56.25%; margin-top: 0.9rem; border-radius: 8px; overflow: hidden; border: 2px solid var(--line); background: var(--surface); }}
.slides-embed iframe {{ position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }}
.slides-placeholder {{
  margin-top: 0.9rem; padding: 1.6rem 1rem; border: 1.5px dashed var(--muted); border-radius: 8px;
  text-align: center; color: var(--muted); font-family: var(--font-latin); font-size: 0.85rem;
}}
ol.objectives {{ margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 0.5rem; }}
ol.objectives li {{ font-size: 0.98rem; }}
ol.objectives .en {{ display: block; font-family: var(--font-latin); color: var(--muted); font-size: 0.8em; margin-top: 0.1rem; }}
ul.grammar {{ margin: 0; padding-left: 1.2rem; font-family: var(--font-latin); font-size: 0.92rem; }}
footer {{ font-family: var(--font-latin); color: var(--muted); font-size: 0.78rem; text-align: center; margin-top: 2.5rem; }}
[data-search].is-hidden {{ display: none !important; }}
</style>

<div class="page">
  <div class="hero" id="top">
    <div class="eyebrow">{course} · {unit_label} · Curriculum Archive 课程归档</div>
    <h1>{big_idea_zh}</h1>
    <p class="en-title">{big_idea_en}</p>
    <p class="subtitle">A searchable reference for this unit — vocabulary, story text, the real Cycle-by-cycle
      flow, and assessment info.</p>
    <div class="search-wrap">
      <input id="search" type="text" placeholder="搜索生词、故事、Cycle… Search vocabulary, stories, cycles…" autocomplete="off">
      <p class="search-hint">Searches vocabulary (中文/拼音/English), stories, and culture content on this page.</p>
    </div>
  </div>

  <nav class="jump">
    <input id="search-sticky" type="text" placeholder="搜索… Search…" autocomplete="off">
    <a href="#top">↑ 顶部 Top</a>
    <a href="#content">学习内容 Content</a>
    <a href="#culture">文化 Culture</a>
    <a href="#teaching-flow">课堂进度 Teaching Flow</a>
    <a href="#assessments">单元考核 Assessments</a>
    <a href="#student-work">学生作品 Student Work</a>
  </nav>

  <section id="objectives">
    <h2>学习目标 <span class="en">Learning Objectives</span></h2>
    <div class="card"><div class="card-body">
      <ol class="objectives">{objectives_html}</ol>
      <h4 style="font-family: var(--font-latin); text-transform: uppercase; letter-spacing: 0.04em; font-size: 0.78rem; color: var(--muted); margin: 1.2rem 0 0.4rem;">语法 / 语言形式 Grammar &amp; Language Forms</h4>
      <ul class="grammar">{grammar_html}</ul>
    </div></div>
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
    <p class="section-note">The general order and content of each Cycle — not a day-by-day log of exact
      dates or activities.</p>
    {cycle_html}
  </section>

  <section id="assessments">
    <h2>单元考核 <span class="en">Assessments</span></h2>
    {assessment_html}
  </section>

  <section id="student-work">
    <h2>学生作品 <span class="en">Student Work</span></h2>
    <p class="section-note">Past students' project work, shared with identifying information
      removed — no names, no photos.</p>
    {student_work_html}
  </section>

  <footer>Generated from the curriculum database · {generated_date} · re-run the generator after the database
    is updated to refresh this page</footer>
</div>

<script>
(function() {{
  var mainInput = document.getElementById('search');
  var stickyInput = document.getElementById('search-sticky');
  var searchables = Array.prototype.slice.call(document.querySelectorAll('[data-search]'));
  function applyFilter(q) {{
    q = q.trim().toLowerCase();
    searchables.forEach(function(el) {{
      var match = !q || (el.getAttribute('data-search') || '').indexOf(q) !== -1;
      el.classList.toggle('is-hidden', !match);
    }});
  }}
  function sync(source, other) {{
    return function() {{
      other.value = source.value;
      applyFilter(source.value);
    }};
  }}
  mainInput.addEventListener('input', sync(mainInput, stickyInput));
  stickyInput.addEventListener('input', sync(stickyInput, mainInput));
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
