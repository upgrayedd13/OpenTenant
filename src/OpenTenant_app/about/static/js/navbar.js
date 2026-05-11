document.addEventListener("DOMContentLoaded", () => {
    const headings = document.querySelectorAll("main.document h2, main.document h3");
    const tocList = document.getElementById("toc-list");

    headings.forEach(h => {
        if (!h.id) return; // skip headings without anchors
        const level = h.tagName.toLowerCase(); // "h2", "h3", "h4"
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.href = `#${h.id}`;
        a.className = `toc-${level}`;
        // Strip the ¶ anchor link character from the text
        a.textContent = h.textContent.replace(/¶/g, "").trim();
        li.appendChild(a);
        tocList.appendChild(li);
    });

    // Highlight active section on scroll
    const links = tocList.querySelectorAll("a");
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
        if (entry.isIntersecting) {
            links.forEach(a => a.classList.remove("toc-active"));
            const active = tocList.querySelector(`a[href="#${entry.target.id}"]`);
            if (active) active.classList.add("toc-active");
        }
        });
    }, { rootMargin: "0px 0px -70% 0px" });

    headings.forEach(h => { if (h.id) observer.observe(h); });
});