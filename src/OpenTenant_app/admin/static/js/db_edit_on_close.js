let hasUnsavedChanges = false;

// Example: mark dirty on input
// document.querySelectorAll("input, textarea").forEach(el => {
//     el.addEventListener("input", () => {
//         hasUnsavedChanges = true;
//     });
// });

window.addEventListener("beforeunload", (e) => {
    if (!hasUnsavedChanges) {
        return;
    }

    e.preventDefault();
    e.returnValue = ""; // REQUIRED
});