const state = {
    cards: [],
    deckBySlug: {},
    query: "",
    activeTag: null,
};

const els = {
    search: document.getElementById("search"),
    grid: document.getElementById("grid"),
    empty: document.getElementById("empty"),
    count: document.getElementById("count"),
    tagBar: document.getElementById("tag-bar"),
    tmpl: document.getElementById("card-tmpl"),
};

async function load() {
    const res = await fetch("./cards.json", { cache: "no-cache" });
    if (!res.ok) throw new Error(`failed to load cards.json: ${res.status}`);
    const data = await res.json();
    state.cards = data.cards || [];
    state.deckBySlug = Object.fromEntries((data.decks || []).map((d) => [d.slug, d]));
    renderTagBar();
    render();
}

function allTags() {
    const seen = new Set();
    for (const c of state.cards) for (const t of c.tags || []) seen.add(t);
    return [...seen].sort();
}

function renderTagBar() {
    els.tagBar.innerHTML = "";
    const tags = allTags();
    const all = document.createElement("button");
    all.className = "tag-chip" + (state.activeTag == null ? " is-active" : "");
    all.textContent = `all (${state.cards.length})`;
    all.addEventListener("click", () => {
        state.activeTag = null;
        renderTagBar();
        render();
    });
    els.tagBar.appendChild(all);
    for (const tag of tags) {
        const btn = document.createElement("button");
        btn.className = "tag-chip" + (state.activeTag === tag ? " is-active" : "");
        const n = state.cards.filter((c) => (c.tags || []).includes(tag)).length;
        btn.textContent = `${tag} (${n})`;
        btn.addEventListener("click", () => {
            state.activeTag = state.activeTag === tag ? null : tag;
            renderTagBar();
            render();
        });
        els.tagBar.appendChild(btn);
    }
}

function matches(card) {
    if (state.activeTag && !(card.tags || []).includes(state.activeTag)) return false;
    if (!state.query) return true;
    const q = state.query.toLowerCase();
    return (
        card.term.toLowerCase().includes(q) ||
        card.definition.toLowerCase().includes(q) ||
        (card.tags || []).some((t) => t.toLowerCase().includes(q))
    );
}

function renderCard(card) {
    const node = els.tmpl.content.firstElementChild.cloneNode(true);
    const deckName = state.deckBySlug[card.deck]?.name || card.deck || "";
    node.querySelector("[data-deck]").textContent = deckName;
    node.querySelector("[data-term]").textContent = card.term;
    node.querySelector("[data-term-back]").textContent = card.term;
    node.querySelector("[data-definition]").textContent = card.definition;
    const src = node.querySelector("[data-source]");
    if (card.source_url) {
        src.href = card.source_url;
        src.hidden = false;
    }
    const tagBox = node.querySelector("[data-tags]");
    for (const t of card.tags || []) {
        const chip = document.createElement("span");
        chip.className = "tag-mini";
        chip.textContent = t;
        tagBox.appendChild(chip);
    }
    const flip = (e) => {
        if (e.target.closest("a")) return;
        node.classList.toggle("is-flipped");
    };
    node.addEventListener("click", flip);
    node.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            node.classList.toggle("is-flipped");
        }
    });
    return node;
}

function render() {
    const visible = state.cards.filter(matches).sort((a, b) => a.term.localeCompare(b.term));
    els.grid.innerHTML = "";
    for (const c of visible) els.grid.appendChild(renderCard(c));
    els.empty.classList.toggle("hidden", visible.length > 0);
    els.count.textContent = `${visible.length} of ${state.cards.length}`;
}

els.search.addEventListener("input", (e) => {
    state.query = e.target.value.trim();
    render();
});

load().catch((err) => {
    els.grid.innerHTML = `<div class="col-span-full text-rose-400 text-sm">Failed to load cards: ${err.message}</div>`;
    console.error(err);
});
