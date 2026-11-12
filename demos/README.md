# Design explorations (frozen)

These pages are the directions explored during the v3 redesign in November 2026, kept as a learning artifact. They are snapshots: they are not updated when the home page changes, and they are excluded from search engines (`robots.txt` and `noindex`).

Open `demos/index.html` through a local server to compare them at desktop, tablet and phone widths.

| Direction | Folder | The idea | Why it was not chosen |
| --- | --- | --- | --- |
| Stack (chosen) | `/` | Mineral ground, deep green, one gold accent. The four-layer stack is the signature | Chosen: leads with the craft and is the least like every other cloud or AI site |
| Stack in blue | `stack-blue/` | The same system with the green family swapped for blue | Blue is the default colour of the field; green reads as Isaac's own |
| Blueprint | `blueprint/` | Grid paper, cobalt ink, a real architecture diagram in the hero | Strong for engineers, colder for founders and hiring managers |
| Strip | `strip/` | Full-width colour bands with a woven divider, a nod to strip-woven kente | The loudest option; leads with the person more than the work |
| Reading Room | `reading-room/` | One serif column, writing first | Survives inside Stack as the TL;DR view (`/#tldr`) |

What the comparison taught:

- All five use the same content. The differences are only in what each one puts first: craft, systems, person or writing.
- A palette swap (Stack in blue) is a few lines of tokens. A direction change is a different page.
- Fonts used only here live in `demos/fonts/`.

The design system for the chosen direction is in `design/stack/`.
