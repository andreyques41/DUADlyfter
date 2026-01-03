// App initialization and core functionality
import { appState } from './state.js';
import { protectPage } from './auth-guard.js';

console.log('LyfterCook Frontend - v1.0.0');

// User Menu Dropdown
const userMenuButton = document.getElementById('user-menu-button');
const userMenuDropdown = document.getElementById('user-menu-dropdown');

if (userMenuButton && userMenuDropdown) {
  userMenuButton.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = userMenuDropdown.classList.contains('open');
    userMenuDropdown.classList.toggle('open');
    userMenuButton.setAttribute('aria-expanded', !isOpen);
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!userMenuButton.contains(e.target) && !userMenuDropdown.contains(e.target)) {
      userMenuDropdown.classList.remove('open');
      userMenuButton.setAttribute('aria-expanded', 'false');
    }
  });
}

// Logout functionality
const logoutBtn = document.getElementById('logout-btn');
if (logoutBtn) {
  logoutBtn.addEventListener('click', (e) => {
    e.preventDefault();
    appState.logout({ redirect: true });
  });
}

// If we're on a protected dashboard page, enforce session.
// (Auth pages should not include this script.)
const path = window.location.pathname || '';
if (path.includes('/pages/dashboard/')) {
  protectPage();

  // Hydrate user display (best-effort).
  appState.init().catch(() => {});
  appState.subscribe((s) => {
    const nameEl = document.querySelector('#user-menu-button span.hide-mobile');
    if (!nameEl) return;

    nameEl.textContent = s.user?.username || 'Chef';
  });
}

// Active navigation link
const currentPath = window.location.pathname;
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
  if (link.getAttribute('href') === currentPath) {
    link.classList.add('active');
  } else {
    link.classList.remove('active');
  }
});
