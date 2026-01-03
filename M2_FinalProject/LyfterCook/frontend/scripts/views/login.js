// frontend/scripts/views/login.js
import { login } from '../services/auth.js';

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');
    const submitButton = loginForm.querySelector('button');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            errorMessage.textContent = ''; // Clear previous errors
            submitButton.disabled = true;
            submitButton.textContent = 'Loading...';

            const username = loginForm.username.value;
            const password = loginForm.password.value;

            try {
                const result = await login(username, password);
                console.log('Login successful:', result);
                // Redirect to the dashboard
                window.location.href = '/pages/dashboard/overview.html';
            } catch (error) {
                console.error('Login failed:', error);
                const message = error?.error || 'Login failed. Please check your credentials and try again.';
                errorMessage.textContent = message;
                errorMessage.style.display = 'block';
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = 'Login';
            }
        });
    }
});
