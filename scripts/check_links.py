#!/usr/bin/env python3
"""Link checker for isaacattuah.com. Python 3 standard library only.

Walks every HTML file in the repository and verifies that each local
reference resolves: links, stylesheets, scripts, images, srcset entries,
`url(...)` inside CSS files, and `#fragment` targets. Also checks that
feed.xml and sitemap.xml only name pages that exist.

Usage
    python3 scripts/check_links.py              local references only
    python3 scripts/check_links.py --external   also request each external URL

External checks are off by default because they need the network and some
hosts (LinkedIn, Medium, Quora) refuse automated requests. Those refusals are
reported as "unverified", not as failures.
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag, urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://isaacattuah.com"
SKIP_DIRS = {".git", "node_modules", "__pycache__", "templates"}
SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")
REFUSES_BOTS = {401, 403, 405, 429, 999}


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, int]] = []
        self.ids: set[str] = set()
        self.base: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: (v or "") for k, v in attrs}
        line = self.getpos()[0]
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        if tag == "base" and a.get("href"):
            self.base = a["href"]
        for key in ("href", "src", "poster"):
            if key in a and a[key].strip():
                self.refs.append((a[key].strip(), line))
        if a.get("srcset"):
            for part in a["srcset"].split(","):
                if part.strip():
                    self.refs.append((part.strip().split()[0], line))
        if tag == "meta" and a.get("http-equiv", "").lower() == "refresh":
            m = re.search(r"url\s*=\s*['\"]?([^'\";]+)", a.get("content", ""), re.I)
            if m:
                self.refs.append((m.group(1).strip(), line))


def html_files() -> list[Path]:
    return sorted(
        p for p in ROOT.rglob("*.html")
        if not any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts)
    )


def css_files() -> list[Path]:
    return sorted(
        p for p in ROOT.rglob("*.css")
        if not any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts)
    )


def resolve(source: Path, ref: str) -> Path | None:
    """Map a local reference to a file on disk, or None if nothing is there."""
    path = unquote(urlparse(ref).path)
    target = (ROOT / path.lstrip("/")) if path.startswith("/") else (source.parent / path)
    target = target.resolve()
    if ROOT.resolve() not in target.parents and target != ROOT.resolve():
        return None
    if target.is_dir():
        target = target / "index.html"
    return target if target.is_file() else None


def check_external(url: str) -> tuple[str, str]:
    headers = {"User-Agent": "Mozilla/5.0 (link check for isaacattuah.com)"}
    for method in ("HEAD", "GET"):
        try:
            request = urllib.request.Request(url, method=method, headers=headers)
            with urllib.request.urlopen(request, timeout=15) as response:
                return "ok", str(response.status)
        except urllib.error.HTTPError as err:
            if err.code in REFUSES_BOTS:
                if method == "GET":
                    return "unverified", f"HTTP {err.code} (host refuses automated requests)"
                continue
            if method == "GET":
                return "broken", f"HTTP {err.code}"
        except Exception as err:  # DNS failure, timeout, TLS problem
            if method == "GET":
                return "unverified", f"{type(err).__name__}: {err}"
    return "unverified", "no response"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify links and assets across the site.")
    parser.add_argument("--external", action="store_true", help="also request every external URL")
    args = parser.parse_args()

    pages: dict[Path, Page] = {}
    for path in html_files():
        page = Page()
        page.feed(path.read_text(encoding="utf-8", errors="replace"))
        pages[path.resolve()] = page

    problems: list[str] = []
    external: dict[str, str] = {}
    checked = 0

    for path, page in pages.items():
        rel = path.relative_to(ROOT.resolve())
        for ref, line in page.refs:
            if ref.startswith(SKIP_SCHEMES):
                continue
            if ref.startswith("//"):
                ref = "https:" + ref
            if ref.startswith(SITE_URL):
                ref = ref[len(SITE_URL):] or "/"
            if ref.startswith(("http://", "https://")):
                external.setdefault(ref, f"{rel}:{line}")
                continue
            checked += 1
            url, fragment = urldefrag(ref)
            target = path if url == "" else resolve(path, url)
            if target is None:
                problems.append(f"{rel}:{line}  missing file: {ref}")
                continue
            if fragment and target.suffix == ".html":
                target_page = pages.get(target.resolve())
                if target_page is not None and fragment not in target_page.ids and fragment != "top":
                    problems.append(f"{rel}:{line}  missing anchor: {ref}")

    for path in css_files():
        rel = path.relative_to(ROOT)
        text = re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8", errors="replace"), flags=re.S)
        for m in re.finditer(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", text):
            ref = m.group(1).strip()
            if ref.startswith(("data:", "#")):
                continue
            if ref.startswith(("http://", "https://", "//")):
                external.setdefault(ref if not ref.startswith("//") else "https:" + ref, str(rel))
                continue
            checked += 1
            if resolve(path, ref.split("#")[0].split("?")[0]) is None:
                problems.append(f"{rel}  missing file in url(): {ref}")

    for name in ("feed.xml", "sitemap.xml"):
        xml = ROOT / name
        if not xml.exists():
            problems.append(f"{name}  file is missing; run scripts/build.py")
            continue
        for m in re.finditer(r"<(?:loc|link|guid[^>]*)>([^<]+)<", xml.read_text(encoding="utf-8")):
            url = m.group(1).strip()
            if url.startswith(SITE_URL):
                checked += 1
                if resolve(xml, url[len(SITE_URL):] or "/") is None:
                    problems.append(f"{name}  names a page that does not exist: {url}")

    for required in ("CNAME", ".nojekyll", "index.html", "404.html"):
        if not (ROOT / required).exists():
            problems.append(f"{required}  required file is missing")

    unverified: list[str] = []
    if args.external:
        for url, where in sorted(external.items()):
            status, detail = check_external(url)
            if status == "broken":
                problems.append(f"{where}  broken external link: {url} ({detail})")
            elif status == "unverified":
                unverified.append(f"{url}  {detail}")

    for line in problems:
        print("FAIL  " + line)
    for line in unverified:
        print("SKIP  " + line)
    summary = f"{len(pages)} pages, {checked} local references"
    summary += f", {len(external)} external URLs " + ("requested" if args.external else "not requested (use --external)")
    if problems:
        print(f"{len(problems)} problems. Checked {summary}.")
        return 1
    print(f"All links resolve. Checked {summary}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
