const menuLinks = document.querySelectorAll(".sidebar a");

    menuLinks.forEach(link => {
        link.addEventListener("click", () => {
            menuLinks.forEach(l => l.classList.remove("active"));
            link.classList.add("active");
        });
    });