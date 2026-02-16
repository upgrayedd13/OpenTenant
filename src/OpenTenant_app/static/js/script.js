const sidebar = document.querySelector(".sidebar");
const menuLinks = document.querySelectorAll(".sidebar a");
const contentBox = document.querySelector(".content-box");
const sections = document.querySelectorAll(".content-box h2");

// function to activate a link + move it to top
function setActiveLink(sectionId) {
    menuLinks.forEach(link => link.classList.remove("active"));

    const activeLink = document.querySelector(`.sidebar a[href="#${sectionId}"]`);

    if (activeLink) {
        activeLink.classList.add("active");
        sidebar.prepend(activeLink);
    }
}

// SCROLL DETECTION (updates sidebar automatically)
contentBox.addEventListener("scroll", () => {
    let currentSection = "";

    sections.forEach(section => {
        const sectionTop = section.offsetTop;

        if (contentBox.scrollTop >= sectionTop - 60) {
            currentSection = section.id;
        }
    });

    if (currentSection) {
        setActiveLink(currentSection);
    }
});

// CLICK BEHAVIOR (jump to section + move tab to top)
menuLinks.forEach(link => {
    link.addEventListener("click", (e) => {
        e.preventDefault();

        const targetId = link.getAttribute("href").replace("#", "");
        const targetSection = document.getElementById(targetId);

        if (targetSection) {
            contentBox.scrollTo({
                top: targetSection.offsetTop,
                behavior: "smooth"
            });

            setActiveLink(targetId);
        }
    });
});
