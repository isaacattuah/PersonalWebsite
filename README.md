# isaacattuah.com

Personal site of Isaac Kofi Attuah, served by GitHub Pages from the root of this
repository at [isaacattuah.com](https://isaacattuah.com).

Plain HTML, CSS and JavaScript. The writing section is compiled from Markdown by
a Python script that uses only the standard library. There is no `npm`, no
bundler and nothing to install.

## Layout

```
index.html                 v3 home page (hand-written; the build fills in recent posts)
404.html                   not-found page
assets/css/site.css        the whole design system: tokens first, then components
assets/js/site.js          theme toggle and footer year
assets/fonts/              self-hosted variable fonts (OFL)
images/                    portrait, social image, favicons

content/writing/*.md       posts: Markdown with a frontmatter block  <- edit these
scripts/build.py           Markdown -> writing/, feed.xml, sitemap.xml, home page post list
scripts/check_links.py     verifies every local link, asset and #anchor
scripts/templates/         HTML shells for a post and for the archive

writing/                   GENERATED. Do not edit by hand.
feed.xml, sitemap.xml      GENERATED.

design/stack/              the Stack design system: brand book, tokens, component guidelines
demos/                     frozen design explorations from the redesign, kept for learning (not indexed)
AGENTS.md, CLAUDE.md       working guide for coding agents; CLAUDE.md imports AGENTS.md
.github/workflows/         CI: build check and link check on every push
legacy/v0, v1, v2          the time machine: every earlier version, self-contained
version_zero.html          redirect stubs so old bookmarks keep working
version_one.html

CNAME                      custom domain for GitHub Pages. Do not remove.
.nojekyll                  tells Pages to serve files as they are. Do not remove.
```

## Everyday commands

```bash
python3 scripts/build.py            # compile the writing section
python3 scripts/build.py --check    # exit 1 if generated files are out of date
python3 scripts/check_links.py      # verify local links, assets and anchors
python3 scripts/check_links.py --external   # also request external URLs (needs network)
python3 -m http.server 8000         # preview at http://localhost:8000
```

## Publish a post

1. Create `content/writing/YYYY-MM-DD-some-slug.md`:

   ```markdown
   ---
   title: A clear title
   date: 2026-11-11
   summary: One or two sentences. Shown in lists, the feed and link previews.
   kind: Deep dive
   ---

   Body in Markdown.
   ```

2. Run `python3 scripts/build.py`, then `python3 scripts/check_links.py`.
3. Commit the Markdown file together with the generated files.

Optional frontmatter: `slug` (defaults to the file name without the date),
`canonical_url` and `source` for a piece that first ran elsewhere (adds a
"read the original" note and points `rel="canonical"` at it), and `draft: true`
to keep a post out of the build.

Supported Markdown: headings, paragraphs, bold, italic, inline code, links,
images, ordered and unordered lists with nesting, blockquotes, fenced code
blocks, tables and horizontal rules.

## Design

The v3 design language is called Stack: a mineral ground, deep green ink, one
gold accent, Bricolage Grotesque for headings and Source Serif 4 for prose. The
signature element is the four-layer stack on the home page. The home page also has a
TL;DR toggle in the header that swaps the page for a one-column summary; it is
linkable as `/#tldr`, and the build fills in its list of recent posts. Every colour, size
and space is a custom property at the top of `assets/css/site.css`.

The full reference is in `design/stack/`: `brand-book.md`, `tokens.json` and a guideline
per component. The same system is kept as a Claude Design system named Stack
(private): https://claude.ai/artifact/3Bna919URpWHzxihXN3TM1

`demos/` keeps the directions explored during the redesign (Stack in blue, Blueprint,
Strip, Reading Room) as frozen snapshots. `demos/README.md` says what each one was and
why Stack was chosen.

## Time machine

| Version | Year | Where | What it was |
| --- | --- | --- | --- |
| v0 | 2019 | `legacy/v0/` | Hand-written HTML with tables, plus the first CSS experiments |
| v1 | 2020 | `legacy/v1/` | Student portfolio on the Miniport template by HTML5 UP (CC BY 3.0, license kept in the folder) |
| v2 | 2025 | `legacy/v2/` | Single page with a dark mode toggle |
| v3 | 2026 | `/` | This site |

Each legacy folder carries its own CSS, scripts, fonts and images, so nothing
from the old sites leaks into the root. The only changes made to them were
fixing paths after the move, removing the retired Universal Analytics snippet,
and adding a small "archived version" bar.

## Content rules

Public pages describe work in technical terms. Internal sales figures such as
quota attainment or deal sizes do not belong anywhere in this repository.
