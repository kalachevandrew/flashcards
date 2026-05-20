# CLAUDE.md

## Project

**flashcards** — a static single-page web app for browsing AI-native definitions (CLI, MCP, token, RAG, agent, etc.). No backend, no build step. Four files at the repo root: `index.html`, `app.js`, `style.css`, `cards.json`. Deployed to both Netlify and GitHub Pages from the same `main` branch.

Read this before editing.

## Stack

- Plain HTML + vanilla JS (ES modules) — no bundler, no framework.
- **Tailwind CSS via the Play CDN** — `<script src="https://cdn.tailwindcss.com">`. Light theme. Custom palette defined inline in `index.html`:
  - `page` `#fafaf9` (stone-50 background)
  - `card` `#ffffff` (card face)
  - `ink` `#0f172a` (slate-900 primary text)
  - `muted` `#64748b` (slate-500 secondary text)
  - `hairline` `#e2e8f0` (slate-200 borders)
  - `accent` `#4f46e5` (indigo-600) / `accent-soft` `#eef2ff` (indigo-50, flip-back face)
- `cards.json` is the single source of truth for content. The JS loads it via `fetch("./cards.json")` at startup.
- No dependencies, no `package.json`, no `npm install`.

## Conventions

**Data shape (`cards.json`):**
```json
{
  "decks": [{ "slug": "ai-native", "name": "AI-Native Vocabulary", "description": "..." }],
  "cards": [
    {
      "deck": "ai-native",
      "term": "RAG",
      "definition": "Retrieval-Augmented Generation. …",
      "tags": ["patterns"],
      "source_url": "https://…"  // optional
    }
  ]
}
```
- `tags` is freeform but kept lowercase by convention.
- `source_url` is optional; the flip back shows a "source ↗" link only when present.

**Where things live:**
- All markup is in `index.html`. Card markup lives in a `<template id="card-tmpl">` at the bottom.
- All behaviour is in `app.js`. State is a single object (`{cards, deckBySlug, query, activeTag}`); render functions read from it.
- All custom styling is in `style.css`. The flip animation uses `transform: rotateY(180deg)` on `.flip-card.is-flipped .flip-inner`, with `backface-visibility: hidden` on each face.

**Don't:**
- Don't reach for a JS framework. 25 cards + search + flip doesn't need it.
- Don't add a build step (`vite`, `esbuild`, npm scripts). The Netlify/Pages flow assumes "publish the repo root as-is."
- Don't make `cards.json` huge. If it grows past a few hundred entries, paginate or split per deck — but the current size loads in <50ms.

## Deploy

Two parallel deploys from the same `main` branch:

- **Netlify** picks up `netlify.toml`, publishes the repo root.
- **GitHub Pages** runs `.github/workflows/pages.yml` on every push: stages the four runtime files into `_site/`, uploads as a Pages artifact, deploys via `actions/deploy-pages@v4`.

The workflow doesn't lint, build, or test — there's nothing to lint or build.

## Local dev

```bash
python -m http.server 8000
# http://localhost:8000
```

The fetch for `./cards.json` needs an HTTP origin; opening `index.html` directly via `file://` will 404 on the JSON.
