const overlay = document.getElementById("overlay");
const titleEl = document.getElementById("modalTitle");
const contentEl = document.getElementById("modalContent");
const closeBtn = document.getElementById("closeModal");

let modalClosed = false;

document.addEventListener("DOMContentLoaded", async () => {
    if (modalClosed) return;

    titleEl.textContent = "Read before continuing!";
    contentEl.innerHTML = "Loading...";

    overlay.classList.add("active");

    try {
        const response = await fetch("/modal/db_edit_notice");
        if (!response.ok) {
            throw new Error("Failed to load");
        }

        contentEl.innerHTML = await response.text();
    } catch {
        contentEl.innerHTML = "<p>Error loading content.</p>";
    }
});

function closeModal() {
    overlay.classList.remove("active");
    modalClosed = true;
}

closeBtn.addEventListener("click", closeModal);

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && overlay.classList.contains("active")) {
        closeModal();
    }
});