# PostRow

One entry in a list of writing: date, title, summary and an optional kind.

- Date in `ui` and `ink-soft`, in a fixed 6.5rem column so titles align. Below 36rem the date sits above the title.
- Title in `h3`. Its underline is hidden until hover, then `gold`.
- Summary in `body` and `ink-soft`, one or two sentences.
- Kind ("Deep dive", "Companion") in `small` with a gold dot. It tells the reader whether the piece is native or a companion to something published elsewhere, so only use it for that.
- Rows are separated by a 1px `line` rule.

You provide: date, title, summary, link, and optionally the kind. On the site these come from the post's frontmatter.
