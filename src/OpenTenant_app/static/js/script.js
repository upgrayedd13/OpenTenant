const menuLinks = document.querySelectorAll(".sidebar a");
const contentBox = document.querySelector(".content-box");
const sections = document.querySelectorAll(".content-box h2");

// highlight sidebar link
function setActiveLink(sectionId) {
    menuLinks.forEach(link => link.classList.remove("active"));
    const activeLink = document.querySelector(`.sidebar a[href="#${sectionId}"]`);
    if (activeLink) activeLink.classList.add("active");
}

// scroll detection
contentBox.addEventListener("scroll", () => {
    let closestSection = null;
    let closestDistance = Infinity;

    sections.forEach(section => {
        const distance = Math.abs(section.offsetTop - contentBox.scrollTop);

        if (distance < closestDistance) {
            closestDistance = distance;
            closestSection = section;
        }
    });

    if (closestSection) setActiveLink(closestSection.id);
});

// click sidebar links
menuLinks.forEach(link => {
    link.addEventListener("click", (e) => {
        e.preventDefault();

        const targetId = link.getAttribute("href").replace("#", "");
        const targetSection = document.getElementById(targetId);

        if (targetSection) {
            const scrollPosition = targetSection.offsetTop - contentBox.offsetTop;

            contentBox.scrollTo({
                top: scrollPosition,
                behavior: "smooth"
            });

            setActiveLink(targetId);
        }
    });
});
