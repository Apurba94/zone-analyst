"""
Apply the shared site chrome (head tags, navigation, footer) to every page.

The nav and footer live here, once. Each page carries them between marker
comments, so re-running this script after editing NAV or FOOT updates every
page in place and never duplicates anything:

    python scripts/site_chrome.py

Runs with the standard library only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "website"
BRAND = "Zone Analyst"

# page file -> (title, meta description, nav key)
PAGES = {
    "index.html": (
        f"{BRAND} — blue-zone and fight analytics",
        "Competitive blue-zone and fight analytics: a live zone simulator, the probability "
        "chart behind circle reads, 1v4 combat math, and a playbook for the 2026 map pool.",
        "home",
    ),
    "simulator.html": (
        f"Zone simulator · {BRAND}",
        "Watch the zone shrink phase by phase, test whether a team can outrun it, and watch "
        "a statistical battery recover the zone rule from simulated matches.",
        "simulator",
    ),
    "chart.html": (
        f"Probability chart · {BRAND}",
        "Where the next circle's centre can land, and where a team can stand and stay "
        "inside: centre density versus survival.",
        "chart",
    ),
    "combat.html": (
        f"Combat math · {BRAND}",
        "The ammunition budget of a 1v4, the armour sensitivity grid, and ranked double-gun "
        "loadouts, computed live from a sourced weapon database.",
        "combat",
    ),
    "playbook.html": (
        f"Playbook · {BRAND}",
        "Anti-rush defence, the 1v4 clutch method, and map analysis for the 2026 tournament "
        "pool: Erangel, Miramar and Rondo.",
        "playbook",
    ),
    "research.html": (
        f"Research report · {BRAND}",
        "Methodology, prior evidence and computed design results for modelling the blue "
        "zone as a grey box.",
        "research",
    ),
    "404.html": (
        f"Page not found · {BRAND}",
        "This page does not exist.",
        "",
    ),
}

LINKS = [
    ("simulator", "simulator.html", "Simulator"),
    ("chart", "chart.html", "Chart"),
    ("combat", "combat.html", "Combat math"),
    ("playbook", "playbook.html", "Playbook"),
    ("research", "research.html", "Research"),
]

BRAND_MARK = (
    '<svg viewBox="0 0 24 24" aria-hidden="true">'
    '<circle class="ring" cx="12" cy="12" r="10"/>'
    '<circle class="core" cx="12" cy="12" r="3.4"/>'
    "</svg>"
)


def head_block(description: str) -> str:
    return (
        "<!-- sz:head -->\n"
        f'<meta name="description" content="{description}">\n'
        '<meta name="color-scheme" content="light dark">\n'
        '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">\n'
        '<link rel="stylesheet" href="assets/site.css">\n'
        "<!-- /sz:head -->"
    )


def nav_block(active: str) -> str:
    items = []
    for key, href, label in LINKS:
        cur = ' aria-current="page"' if key == active else ""
        items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    home_cur = ' aria-current="page"' if active == "home" else ""
    return (
        "<!-- sz:nav -->\n"
        '<nav class="sz-nav" aria-label="Site">\n'
        '  <div class="sz-nav-in">\n'
        f'    <a class="sz-brand" href="index.html"{home_cur}>{BRAND_MARK}<span>{BRAND}</span></a>\n'
        f'    <ul class="sz-links">{"".join(items)}</ul>\n'
        "  </div>\n"
        "</nav>\n"
        "<!-- /sz:nav -->"
    )


FOOT = (
    "<!-- sz:foot -->\n"
    '<footer class="sz-foot">\n'
    '  <div class="sz-foot-in">\n'
    "    <p>Independent analysis toolkit. Not affiliated with, endorsed by, or connected to "
    "KRAFTON, Tencent or PUBG Mobile. Zone models test a candidate algorithm from a published "
    "patent; weapon figures are community estimates, graded by confidence.</p>\n"
    "    <p>© 2026 Janin A Apurba</p>\n"
    "  </div>\n"
    "</footer>\n"
    "<!-- /sz:foot -->"
)


def replace_or_insert(html: str, tag: str, block: str, anchor: re.Pattern, after: bool) -> str:
    """Replace an existing marked block, or insert one next to `anchor`."""
    marked = re.compile(rf"<!-- sz:{tag} -->.*?<!-- /sz:{tag} -->", re.S)
    if marked.search(html):
        return marked.sub(lambda _: block, html, count=1)
    m = anchor.search(html)
    if not m:
        raise ValueError(f"no anchor for {tag}")
    pos = m.end() if after else m.start()
    return html[:pos] + ("\n" if after else "") + block + ("" if after else "\n") + html[pos:]


def apply(path: Path) -> bool:
    title, desc, key = PAGES[path.name]
    html = path.read_text(encoding="utf-8")
    before = html

    html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1, flags=re.S)
    html = replace_or_insert(html, "head", head_block(desc),
                             re.compile(r'<meta name="viewport"[^>]*>'), after=True)
    html = replace_or_insert(html, "nav", nav_block(key), re.compile(r"<body[^>]*>"), after=True)
    html = replace_or_insert(html, "foot", FOOT, re.compile(r"</body>"), after=False)

    if html != before:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def main() -> int:
    missing = [n for n in PAGES if not (SITE / n).exists()]
    for name in PAGES:
        p = SITE / name
        if p.exists():
            changed = apply(p)
            print(f"{'updated' if changed else 'unchanged':9s}  {name}")
    if missing:
        print("not yet present:", ", ".join(missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
