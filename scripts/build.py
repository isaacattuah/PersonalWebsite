#!/usr/bin/env python3
"""Static site compiler for isaacattuah.com. Python 3 standard library only.

Reads   content/writing/*.md          (Markdown with a frontmatter block)
Writes  writing/<slug>/index.html     one page per post
        writing/index.html            the archive
        feed.xml                      RSS 2.0
        sitemap.xml
        index.html                    only the blocks between the posts markers

Usage
    python3 scripts/build.py            build everything
    python3 scripts/build.py --check    exit 1 if any generated file is stale
    python3 scripts/build.py --drafts   include posts marked `draft: true`

Frontmatter keys
    title          required
    date           required, YYYY-MM-DD
    summary        required, one or two sentences
    slug           optional, defaults to the file name without its date prefix
    canonical_url  optional, URL of the original when the piece first ran elsewhere
    source         optional, name of that publication ("Medium")
    kind           optional, short label shown in the archive ("Deep dive", "Companion")
    draft          optional, true to skip the post
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import sys
from email.utils import format_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "writing"
TEMPLATES = ROOT / "scripts" / "templates"
OUT = ROOT / "writing"

SITE_URL = "https://isaacattuah.com"
SITE_TITLE = "Isaac Attuah"
FEED_TITLE = "Isaac Attuah: Writing"
FEED_DESCRIPTION = "Notes on multi-agent systems, model selection, and getting AI into production."
AUTHOR = "Isaac Attuah"
HOME_POST_COUNT = 3
POSTS_START = "<!-- posts:start -->"
POSTS_END = "<!-- posts:end -->"
COMPACT_START = "<!-- posts-compact:start -->"  # optional second list (TL;DR view)
COMPACT_END = "<!-- posts-compact:end -->"
STATIC_PAGES = ["", "writing/"]  # sitemap entries besides the posts


# --------------------------------------------------------------------------
# Markdown
# --------------------------------------------------------------------------

def esc(text: str) -> str:
    return html.escape(text, quote=True)


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "section"


def inline(text: str) -> str:
    """Inline Markdown to HTML: code, images, links, bold, italic."""
    stash: list[str] = []

    def keep(fragment: str) -> str:
        stash.append(fragment)
        return f"\x00{len(stash) - 1}\x00"

    text = re.sub(r"`([^`]+)`", lambda m: keep(f"<code>{esc(m.group(1))}</code>"), text)
    text = esc(text)

    def image(m: re.Match) -> str:
        return keep(f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy">')

    def link(m: re.Match) -> str:
        label, url = m.group(1), m.group(2)
        external = url.startswith(("http://", "https://"))
        attrs = ' rel="noopener"' if external else ""
        return keep(f'<a href="{url}"{attrs}>') + label + keep("</a>")

    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", image, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"&lt;(https?://[^\s&]+)&gt;", lambda m: keep(f'<a href="{m.group(1)}" rel="noopener">{m.group(1)}</a>'), text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)", r"<em>\1</em>", text)
    while "\x00" in text:
        text = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)
    return text


LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^(```|~~~)\s*([\w+-]*)\s*$")
TABLE_RULE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def render_list(lines: list[str]) -> str:
    """Render a block of list lines. Nesting follows indentation."""
    out: list[str] = []
    stack: list[tuple[int, str]] = []  # (indent, tag)
    open_item = False
    for line in lines:
        m = LIST_ITEM.match(line)
        if not m:  # continuation of the previous item
            out.append(" " + inline(line.strip()))
            continue
        indent = len(m.group(1).replace("\t", "    "))
        tag = "ul" if m.group(2) in "-*+" else "ol"
        while stack and indent < stack[-1][0]:
            out.append(f"</li></{stack.pop()[1]}>")
            open_item = True
        if not stack or indent > stack[-1][0]:
            stack.append((indent, tag))
            out.append(f"<{tag}>")
        elif open_item:
            out.append("</li>")
        out.append("<li>" + inline(m.group(3)))
        open_item = True
    while stack:
        out.append(f"</li></{stack.pop()[1]}>")
    return "".join(out)


def markdown(source: str) -> tuple[str, list[tuple[int, str, str]]]:
    """Convert Markdown to HTML. Returns (html, headings) where headings is
    a list of (level, id, text) for h2 and h3."""
    lines = source.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    headings: list[tuple[int, str, str]] = []
    used_ids: set[str] = set()
    i, n = 0, len(lines)

    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        fence = FENCE.match(line)
        if fence:
            marker, lang = fence.group(1), fence.group(2)
            i += 1
            code: list[str] = []
            while i < n and not lines[i].startswith(marker):
                code.append(lines[i])
                i += 1
            i += 1
            cls = f' class="language-{esc(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>{esc(chr(10).join(code))}</code></pre>")
            continue

        heading = HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            text = inline(heading.group(2))
            if level in (2, 3):
                base = slugify(heading.group(2))
                ident, k = base, 2
                while ident in used_ids:
                    ident, k = f"{base}-{k}", k + 1
                used_ids.add(ident)
                headings.append((level, ident, re.sub(r"<[^>]+>", "", text)))
                out.append(f'<h{level} id="{ident}">{text}</h{level}>')
            else:
                out.append(f"<h{level}>{text}</h{level}>")
            i += 1
            continue

        if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        if line.lstrip().startswith(">"):
            quote: list[str] = []
            while i < n and lines[i].lstrip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append(f"<blockquote>{markdown(chr(10).join(quote))[0]}</blockquote>")
            continue

        if "|" in line and i + 1 < n and TABLE_RULE.match(lines[i + 1]):
            head = split_row(line)
            i += 2
            rows: list[list[str]] = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(split_row(lines[i]))
                i += 1
            thead = "".join(f"<th>{inline(c)}</th>" for c in head)
            tbody = "".join(
                "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>" for row in rows
            )
            out.append(
                f'<div class="table-scroll"><table><thead><tr>{thead}</tr></thead>'
                f"<tbody>{tbody}</tbody></table></div>"
            )
            continue

        if LIST_ITEM.match(line):
            block: list[str] = []
            while i < n and lines[i].strip() and (LIST_ITEM.match(lines[i]) or lines[i].startswith((" ", "\t"))):
                block.append(lines[i])
                i += 1
            out.append(render_list(block))
            continue

        para: list[str] = []
        while i < n and lines[i].strip() and not (
            FENCE.match(lines[i]) or HEADING.match(lines[i]) or LIST_ITEM.match(lines[i])
            or lines[i].lstrip().startswith(">")
        ):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")

    return "\n".join(out), headings


# --------------------------------------------------------------------------
# Posts
# --------------------------------------------------------------------------

class Post:
    def __init__(self, path: Path):
        raw = path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.S)
        if not match:
            raise SystemExit(f"{path.name}: missing frontmatter block (--- ... ---)")
        meta: dict[str, str] = {}
        for line in match.group(1).splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if ":" not in line:
                raise SystemExit(f"{path.name}: cannot read frontmatter line: {line!r}")
            key, value = line.split(":", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            meta[key.strip().lower()] = value
        for key in ("title", "date", "summary"):
            if not meta.get(key):
                raise SystemExit(f"{path.name}: frontmatter needs `{key}`")
        try:
            self.date = dt.date.fromisoformat(meta["date"])
        except ValueError:
            raise SystemExit(f"{path.name}: date must be YYYY-MM-DD, got {meta['date']!r}")
        self.path = path
        self.title = meta["title"]
        self.summary = meta["summary"]
        self.slug = meta.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", self.slug):
            raise SystemExit(f"{path.name}: slug must be lowercase words joined by hyphens, got {self.slug!r}")
        self.canonical_url = meta.get("canonical_url", "")
        self.source = meta.get("source", "")
        self.kind = meta.get("kind", "")
        self.draft = meta.get("draft", "").lower() in ("true", "yes", "1")
        self.body_md = match.group(2)
        self.body_html, self.headings = markdown(self.body_md)
        words = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", self.body_html)))
        self.minutes = max(1, round(words / 230))

    @property
    def url(self) -> str:
        return f"{SITE_URL}/writing/{self.slug}/"

    @property
    def date_long(self) -> str:
        return f"{self.date.strftime('%B')} {self.date.day}, {self.date.year}"

    @property
    def date_short(self) -> str:
        return f"{self.date.strftime('%b')} {self.date.year}"


def load_posts(include_drafts: bool) -> list[Post]:
    posts = [Post(p) for p in sorted(CONTENT.glob("*.md"))]
    if not include_drafts:
        posts = [p for p in posts if not p.draft]
    seen: dict[str, Path] = {}
    for post in posts:
        if post.slug in seen:
            raise SystemExit(f"duplicate slug {post.slug!r}: {seen[post.slug].name} and {post.path.name}")
        seen[post.slug] = post.path
    return sorted(posts, key=lambda p: (p.date, p.slug), reverse=True)


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def fill(template: str, values: dict[str, str]) -> str:
    def swap(m: re.Match) -> str:
        key = m.group(1)
        if key not in values:
            raise SystemExit(f"template uses unknown placeholder {{{{{key}}}}}")
        return values[key]
    return re.sub(r"\{\{\s*(\w+)\s*\}\}", swap, template)


def post_row(post: Post, href: str) -> str:
    kind = f'<span class="post-kind">{esc(post.kind)}</span>' if post.kind else ""
    return (
        '<li class="post-row">'
        f'<time datetime="{post.date.isoformat()}">{esc(post.date_short)}</time>'
        '<div class="post-row-body">'
        f'<h3><a href="{href}">{esc(post.title)}</a></h3>'
        f"<p>{esc(post.summary)}</p>{kind}"
        "</div></li>"
    )


def render_post(post: Post, newer: Post | None, older: Post | None, template: str) -> str:
    origin = ""
    if post.canonical_url:
        where = esc(post.source or "its original home")
        origin = (
            '<p class="post-origin">This is a companion to a piece published on '
            f'{where}. <a href="{esc(post.canonical_url)}" rel="noopener">Read the original</a>.</p>'
        )
    toc = ""
    h2s = [h for h in post.headings if h[0] == 2]
    if len(h2s) >= 4:
        items = "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for _, i, t in h2s)
        toc = f'<nav class="post-toc" aria-label="In this piece"><h2>In this piece</h2><ol>{items}</ol></nav>'
    pager = []
    if newer:
        pager.append(f'<a class="pager-newer" href="../{newer.slug}/"><span>Newer</span>{esc(newer.title)}</a>')
    if older:
        pager.append(f'<a class="pager-older" href="../{older.slug}/"><span>Older</span>{esc(older.title)}</a>')
    return fill(template, {
        "root": "../../",
        "title": esc(post.title),
        "summary": esc(post.summary),
        "canonical": esc(post.canonical_url or post.url),
        "url": esc(post.url),
        "date_iso": post.date.isoformat(),
        "date_long": esc(post.date_long),
        "minutes": str(post.minutes),
        "origin": origin,
        "toc": toc,
        "content": post.body_html,
        "pager": "".join(pager),
    })


def render_archive(posts: list[Post], template: str) -> str:
    groups: list[str] = []
    year = None
    for post in posts:
        if post.date.year != year:
            if year is not None:
                groups.append("</ul></section>")
            year = post.date.year
            groups.append(f'<section class="archive-year"><h2>{year}</h2><ul class="post-list">')
        groups.append(post_row(post, f"{post.slug}/"))
    if posts:
        groups.append("</ul></section>")
    else:
        groups.append('<p class="empty">Nothing published yet. Add a Markdown file to content/writing/ and run the build.</p>')
    return fill(template, {"root": "../", "posts": "\n".join(groups), "count": str(len(posts))})


def render_home_block(posts: list[Post]) -> str:
    rows = "\n".join("      " + post_row(p, f"writing/{p.slug}/") for p in posts[:HOME_POST_COUNT])
    return f'{POSTS_START}\n      <ul class="post-list">\n{rows}\n      </ul>\n      {POSTS_END}'


def render_compact_block(posts: list[Post]) -> str:
    rows = "\n".join(
        f'            <li><a href="writing/{p.slug}/">{esc(p.title)}</a> '
        f'<time datetime="{p.date.isoformat()}">{esc(p.date_short)}</time></li>'
        for p in posts[:HOME_POST_COUNT]
    )
    return f'{COMPACT_START}\n          <ul class="tldr-posts">\n{rows}\n          </ul>\n          {COMPACT_END}'


def render_feed(posts: list[Post]) -> str:
    def stamp(day: dt.date) -> str:
        return format_datetime(dt.datetime(day.year, day.month, day.day, 12, tzinfo=dt.timezone.utc))

    items = []
    for post in posts:
        body = post.body_html.replace("]]>", "]]]]><![CDATA[>")
        items.append(
            "  <item>\n"
            f"    <title>{esc(post.title)}</title>\n"
            f"    <link>{post.url}</link>\n"
            f'    <guid isPermaLink="true">{post.url}</guid>\n'
            f"    <pubDate>{stamp(post.date)}</pubDate>\n"
            f"    <description>{esc(post.summary)}</description>\n"
            f"    <content:encoded><![CDATA[{body}]]></content:encoded>\n"
            "  </item>"
        )
    built = f"  <lastBuildDate>{stamp(posts[0].date)}</lastBuildDate>\n" if posts else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" '
        'xmlns:content="http://purl.org/rss/1.0/modules/content/">\n<channel>\n'
        f"  <title>{esc(FEED_TITLE)}</title>\n"
        f"  <link>{SITE_URL}/writing/</link>\n"
        f"  <description>{esc(FEED_DESCRIPTION)}</description>\n"
        "  <language>en</language>\n"
        f'  <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>\n'
        f"{built}" + "\n".join(items) + "\n</channel>\n</rss>\n"
    )


def render_sitemap(posts: list[Post]) -> str:
    latest = posts[0].date.isoformat() if posts else None
    entries = []
    for page in STATIC_PAGES:
        lastmod = f"<lastmod>{latest}</lastmod>" if latest else ""
        entries.append(f"  <url><loc>{SITE_URL}/{page}</loc>{lastmod}</url>")
    for post in posts:
        entries.append(f"  <url><loc>{post.url}</loc><lastmod>{post.date.isoformat()}</lastmod></url>")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries) + "\n</urlset>\n"
    )


def plan(include_drafts: bool) -> tuple[dict[Path, str], list[Post]]:
    """Return every generated file as {path: content}."""
    posts = load_posts(include_drafts)
    post_tpl = (TEMPLATES / "post.html").read_text(encoding="utf-8")
    archive_tpl = (TEMPLATES / "writing_index.html").read_text(encoding="utf-8")
    files: dict[Path, str] = {}
    for i, post in enumerate(posts):
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i + 1 < len(posts) else None
        files[OUT / post.slug / "index.html"] = render_post(post, newer, older, post_tpl)
    files[OUT / "index.html"] = render_archive(posts, archive_tpl)
    files[ROOT / "feed.xml"] = render_feed(posts)
    files[ROOT / "sitemap.xml"] = render_sitemap(posts)

    home = ROOT / "index.html"
    current = home.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(POSTS_START) + r".*?" + re.escape(POSTS_END), re.S)
    if not pattern.search(current):
        raise SystemExit(f"index.html is missing the {POSTS_START} ... {POSTS_END} markers")
    updated = pattern.sub(lambda _: render_home_block(posts), current, count=1)
    compact = re.compile(re.escape(COMPACT_START) + r".*?" + re.escape(COMPACT_END), re.S)
    files[home] = compact.sub(lambda _: render_compact_block(posts), updated, count=1)
    return files, posts


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the writing section, feed and sitemap.")
    parser.add_argument("--check", action="store_true", help="report stale generated files and exit 1")
    parser.add_argument("--drafts", action="store_true", help="include posts marked draft: true")
    args = parser.parse_args()

    files, posts = plan(args.drafts)
    expected_dirs = {p.parent for p in files if p.parent.parent == OUT}
    orphans = sorted(d for d in OUT.glob("*/") if d.is_dir() and d not in expected_dirs) if OUT.exists() else []

    if args.check:
        stale = [p for p, text in files.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
        for path in stale:
            print(f"stale: {path.relative_to(ROOT)}")
        for path in orphans:
            print(f"orphan: {path.relative_to(ROOT)}/ has no source post")
        if stale or orphans:
            print("Run `python3 scripts/build.py` to refresh.")
            return 1
        print(f"Build is current: {len(posts)} posts, {len(files)} generated files.")
        return 0

    written = 0
    for path, text in files.items():
        if path.exists() and path.read_text(encoding="utf-8") == text:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written += 1
    for path in orphans:
        (path / "index.html").unlink(missing_ok=True)
        try:
            path.rmdir()
            print(f"removed writing/{path.name}/ (no source post)")
        except OSError:
            print(f"left writing/{path.name}/ in place: it holds files the build did not create")
    print(f"Built {len(posts)} posts. {written} of {len(files)} files changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
