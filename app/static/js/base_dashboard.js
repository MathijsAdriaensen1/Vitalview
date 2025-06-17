document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('toggleSidebar');
    const toggleBtn = document.getElementById('darkModeToggle');
    const themeIcon = document.getElementById('theme-icon-animation');

    // Sidebar toggling
    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('close');
    });

    // Dark mode toggle
    const prefersDark = localStorage.getItem("darkMode") === "true";
    if (prefersDark) {
        document.body.classList.add("dark-mode");
        toggleBtn.textContent = "🌞";
    }

    toggleBtn.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
        const isDark = document.body.classList.contains("dark-mode");
        localStorage.setItem("darkMode", isDark);
        toggleBtn.textContent = isDark ? "🌞" : "🌙";

        const rect = toggleBtn.getBoundingClientRect();
        themeIcon.textContent = isDark ? "🌙" : "🌞";
        themeIcon.style.left = `${rect.left + rect.width / 2 - 48}px`;
        themeIcon.style.top = `${rect.top}px`;
        themeIcon.classList.add("show");

        setTimeout(() => {
            themeIcon.classList.remove("show");
        }, 2000);
    });
});
