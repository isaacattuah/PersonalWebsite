# AGENTS.md

Working guide for any coding agent (Claude Code, Antigravity, Gemini CLI, Codex, Cursor) in this repository. `CLAUDE.md` imports this file, so there is one source of truth. If you change how the site works, update this file in the same change.

## What this is

`isaacattuah.com`: the personal site of Isaac Kofi Attuah, served by GitHub Pages from the repository root (custom domain via `CNAME`). Plain HTML, CSS and JavaScript. The writing section is compiled from Markdown by a Python script that uses only the standard library.

Version 3 of the site, design language "Stack", built November 2026.

## Layout

```
index.html                 home page, hand-written. The build fills two marked blocks (see Build)
404.html                   not-found page. Uses absolute paths (/assets/...) because it is served at any depth
assets/css/site.css        the whole design system: tokens first, then components
assets/js/site.js          theme toggle, TL;DR view toggle, footer year
assets/fonts/              self-hosted variable fonts (OFL). No third-party font requests
images/                    portrait-320/640.webp, og.png (1200x630 social card), favicons

content/writing/*.md       posts. EDIT THESE
scripts/build.py           compiler
scripts/check_links.py     link, asset and anchor checker
scripts/templates/         post.html and writing_index.html, with {{placeholders}}

writing/                   GENERATED. Never edit by hand
feed.xml, sitemap.xml      GENERATED

design/stack/              copy of the Stack design system (brand book, tokens.json, component guidelines)
demos/                     frozen design explorations from the redesign, kept for learning. See demos/README.md
legacy/v0, v1, v2          the time machine. Self-contained snapshots of earlier sites
version_zero.html, version_one.html   redirect stubs for old bookmarks

CNAME, .nojekyll           required by GitHub Pages. Never delete
.github/workflows/verify-site.yml     CI: build check and link check on every push and pull request
```

## Commands

```bash
python3 scripts/build.py            # compile content/writing/ into writing/, feed.xml, sitemap.xml, index.html blocks
python3 scripts/build.py --check    # exit 1 if any generated file is stale (CI runs this)
python3 scripts/build.py --drafts   # include posts marked draft: true, for local preview only
python3 scripts/check_links.py      # every local href, src, srcset, CSS url() and #anchor
python3 scripts/check_links.py --external   # also request external URLs (needs network; bot-blocking hosts are reported as SKIP)
python3 -m http.server 8000         # preview at http://localhost:8000
```

Before you call any change finished: run `build.py`, then `build.py --check`, then `check_links.py`. All three must pass.

## Build

`scripts/build.py` reads each `content/writing/YYYY-MM-DD-slug.md` and writes:

- `writing/<slug>/index.html` from `scripts/templates/post.html`
- `writing/index.html` (archive grouped by year) from `scripts/templates/writing_index.html`
- `feed.xml` (RSS 2.0 with full content) and `sitemap.xml`
- two blocks inside `index.html`, each replaced whole on every build:
  - `<!-- posts:start -->` to `<!-- posts:end -->`: the three most recent posts in the Writing section
  - `<!-- posts-compact:start -->` to `<!-- posts-compact:end -->`: the same three as a compact list in the TL;DR view

Never remove those markers. Never edit between them.

Frontmatter (simple `key: value` lines, not full YAML; a colon inside the value is fine):

| Key | Required | Meaning |
| --- | --- | --- |
| `title` | yes | Shown as the h1 and in lists |
| `date` | yes | `YYYY-MM-DD`. Sets the order |
| `summary` | yes | One or two sentences. Used in lists, the feed, meta description and link previews |
| `slug` | no | Defaults to the file name without the date prefix. Lowercase words joined by hyphens |
| `kind` | no | Short label in lists: `Deep dive` for native pieces, `Companion` for pieces that accompany something published elsewhere |
| `canonical_url` | no | URL of the original. Adds a "read the original" note and points `rel="canonical"` at it |
| `source` | no | Name of the publication that ran the original, used in that note |
| `draft` | no | `true` keeps the post out of the build |

Markdown supported: headings, paragraphs, bold, italic, inline code, links, images, ordered and unordered lists with nesting, blockquotes, fenced code, tables, horizontal rules. Raw HTML is escaped, not passed through. A post with four or more `##` headings gets a table of contents.

The templates use `{{root}}` for relative paths. Pages must work both at `https://isaacattuah.com/` and under `python3 -m http.server`, so keep asset paths relative everywhere except `404.html`.

## Design: Stack

Full reference in `design/stack/brand-book.md` and `design/stack/tokens.json`. The live source of truth is the token block at the top of `assets/css/site.css`; if you change a token there, change `design/stack/tokens.json` too. The same system is published as a Claude Design system named "Stack" in Isaac's Claude account (private to him): https://claude.ai/artifact/3Bna919URpWHzxihXN3TM1

Rules that are easy to break:

- **One bold thing.** The four-layer stack on the home page (Agents, Models, Capacity, Data, in that order) is the only large field of colour before the contact band. Do not reuse the `--layer-*` colours as card backgrounds.
- **One accent.** `--gold` is for the primary button, link underlines and the "you are here" marker. At most one gold fill in view. Never gold text on a light ground.
- **Two fonts with two jobs.** Bricolage Grotesque (`--sans`) for headings and every piece of interface. Source Serif 4 (`--serif`) for sentences. Monospace only inside code.
- **Use tokens.** No raw hex values, sizes or radii in component rules. Add a token if one is missing.
- **Both themes.** Every colour token has a light and a dark value, and the dark values appear twice: under `:root[data-theme="dark"]` and inside `@media (prefers-color-scheme: dark)`. Change both.
- **Contrast.** Text is at least 4.5:1 on its background in both themes. Control borders use `--ink-soft`, not `--line`.
- **No template chrome.** No all-caps labels above headings, no decorative badges, no arrows appended to links, no shadows, no gradients.
- **Motion.** One moment only: the stack settles on load. Everything else changes colour, nothing moves. Respect `prefers-reduced-motion`.
- **No JavaScript dependency for content.** The page must read fully with scripts off. Controls that need script (the TL;DR button) ship with `hidden` and are revealed by `site.js`.

Home page structure, in order: hero, stack, enablement ledger, selected systems, writing, background, then the contact band and footer shared by every page. The TL;DR view (`#tldr`) is a sibling of the full view inside `<main>`; `site.js` shows one and hides the other.

## Writing voice

- First person, plain verbs, sentence case headings.
- No em dashes and no spaced en dashes. Use a full stop or a colon.
- Say what a thing does before naming the tools.
- Credit collaborators by name when work was shared. The Google Cloud Blog guide "Four steps for startups to build multi-agent systems" was written by Oluwamayowa Awojuyigbe; Isaac is a credited collaborator, not the author. Never present it as his byline.

## Content rules

- **No customer names.** Use "large enterprise customers" or similar. Isaac is not cleared to name them.
- **No internal sales figures.** No quota attainment, no deal sizes. People reached, hours returned and cost removed are fine.
- Certification links are the Credly badge URLs already in `index.html`. Do not swap them for other credential hosts.
- The email address on the site is deliberate. Do not add other personal contact details.

## Guardrails

- Never delete or rename `CNAME` or `.nojekyll`.
- Never add `package.json`, a bundler, a framework or a third-party Python package.
- `legacy/v0`, `legacy/v1` and `legacy/v2` are historical. Do not restyle them or link them to v3 CSS or JS. The only allowed edits are path fixes and the small "archived version" bar.
- `demos/` is frozen. Do not keep it in sync with the home page and do not delete it.
- `robots.txt` disallows `/demos/`. Keep `noindex` on every page under `demos/`.
- Do not add analytics or any third-party script without asking.
- Do not push, merge into `master` or change the Pages setup without Isaac asking for it. Pushing `master` publishes the live site.
- `images/portrait-*.webp` and `images/og.png` were produced from Isaac's headshot. Regenerate both sizes and the social card together if the headshot changes.
