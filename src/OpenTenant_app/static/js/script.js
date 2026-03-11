const navLinks = document.querySelectorAll('nav a');

// active pages in nav bar
navLinks.forEach(link => {
    // Compare just the pathname (ignores domain)
    if (link.pathname === window.location.pathname) {
        link.classList.add('active');
    }
});
