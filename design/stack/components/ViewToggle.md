# ViewToggle

A pill button in the header that swaps the home page for a short one-column summary, for readers who want the gist.

- Label is "TL;DR" when the full page is showing and "Full page" when the summary is showing. The label names where the button takes you.
- Off: 1px `ink-soft` border on the ground. On: `ink` fill with `ground` text. It never uses `gold`, so it does not compete with the primary button.
- It is a real `button` with `aria-pressed`. It is hidden until the script runs, so a reader without JavaScript never sees a control that does nothing.
- The summary view is linkable as `/#tldr`. Following a link to a section of the full page leaves the summary first.
- The summary itself is one 40rem column: an `h1`, a `lead` paragraph, four points that each open with a bold sans label, a short list of recent writing, and a quiet button back to the full page. The contact band and footer stay.
- Home page only. Posts already open with a summary.

You provide: the lead sentence and the points. The recent writing list is filled in by the build.
