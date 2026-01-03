// App initialization and core functionality
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
    // TODO: Implement actual logout logic
    console.log('Logout clicked');
    alert('Logout functionality will be implemented with AppState');
    // window.location.href = '/pages/auth/login.html';
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
