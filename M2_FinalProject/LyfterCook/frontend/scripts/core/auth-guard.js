// frontend/scripts/core/auth-guard.js
import { logout } from '../services/auth.js';

/**
 * Checks if a user is authenticated. If not, redirects to the login page.
 * Also sets up the logout button functionality.
 */
export function protectPage() {
    if (!localStorage.getItem('token')) {
        window.location.href = '../auth/login.html';
        return false; // Indicates that the page should stop rendering
    }

    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            logout();
            window.location.href = '../auth/login.html';
        });
    }

    return true; // Indicates that the user is authenticated
}
