document.addEventListener("DOMContentLoaded", () => {
    const headings = document.querySelectorAll(
        "main.document h2, main.document h3, main.document h4"
    );

    headings.forEach(h => {
        // Skip if already processed
        if (h.querySelector(".anchor-link")) {
            return;
        }

        // Generate slug from text
        const text = h.textContent.trim();
        const slug = text
            .toLowerCase()
            .replace(/[^\w\s-]/g, "")   // remove punctuation
            .replace(/\s+/g, "-")       // spaces → hyphens
            .replace(/-+/g, "-");       // collapse dashes

        // Assign ID if missing
        if (!h.id) {
            h.id = slug;
        }

        // Create anchor link
        const a = document.createElement("a");
        a.className = "anchor-link";
        a.href = `#${h.id}`;
        a.innerHTML = "&#182;";

        h.appendChild(a);
    });
});