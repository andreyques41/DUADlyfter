// frontend/scripts/views/dashboard.js
import { logout } from '../services/auth.js';

document.addEventListener('DOMContentLoaded', () => {
    // Basic protected route check
    if (!localStorage.getItem('token')) {
        window.location.href = '../auth/login.html';
        return; // Stop execution if not authenticated
    }

    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            logout();
            window.location.href = '../auth/login.html';
        });
    }
});
