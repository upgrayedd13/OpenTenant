const sidebar = document.querySelector(".sidebar");
    const menuLinks = document.querySelectorAll(".sidebar a");

    menuLinks.forEach(link => {
        link.addEventListener("click", () => {

            // remove active from all links
            menuLinks.forEach(l => l.classList.remove("active"));

            // add active to clicked one
            link.classList.add("active");

            // move clicked link to the top
            sidebar.prepend(link);
        });
    });