// frontend/scripts/core/auth-guard.js
import { logout } from '../services/auth.js';
import { appState } from './state.js';

/**
 * Checks if a user is authenticated. If not, redirects to the login page.
 * Also sets up the logout button functionality.
 */
export function protectPage() {
    if (!localStorage.getItem('token')) {
        window.location.href = '../auth/login.html';
        return false; // Indicates that the page should stop rendering
    }

    // Best-effort user hydration for pages that want to show the username.
    // Not awaited to keep existing pages working.
    appState.init().catch(() => {
        // api interceptor handles redirect on 401
    });

    const logoutButton = document.getElementById('logout-button') || document.getElementById('logout-btn');
    if (logoutButton) {
        logoutButton.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }

    return true; // Indicates that the user is authenticated
}
