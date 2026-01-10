// frontend/scripts/views/dashboard.js
import { protectPage } from '../core/auth-guard.js';

document.addEventListener('DOMContentLoaded', () => {
    (async () => {
        await protectPage();
    })();
    // Any other dashboard-specific logic can go here.
});
