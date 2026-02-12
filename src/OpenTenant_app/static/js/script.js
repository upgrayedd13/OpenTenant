// -----------------------------
// SIDEBAR MENU FUNCTIONALITY
// -----------------------------
const sidebar = document.querySelector(".sidebar");
const menuLinks = document.querySelectorAll(".sidebar a");

if (sidebar && menuLinks.length > 0) {
    menuLinks.forEach(link => {
        link.addEventListener("click", () => {

            // Remove active class from all links
            menuLinks.forEach(l => l.classList.remove("active"));

            // Add active class to clicked link
            link.classList.add("active");

            // Move clicked link to the top
            sidebar.prepend(link);
        });
    });
}


// -----------------------------
// NAVBAR LOGIN / ACCOUNT TAB
// -----------------------------
const loginTab = document.getElementById("loginTab");

function updateLoginTab() {
    if (!loginTab) return;

    if (localStorage.getItem("loggedIn") === "true") {
        loginTab.textContent = "Account";
        loginTab.href = "/account";
        loginTab.classList.add("account-tab");
    } else {
        loginTab.textContent = "Login";
        loginTab.href = "/login";
        loginTab.classList.remove("account-tab");
    }
}

// Run this as soon as page loads
updateLoginTab();


// -----------------------------
// LOGIN BUTTON FUNCTIONALITY
// -----------------------------
const loginBtn = document.getElementById("loginBtn");

if (loginBtn) {
    loginBtn.addEventListener("click", (event) => {
        event.preventDefault(); // prevents link from instantly going somewhere weird

        // Log user in
        localStorage.setItem("loggedIn", "true");

        // Update navbar tab immediately
        updateLoginTab();

        // Redirect to account page
        window.location.href = "/account";
    });
}


// -----------------------------
// SIGN OUT BUTTON FUNCTIONALITY
// -----------------------------
const signOutBtn = document.getElementById("signOutBtn");

if (signOutBtn) {
    signOutBtn.addEventListener("click", () => {

        // Log user out
        localStorage.removeItem("loggedIn");

        // Update navbar tab immediately
        updateLoginTab();

        // Redirect to homepage
        window.location.href = "/index";
    });
}


// -----------------------------
// HIGHLIGHT CURRENT PAGE IN NAVBAR
// -----------------------------
const navLinks = document.querySelectorAll("nav a");

navLinks.forEach(link => {
    if (link.href === window.location.href) {
        link.classList.add("active-page");
    }
});