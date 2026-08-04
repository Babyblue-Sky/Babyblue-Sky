"""
Generation Layer renderer (Blueprint v1.0, Layer 3): the portfolio site shell.

Wraps student_reference.py's per-Unit HTML fragment (title/style/body/script,
no <html>/<head>/<body> of its own — that shape is deliberate, see that
file's docstring) into full HTML5 documents, plus a landing page, and writes
them to site/ for GitHub Pages to publish as a static site.

This script owns the site's *framing* (why this project exists, who it's
for) — the per-Unit content itself stays entirely owned by
student_reference.py and the Content Layer it reads from. Adding a new Unit
page later means calling render() again and adding one entry to UNITS below,
not touching the wrapper/landing page logic.

Usage:
    python3 generators/build_site.py <output_dir>
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from student_reference import render  # noqa: E402

UNITS = [
    {
        "unit_dir": "mandarin-1.2/unit-01-a-day-in-my-life",
        "slug": "mandarin-1-2-unit-01",
        "title": "Mandarin 1.2 · Unit 1 — 我的一天 (A Day in My Life)",
    },
]

PAGE_SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{extra_head}
</head>
<body>
{body}
</body>
</html>
"""


def wrap_fragment(fragment, extra_head=""):
    """student_reference.py's render() returns <title>+<style>+markup+<script>
    with no document shell (that's intentional for Claude Artifact embedding);
    a real static-hosting deploy needs a proper <!doctype html> document."""
    return PAGE_SHELL.format(extra_head=extra_head, body=fragment)


LANDING_PAGE = """<title>Tian Liao · Mandarin Curriculum Portfolio</title>
<style>
  :root {{
    --bg: #F3EFE3; --surface: #FFFFFF; --ink: #221F1A; --muted: #6E6656;
    --bar: #8A5A3B; --bar-ink: #FBF6EA; --line: #221F1A;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg: #171913; --surface: #1F2219; --ink: #EDE7DC; --muted: #A9A28F; --bar: #C08A57; --bar-ink: #2A1B10; --line: #E9E3D4; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--ink);
    font-family: -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    line-height: 1.6;
  }}
  .page {{ max-width: 760px; margin: 0 auto; padding: 3rem 1.4rem 5rem; }}
  .hero {{ border-radius: 14px; padding: 2.2rem 1.9rem; margin-bottom: 2rem; background: var(--bar); color: var(--bar-ink); }}
  .eyebrow {{ font-family: ui-monospace, monospace; text-transform: uppercase; letter-spacing: 0.14em; font-size: 0.72rem; opacity: 0.9; }}
  h1 {{ margin: 0.5rem 0 0.3rem; font-size: clamp(1.9rem, 5vw, 2.5rem); font-weight: 400; }}
  .hero p {{ margin: 0; font-size: 1rem; max-width: 56ch; opacity: 0.95; }}
  .card {{ background: var(--surface); border: 2px solid var(--line); border-radius: 10px; padding: 1.3rem 1.5rem; margin-bottom: 1.1rem; }}
  .card h2 {{ margin: 0 0 0.4rem; font-size: 1.1rem; }}
  .card p {{ margin: 0 0 0.8rem; color: var(--muted); font-size: 0.95rem; }}
  .card a.btn {{
    display: inline-block; font-weight: 700; text-decoration: none; color: var(--bar-ink);
    background: var(--bar); border-radius: 999px; padding: 0.45rem 1.1rem; font-size: 0.9rem;
  }}
  footer {{ color: var(--muted); font-size: 0.82rem; margin-top: 2.5rem; }}
</style>

<div class="page">
  <div class="hero">
    <div class="eyebrow">Curriculum Design Portfolio</div>
    <h1>Tian Liao — Mandarin Curriculum</h1>
    <p>An AI-native curriculum database for Middle School Mandarin — Markdown+YAML as the single
      source of truth for classroom Slides, assessments, and this site. Built and maintained
      unit by unit; this page indexes what's published so far.</p>
  </div>

  {unit_cards}

  <footer>Content and design decisions are version-controlled in git — see the project's
    curriculum-intelligence notes for the reasoning behind each choice.</footer>
</div>
"""

UNIT_CARD = """  <div class="card">
    <h2>{title}</h2>
    <p>Vocabulary, story texts, culture content, the real Cycle-by-cycle teaching flow, and
      assessment info for this Unit.</p>
    <a class="btn" href="{href}">Open Unit →</a>
  </div>
"""


def build(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    unit_cards = []
    for u in UNITS:
        fragment = render(u["unit_dir"])
        html = wrap_fragment(fragment)
        out_path = os.path.join(out_dir, f"{u['slug']}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"wrote {out_path}")
        unit_cards.append(UNIT_CARD.format(title=u["title"], href=f"{u['slug']}.html"))

    index_html = wrap_fragment(LANDING_PAGE.format(unit_cards="\n".join(unit_cards)))
    index_path = os.path.join(out_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"wrote {index_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out_dir")
    args = parser.parse_args()
    build(args.out_dir)
