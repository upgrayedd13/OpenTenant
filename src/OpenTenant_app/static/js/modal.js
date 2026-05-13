const overlay = document.getElementById("overlay");
const titleEl = document.getElementById("modalTitle");
const contentEl = document.getElementById("modalContent");
const closeBtn = document.getElementById("closeModal");

document.addEventListener("click", async (e) => {
    const btn = e.target.closest(".openModal");
    if (!btn) {
        return;
    }

    titleEl.textContent = btn.dataset.title;
    contentEl.innerHTML = "Loading...";

    overlay.classList.add("active");

    try {
        const response = await fetch(btn.dataset.src);
        if (!response.ok) {
            throw new Error("Failed to load");
        }

        contentEl.innerHTML = await response.text();
    } catch (err) {
        contentEl.innerHTML = "<p>Error loading content.</p>";
    }
});

closeBtn.addEventListener("click", () => {
    overlay.classList.remove("active");
});

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        overlay.classList.remove("active");
    }
});