// frontend/scripts/core/auth-guard.js
import { logout } from '../services/auth.js';
import { appState } from './state.js';
import api from '../services/api.js';

/**
 * Checks if a user is authenticated. If not, redirects to the login page.
 * Also sets up the logout button functionality.
 * 
 * Additionally, checks if the chef has completed their profile onboarding.
 * If not, redirects to the onboarding page (except when already on onboarding).
 */
export async function protectPage() {
    if (!localStorage.getItem('token')) {
        window.location.href = '../auth/login.html';
        return false; // Indicates that the page should stop rendering
    }

    // Best-effort user hydration for pages that want to show the username.
    // Not awaited to keep existing pages working.
    appState.init().catch(() => {
        // api interceptor handles redirect on 401
    });

    // NEW: Check if chef has profile (only for non-onboarding pages)
    const currentPath = window.location.pathname;
    const isOnboardingPage = currentPath.includes('/onboarding.html');
    const isAuthPage = currentPath.includes('/auth/');
    
    if (!isOnboardingPage && !isAuthPage) {
        try {
            await api.get('/chefs/profile');
            // Profile exists, continue normally
        } catch (error) {
            if (error.response?.status === 404) {
                // No profile found, redirect to onboarding
                console.log('Chef profile not found, redirecting to onboarding');
                window.location.href = '/pages/chef/onboarding.html';
                return false;
            }
            // Other errors (401, 500, etc.) are handled by api interceptor
        }
    }

    const logoutButton = document.getElementById('logout-button') || document.getElementById('logout-btn');
    if (logoutButton) {
        logoutButton.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }

    return true; // Indicates that the user is authenticated
}
