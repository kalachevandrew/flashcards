# flashcards

AI-native flashcards. A tiny static site that helps you learn the vocabulary of working with LLMs — **CLI**, **MCP**, **token**, **context window**, **RAG**, **agent**, **embedding**, **fine-tuning**, and ~20 more. Click a card to flip it; search to filter live.

**Zero build step.** Plain HTML + vanilla JS + JSON data. Tailwind via CDN. The whole site is four files at the repo root.

## Layout

```
flashcards/
├── index.html              # markup + Tailwind config
├── app.js                  # fetch cards.json, render grid, search, flip
├── style.css               # flip-card animation + chip styles
├── cards.json              # the data (decks + cards array)
├── netlify.toml            # Netlify deploy config
├── .github/workflows/
│   └── pages.yml           # GitHub Pages deploy on every push to main
├── LICENSE                 # MIT
└── README.md
```

## Run locally

Any static server works. Easiest:

```bash
python -m http.server 8000
# then open http://localhost:8000
```

Or with Node:

```bash
npx serve .
```

Don't just double-click `index.html` — the `fetch("./cards.json")` call needs an HTTP origin, not `file://`.

## Add a card

Edit `cards.json`. The file has two top-level keys:

- `decks` — array of `{slug, name, description}`. Used for the deck label on each card.
- `cards` — array of `{deck, term, definition, tags, source_url?}`.

Commit and push; Netlify and GitHub Pages will rebuild within seconds.

## Deploy

### Netlify

1. Connect this repo at <https://app.netlify.com/>.
2. Build command: *(empty)*. Publish directory: `.`. The included `netlify.toml` sets this.
3. Done.

### GitHub Pages

The `.github/workflows/pages.yml` workflow publishes on every push to `main`. One-time enable:

1. **Settings → Pages → Source → GitHub Actions**.
2. Push any commit; the workflow stages `index.html`, `app.js`, `style.css`, and `cards.json` into a `_site/` directory and deploys it.

The live URL appears at `https://kalachevandrew.github.io/flashcards/`.

## Why no backend?

Earlier versions ran on FastAPI + SQLite. The whole API surface is doing exactly two things: serving the same 25 cards on every request, and accepting an admin POST gated by a header. Neither needs a server. Editing JSON + git push is a tighter loop than running a database. If real multi-user features (spaced repetition, accounts) ever come up, that's the moment to bring back a backend — not before.

## License

MIT — see [LICENSE](LICENSE).
