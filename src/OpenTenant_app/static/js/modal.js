const overlay   = document.getElementById("overlay");
const titleEl   = document.getElementById("modalTitle");
const contentEl = document.getElementById("modalContent");
const closeBtn  = document.getElementById("closeModal");

document.addEventListener("click", handleOpen);
contentEl.addEventListener("submit", handleSubmit);
closeBtn.addEventListener("click", closeModal);
document.addEventListener("keydown", handleEsc);


async function handleOpen(e) {
    const btn = e.target.closest(".openModal");
    if (!btn) {
        return;
    }

    titleEl.textContent = btn.dataset.title;
    contentEl.innerHTML = "Loading...";
    overlay.removeAttribute("hidden");
    overlay.classList.add("active");

    try {
        const res = await fetch(btn.dataset.src);

        if (!res.ok) {
            throw new Error();
        }

        contentEl.innerHTML = await res.text();
    } catch {
        contentEl.innerHTML = "<p>Error loading content.</p>";
    }
}


async function handleSubmit(e) {
    const form = e.target.closest("form");
    if (!form) {
        return;
    }

    e.preventDefault();

    try {
        const res = await fetch(form.action, {
            method: form.method || "POST",
            body: new FormData(form),
        });

        if (res.status === 422) {
            contentEl.innerHTML = await res.text();
            return;
        }

        if (res.status === 204) {
            window.location.reload();
            return;
        }

        throw new Error();
    } catch {
        contentEl.innerHTML = "<p>Error submitting form.</p>";
    }
}


function closeModal() {
    overlay.classList.remove("active");
    overlay.setAttribute("hidden", "");
}


function handleEsc(e) {
    if (e.key === "Escape" && !overlay.hasAttribute("hidden")) {
        closeModal();
    }
}