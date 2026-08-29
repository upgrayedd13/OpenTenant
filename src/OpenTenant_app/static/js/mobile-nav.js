document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('nav');
    const dropdowns = document.querySelectorAll('.dropdown');

    if (!menuToggle || !nav) {
        return;
    }

    function isHamburgerVisible() {
        const hamburger = document.querySelector('.menu-toggle');
        if (!hamburger) return false;
        return window.getComputedStyle(hamburger).display !== 'none';
    }

    const isMobile = window.innerWidth <= 375;
    let currentHamburgerVisible = isHamburgerVisible();

    menuToggle.addEventListener('click', function() {
        const isOpen = nav.classList.toggle('active');
        menuToggle.setAttribute('aria-expanded', isOpen);
        
        if (!isOpen) {
            closeAllDropdowns();
        }
    });

    function closeAllDropdowns() {
        dropdowns.forEach(function(dropdown) {
            dropdown.classList.remove('active');
            const btn = dropdown.querySelector('.dropdown-btn');
            if (btn) {
                btn.classList.remove('active');
                btn.setAttribute('aria-expanded', 'false');
            }
            dropdown.dataset.isClickOpen = 'false';
            
            // Clear any hover timeout
            if (dropdown.dataset.hoverTimeout) {
                clearTimeout(dropdown.dataset.hoverTimeout);
            }
        });
    }

    document.addEventListener('click', function(e) {
        if (!nav.contains(e.target) && !menuToggle.contains(e.target)) {
            nav.classList.remove('active');
            menuToggle.setAttribute('aria-expanded', 'false');
            
            // Close all dropdowns
            closeAllDropdowns();
        }
    });

    dropdowns.forEach(function(dropdown) {
        const btn = dropdown.querySelector('.dropdown-btn');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (!btn || !menu) return;

        let hoverTimeout;
        dropdown.dataset.hoverTimeout = null;
        
        // Add hover handlers - check hamburger visibility on each event
        dropdown.addEventListener('mouseenter', function() {
            // Only show on hover if hamburger is NOT visible
            if (isHamburgerVisible()) {
                return;
            }
            
            // Show submenu on hover for non-active dropdowns
            const otherDropdowns = Array.from(dropdowns).filter(d => d !== dropdown);
            
            // Close any other open dropdowns first
            otherDropdowns.forEach(function(otherDropdown) {
                otherDropdown.classList.remove('active');
                const otherBtn = otherDropdown.querySelector('.dropdown-btn');
                if (otherBtn) {
                    otherBtn.classList.remove('active');
                    otherBtn.setAttribute('aria-expanded', 'false');
                }
            });
            
            // Show this dropdown on hover
            dropdown.classList.add('active');
            btn.classList.add('active');
            btn.setAttribute('aria-expanded', 'true');
            
            clearTimeout(hoverTimeout);
            dropdown.dataset.hoverTimeout = null;
        });
        
        dropdown.addEventListener('mouseleave', function(e) {
            // Don't close if hamburger is visible
            if (isHamburgerVisible()) {
                // If dropdown is marked as click-open, never close on mouseleave
                if (dropdown.dataset.isClickOpen === 'true') {
                    return;
                }
                return;
            }
            
            // Don't close if moving to another dropdown
            if (e.relatedTarget && e.relatedTarget.closest('.dropdown')) {
                return;
            }
            
            // Don't close if moving to the submenu
            if (e.relatedTarget && dropdown.querySelector('.dropdown-menu') && 
                dropdown.querySelector('.dropdown-menu').contains(e.relatedTarget)) {
                return;
            }
            
            // Only close if mouse is leaving the entire dropdown container
            if (e.relatedTarget === null || !dropdown.contains(e.relatedTarget)) {
                hoverTimeout = setTimeout(function() {
                    dropdown.classList.remove('active');
                    btn.classList.remove('active');
                    btn.setAttribute('aria-expanded', 'false');
                }, 200);
                dropdown.dataset.hoverTimeout = hoverTimeout;
            }
        });

        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Check if this dropdown is already open
            const isCurrentlyOpen = dropdown.classList.contains('active');
            
            // Close all other dropdowns
            dropdowns.forEach(function(otherDropdown) {
                if (otherDropdown !== dropdown) {
                    otherDropdown.classList.remove('active');
                    const otherBtn = otherDropdown.querySelector('.dropdown-btn');
                    if (otherBtn) {
                        otherBtn.classList.remove('active');
                        otherBtn.setAttribute('aria-expanded', 'false');
                    }
                    // Reset click-open flag for other dropdowns
                    otherDropdown.dataset.isClickOpen = 'false';
                }
            });
            
            // Toggle current dropdown
            if (isCurrentlyOpen) {
                // If open via click, close it
                if (dropdown.dataset.isClickOpen === 'true') {
                    dropdown.classList.remove('active');
                    btn.classList.remove('active');
                    btn.setAttribute('aria-expanded', 'false');
                    dropdown.dataset.isClickOpen = 'false';
                } else {
                    // If open via hover, keep it open and mark as click-open
                    dropdown.dataset.isClickOpen = 'true';
                }
            } else {
                dropdown.classList.add('active');
                btn.classList.add('active');
                btn.setAttribute('aria-expanded', 'true');
                dropdown.dataset.isClickOpen = 'true';
            }
        });

        // Close dropdown when clicking any link inside it
        menu.querySelectorAll('a').forEach(function(link) {
            link.addEventListener('click', function() {
                dropdown.classList.remove('active');
                btn.setAttribute('aria-expanded', 'false');
            });
        });
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openDropdown = document.querySelector('.dropdown.active');
            if (openDropdown) {
                openDropdown.classList.remove('active');
                const btn = openDropdown.querySelector('.dropdown-btn');
                if (btn) {
                    btn.setAttribute('aria-expanded', 'false');
                    btn.focus();
                }
                return;
            }
            
            if (nav.classList.contains('active')) {
                nav.classList.remove('active');
                menuToggle.setAttribute('aria-expanded', 'false');
                menuToggle.focus();
            }
        }
    });

    window.addEventListener('beforeunload', function() {
        nav.classList.remove('active');
        menuToggle.setAttribute('aria-expanded', 'false');
        closeAllDropdowns();
    });

    window.addEventListener('resize', function() {
        const newIsHamburgerVisible = isHamburgerVisible();
        
        // Switching from hamburger-visible to hamburger-not-visible
        if (currentHamburgerVisible && !newIsHamburgerVisible) {
            // Now hover should work
        }
        
        // Switching from hamburger-not-visible to hamburger-visible
        if (!currentHamburgerVisible && newIsHamburgerVisible) {
            nav.classList.remove('active');
            menuToggle.setAttribute('aria-expanded', 'false');
            closeAllDropdowns();
        }
        
        currentHamburgerVisible = newIsHamburgerVisible;
    });
});
