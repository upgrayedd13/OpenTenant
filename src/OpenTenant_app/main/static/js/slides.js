const slides = document.querySelectorAll(".slide");
const slidesWrapper = document.querySelector(".slides-wrapper");
const prevBtn = document.querySelector(".arrow.left");
const nextBtn = document.querySelector(".arrow.right");
const dotsContainer = document.querySelector(".dots");

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
