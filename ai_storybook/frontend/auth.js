/**
 * auth.js — Shared authentication & navigation logic for StoryMagic AI
 */

document.addEventListener('DOMContentLoaded', () => {
    updateNavigation();
});

/**
 * Updates the navigation bar based on the current login state
 */
function updateNavigation() {
    const authContainer = document.querySelector('.nav-pill-auth');
    if (!authContainer) return;

    const currentUser = JSON.parse(localStorage.getItem('currentUser'));

    if (currentUser) {
        // User is logged in — show profile avatar and name
        authContainer.innerHTML = `
            <a href="profile.html" class="nav-profile-link jelly-hover">
                <img src="${currentUser.avatar || 'images/Rosie.webp'}" alt="Profile" class="nav-avatar-img">
                <span class="nav-profile-name">${currentUser.name || 'Little Explorer'}</span>
            </a>
        `;
    } else {
        // User is logged out — show login/signup buttons
        authContainer.innerHTML = `
            <a href="login.html" class="nav-btn login jelly-hover">Login</a>
            <a href="signup.html" class="nav-btn signup jelly-hover">Sign Up</a>
        `;
    }
}

/**
 * Simulated Login for demo purposes
 */
function mockLogin(email, name = 'Little Explorer') {
    const userData = {
        email: email || 'guest@example.com',
        name: name,
        avatar: 'images/Rosie.webp', // Default avatar
        joined: new Date().toLocaleDateString()
    };
    localStorage.setItem('currentUser', JSON.stringify(userData));
    window.location.href = 'index.html';
}

/**
 * Logout
 */
function logout() {
    localStorage.removeItem('currentUser');
    window.location.href = 'index.html';
}
