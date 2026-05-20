function bindFlip(root) {
    root.querySelectorAll('.flip-card').forEach((card) => {
        if (card.dataset.bound === '1') return;
        card.dataset.bound = '1';
        card.addEventListener('click', () => card.classList.toggle('is-flipped'));
    });
}

document.addEventListener('DOMContentLoaded', () => bindFlip(document));
document.body.addEventListener('htmx:afterSwap', (evt) => bindFlip(evt.target));
