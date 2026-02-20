const menuLinks = document.querySelectorAll(".sidebar a");
const contentBox = document.querySelector(".content-box");
const sections = document.querySelectorAll(".content-box h2");
const slides = document.querySelectorAll(".slide");
const slidesWrapper = document.querySelector(".slides-wrapper");
const prevBtn = document.querySelector(".arrow.left");
const nextBtn = document.querySelector(".arrow.right");
const dotsContainer = document.querySelector(".dots");


// -----------------------------
// Sidebar logic (ONLY if exists)
// -----------------------------
if (contentBox) {

    function setActiveLink(sectionId) {
        menuLinks.forEach(link => link.classList.remove("active"));
        const activeLink = document.querySelector(`.sidebar a[href="#${sectionId}"]`);
        if (activeLink) activeLink.classList.add("active");
    }

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
}


// -----------------------------
// Slideshow logic (ONLY if slides exist)
// -----------------------------
if (slides.length > 0) {

    let currentSlide = 0;
    let autoSlide;

    // Create dots
    slides.forEach((_, index) => {
        const dot = document.createElement("span");
        dot.classList.add("dot");
        if (index === 0) dot.classList.add("active");

        dot.addEventListener("click", () => {
            currentSlide = index;
            updateSlide();
            resetAutoSlide();
        });

        dotsContainer.appendChild(dot);
    });

    const dots = document.querySelectorAll(".dot");

    function updateSlide() {
        slidesWrapper.style.transform = `translateX(-${currentSlide * 100}%)`;

        dots.forEach(dot => dot.classList.remove("active"));
        dots[currentSlide].classList.add("active");
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % slides.length;
        updateSlide();
    }

    function prevSlide() {
        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        updateSlide();
    }

    nextBtn.addEventListener("click", () => {
        nextSlide();
        resetAutoSlide();
    });

    prevBtn.addEventListener("click", () => {
        prevSlide();
        resetAutoSlide();
    });

    function startAutoSlide() {
        autoSlide = setInterval(nextSlide, 3000);
    }

    function resetAutoSlide() {
        clearInterval(autoSlide);
        startAutoSlide();
    }

    startAutoSlide();
}