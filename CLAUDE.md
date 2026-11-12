@AGENTS.md

# Claude Code quick reference

`AGENTS.md` (imported above) is the full guide. The invariants that matter most:

- **Verify before finishing**: `python3 scripts/build.py && python3 scripts/build.py --check && python3 scripts/check_links.py`.
- **Edit sources, not output**: posts live in `content/writing/*.md`; `writing/`, `feed.xml` and `sitemap.xml` are generated. Keep the `posts` and `posts-compact` markers in `index.html`.
- **Zero dependencies**: standard-library Python only. No `package.json`, no bundler.
- **Design changes** follow the Stack rules in `AGENTS.md` and `design/stack/brand-book.md`. Tokens only, both themes, one gold accent.
- **Public-safe content**: no customer names, no internal sales figures, no em dashes.
- **Never push or merge to `master` unasked.** That publishes the live site.
