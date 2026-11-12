# Stack

The signature element: four full-width bands that show the layers of an AI product Isaac works in, from what the user touches down to where the data lives.

- Always four layers, in this order: Agents, Models, Capacity, Data. The order is the meaning.
- Mark it up as an ordered list. Each layer has a title (`layer-title`), one sentence in `body`, and a tool list in `ui`.
- Bands meet flush. Only the outer corners take `radius-md`.
- Backgrounds are `layer-1` to `layer-4`. Text is `layer-ink-light` on the first two and `layer-ink-dark` on the last two.
- One per site, on the home page. Do not reuse the band colours as card backgrounds elsewhere.
- Below 52rem the three columns in each band stack vertically.

You provide: the sentence and the tool list for each layer.
