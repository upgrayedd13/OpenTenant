document.addEventListener("DOMContentLoaded", () => {
    const headings = [...document.querySelectorAll("main.document h2, main.document h3")]
        .filter(h => h.id);

    const tocList = document.getElementById("toc-list");

    headings.forEach(h => {
        const level = parseInt(h.tagName.substring(1), 10);

        const li = document.createElement("li");
        li.dataset.level = level;

        const a = document.createElement("a");
        a.href = `#${h.id}`;
        a.textContent = h.textContent.replace(/¶/g, "").trim();

        li.appendChild(a);
        tocList.appendChild(li);
    });

    const links = [...tocList.querySelectorAll("a")];
    const OFFSET = 120; // adjust for fixed header

    function onScroll() {
        let current = null;

        for (const heading of headings) {
            const top = heading.getBoundingClientRect().top;
            if (top - OFFSET <= 0) {
                current = heading;
            } else {
                break;
            }
        }

        if (!current) {
            return;
        }

        links.forEach(a => a.classList.remove("toc-active"));
        const active = tocList.querySelector(`a[href="#${current.id}"]`);
        if (active) active.classList.add("toc-active");
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll(); // run on load
});