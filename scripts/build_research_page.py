"""
Render research/docs/REPORT.md into website/research.html.

The report is the source of truth; this page is generated from it so the two
can never drift. Re-run after editing the report:

    pip install markdown
    python scripts/build_research_page.py
    python scripts/site_chrome.py        # re-applies nav and footer

The generated page is committed, so viewing the site never needs this step.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:  # pragma: no cover
    sys.exit("This script needs the markdown package:  pip install markdown")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "research" / "docs" / "REPORT.md"
OUT = ROOT / "website" / "research.html"

# Stable anchors that other pages link to. Keyed by a phrase in the heading, so
# renumbering sections in the report does not break inbound links.
ALIASES = {
    "measurement precision ceiling": "measurement-precision",
    "how much data is needed": "data-needed",
    "guaranteed-safe disc": "guaranteed-safe",
    "confound found by running": "confound",
    "what the prior evidence actually says": "evidence",
}

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Research report</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,300;0,400;0,600;1,400&family=Archivo:wght@400;500;600&display=swap" rel="stylesheet">
<style>
.page-head{{border-bottom:2px solid var(--ink);padding-bottom:18px;margin-bottom:8px}}
.status{{margin:14px 0 0}}
.toc{{background:var(--paper-2);border:1px solid var(--rule);padding:14px 18px;margin:24px 0 8px}}
.toc h2{{font-size:13px;margin:0 0 8px}}
.toc ul{{margin:0;padding-left:0;list-style:none;columns:2;column-gap:28px;font-size:14px}}
@media (max-width:640px){{.toc ul{{columns:1}}}}
.toc li{{margin-bottom:4px;break-inside:avoid}}
.toc ul ul{{display:none}}
.toc a{{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--rule)}}
.toc a:hover{{border-bottom-color:var(--caution)}}

article.report{{font-size:15.5px;line-height:1.65}}
article.report h2{{margin:46px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--rule);scroll-margin-top:16px}}
article.report h3{{margin:28px 0 8px;scroll-margin-top:16px}}
article.report ul,article.report ol{{margin:0 0 13px;padding-left:22px}}
article.report li{{margin-bottom:6px}}
article.report code{{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.88em;
  background:var(--paper-2);border:1px solid var(--rule);padding:0 4px}}
article.report pre{{background:var(--paper-2);border:1px solid var(--rule);padding:12px 14px;
  overflow-x:auto;font-size:13.5px;line-height:1.5;margin:0 0 14px}}
article.report pre code{{background:none;border:0;padding:0;font-size:inherit}}
article.report hr{{border:0;border-top:1px solid var(--rule);margin:30px 0}}
article.report table{{margin:4px 0 16px;font-size:14px}}
article.report td,article.report th{{padding:6px 12px 6px 0}}
article.report blockquote{{margin:0 0 14px;padding:4px 0 4px 16px;border-left:3px solid var(--caution)}}
.source-note{{margin-top:40px}}
</style>
</head>
<body class="sz-page">

<main class="wrap narrow">
  <header class="page-head">
    <p class="kicker">Research report</p>
    <h1>{title}</h1>
  </header>
  <p class="note status">{status}</p>

  <nav class="toc" aria-label="Contents">
    <h2>Contents</h2>
    {toc}
  </nav>

  <article class="report">
{body}
  </article>

  <p class="small source-note">Generated from <code>research/docs/REPORT.md</code>. The power and
  precision figures were computed by the code in the repository and reproduce with
  <code>python -m bluezone.power</code>.</p>
</main>

</body>
</html>
"""


def _capitalise(s: str) -> str:
    return s[:1].upper() + s[1:]


def main() -> int:
    text = SRC.read_text(encoding="utf-8")

    # Title comes from the first H1; the "Status:" paragraph becomes a callout.
    m = re.match(r"#\s+(.+?)\n+(Status:.+?)\n\n", text, flags=re.S)
    if not m:
        sys.exit("REPORT.md must start with '# Title' followed by a 'Status:' paragraph")
    title, status = m.group(1).strip(), " ".join(m.group(2).split())
    text = text[m.end():]

    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", "toc"],
        extension_configs={"toc": {"toc_depth": "2-3", "permalink": False}},
    )
    body = md.convert(text)

    # Wide tables scroll sideways on phones instead of breaking the layout.
    body = body.replace("<table>", '<div class="table-scroll"><table>').replace("</table>", "</table></div>")

    # Stable alias anchors, placed immediately before the matching heading.
    for phrase, alias in ALIASES.items():
        pat = re.compile(rf'(<h[23] id="[^"]+">[^<]*{re.escape(phrase)})', re.I)
        body, n = pat.subn(lambda mm: f'<span id="{alias}"></span>{mm.group(1)}', body, count=1)
        if n == 0:
            print(f"warning: no heading matched alias phrase {phrase!r}")

    page = PAGE.format(
        title=html.escape(title),
        status="<b>Status.</b> " + html.escape(_capitalise(status.replace("Status:", "").strip())),
        toc=md.toc.replace('<div class="toc">', "").replace("</div>", "").strip(),
        body=body,
    )
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(page):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
