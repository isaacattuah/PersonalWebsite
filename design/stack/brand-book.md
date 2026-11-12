# Stack

Stack is the design language of isaacattuah.com, the personal site of Isaac Kofi Attuah, an AI/ML Customer Engineer who works with startups at Google Cloud. It was built for the v3 redesign in November 2026 and lives in one stylesheet, `assets/css/site.css`, in the site's repository.

The site has one job: show a founder, an engineering leader or a hiring manager what Isaac is good at within one screen, then hand them his writing.

## The idea

Isaac's work spans four layers of an AI product: agents, models, capacity and data. The design takes that literally. The signature element is a four-band stack, lightest at the surface and deepest at the foundation, and every colour in the system comes out of that stack. Everything around it stays quiet.

Three rules follow from that.

1. **One bold thing.** The stack is the only large field of colour on the home page until the contact band. Do not add a second.
2. **One accent.** Gold marks the single most important action on a page, underlines links, and marks "you are here". If two gold fills are visible at once, remove one.
3. **Structure carries meaning.** A numbered list is a real sequence. A table is real tabular data. No labels above headings, no decorative badges.

## Content fundamentals

- First person, plain verbs, sentence case. "I built", "I led", not "responsible for".
- Say what a thing does before naming what it is made with. Tools come last, in the interface face.
- Numbers are specific and public-safe: people reached, hours returned, cost removed. Never quota attainment or deal sizes.
- No em dashes. Use a full stop or a colon.
- Link text names the destination: "Code on GitHub", "Read the original". No arrows appended to links.
- Credit collaborators by name when the work was shared.

## Visual foundations

**Colour.** `ground` is a cool mineral white, chosen to sit under green without turning cream. `ink` is a green so deep it reads as black next to the stack. The four `layer-*` colours step by lightness, not hue, so the stack still reads in greyscale and for colour-blind readers. Text on `layer-1` and `layer-2` is `layer-ink-light`; text on `layer-3` and `layer-4` is `layer-ink-dark`. `gold` is a fill and an underline, never body text on a light ground.

**Type.** Two families with clearly different jobs. Bricolage Grotesque sets headings and every piece of interface: navigation, buttons, dates, tool lists. Source Serif 4 sets everything meant to be read as a sentence. Headings are tight (`h1` at 0.98 leading, -0.035em) and prose is open (1.6 to 1.68). There are no all-caps labels and no monospace outside code.

**Layout.** Left aligned, in a 70rem page. Sections use a heading rail: the `h2` and one line of context sit in the left third, the content in the right two thirds. On narrow screens the rail stacks above the content. Essays use a single 43rem column.

**Shape.** Three radii. `radius-md` rounds the outer corners of the stack and of code blocks; the bands inside the stack meet flush. `radius-pill` is for things you press. Rules are 1px in `line`. There are no shadows and no gradients.

**Motion.** One moment: on load, the stack settles from the foundation up, 520ms per layer with a 110ms stagger. Hover and focus change colour only. Everything is disabled under `prefers-reduced-motion`.

**Themes.** Light is primary. Dark follows the system setting until the visitor chooses, and keeps the stack's two light bands at full value so the stack stays the brightest thing on the page.

## Accessibility

- Body text is at least 7:1 on its ground in both themes.
- The focus ring is 3px in `focus`, a blue outside the brand palette, with a 3px offset. On `layer-4` it switches to `gold`.
- Control borders (the two header toggles) use `ink-soft`, not `line`, so they reach 3:1 on the ground.
- Tap targets are at least 40px. The text floor is 14px, used for one label.
- The page works without JavaScript; the script only stores the theme choice.

## Iconography

Stack uses one icon, the half-filled circle on the theme toggle, drawn inline as SVG in `currentColor`. There is no icon set and no logo: the wordmark is the name set in Bricolage Grotesque at weight 700. If an icon is needed later, draw it at 24px with a 2px stroke to match.

## Components

Each has a live preview and guidelines in this system.

- **Stack**: the four-layer signature. Home page only.
- **Button**: primary (gold) and quiet (outlined). At most one primary per view.
- **PostRow**: a dated entry in a list of writing.
- **Ledger**: a figure and what it counts, as table rows.
- **ViewToggle**: the TL;DR switch in the header, and the one-column short version it reveals.

## Three directions not taken

The repository keeps three alternative directions in `demos/` built from the same content: Blueprint (grid paper and cobalt ink), Strip (full-width colour bands with a woven divider) and Reading Room (one serif column, writing first). They are comparisons, not part of this system.
