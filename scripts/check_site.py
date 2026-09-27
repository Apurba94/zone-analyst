"""
Check the website before it ships: links, anchors, assets, external hosts.

    python scripts/check_site.py

Standard library only. Exits non-zero on any problem, so CI and the deploy
workflow stop before a broken page reaches the server.
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

SITE = Path(__file__).resolve().parents[1] / "website"
ALLOWED_HOSTS = {"fonts.googleapis.com", "fonts.gstatic.com"}
MARKERS = ("<!-- sz:head -->", "<!-- sz:nav -->", "<!-- sz:foot -->")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.refs: list[tuple[str, str]] = []  # (attribute, value)
        self.base: str | None = None
        self.has_title = False
        self.has_desc = False
        self.lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "base":
            self.base = a.get("href")
        if tag == "title":
            self.has_title = True
        if tag == "meta" and a.get("name") == "description" and a.get("content"):
            self.has_desc = True
        for attr in ("href", "src"):
            if a.get(attr):
                self.refs.append((attr, a[attr]))


def parse(path: Path) -> Page:
    p = Page()
    p.feed(path.read_text(encoding="utf-8"))
    return p


def main() -> int:
    pages = {p.name: parse(p) for p in sorted(SITE.glob("*.html"))}
    problems: list[str] = []

    for name, page in pages.items():
        html = (SITE / name).read_text(encoding="utf-8")
        for m in MARKERS:
            if m not in html:
                problems.append(f"{name}: missing shared chrome ({m}); run scripts/site_chrome.py")
        if not page.has_title:
            problems.append(f"{name}: no <title>")
        if not page.has_desc:
            problems.append(f"{name}: no meta description")
        if not page.lang:
            problems.append(f"{name}: <html> has no lang attribute")

        for attr, ref in page.refs:
            if ref.startswith(("mailto:", "tel:", "data:", "javascript:")):
                continue
            parts = urlsplit(ref)
            if parts.scheme in ("http", "https"):
                if parts.hostname not in ALLOWED_HOSTS:
                    problems.append(f"{name}: external {attr} to {parts.hostname} ({ref})")
                continue
            if ref.startswith("/") and page.base is None:
                problems.append(f"{name}: root-relative {ref} breaks double-click and subfolder use")
                continue
            target_name = parts.path.lstrip("/") or name
            target = SITE / target_name
            if parts.path and not target.exists():
                problems.append(f"{name}: {attr}={ref} points to a missing file")
                continue
            if parts.fragment:
                tpage = pages.get(Path(target_name).name)
                if tpage is None:
                    continue
                if parts.fragment not in tpage.ids:
                    problems.append(f"{name}: #{parts.fragment} not found in {target_name}")

    # every page reachable from the nav, every nav target present
    home = (SITE / "index.html").read_text(encoding="utf-8")
    nav = re.search(r'<ul class="sz-links">(.*?)</ul>', home, re.S)
    if nav:
        for href in re.findall(r'href="([^"#]+)"', nav.group(1)):
            if not (SITE / href).exists():
                problems.append(f"nav links to missing page {href}")

    for extra in (".htaccess", "robots.txt", "assets/site.css", "assets/favicon.svg",
                  "assets/combat-model.js", "downloads/pubgm-combat-math.xlsx"):
        if not (SITE / extra).exists():
            problems.append(f"missing {extra}")

    print(f"checked {len(pages)} pages")
    for p in problems:
        print("  PROBLEM:", p)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
