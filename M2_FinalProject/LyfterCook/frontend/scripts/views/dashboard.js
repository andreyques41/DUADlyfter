// frontend/scripts/views/dashboard.js
import { protectPage } from '../core/auth-guard.js';

document.addEventListener('DOMContentLoaded', () => {
    protectPage();
    // Any other dashboard-specific logic can go here.
});
