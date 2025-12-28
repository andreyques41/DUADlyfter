// frontend/scripts/views/register.js
import { register } from '../services/auth.js';

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    const errorMessage = document.getElementById('error-message');
    const submitButton = registerForm.querySelector('button');

    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            errorMessage.textContent = ''; // Clear previous errors
            submitButton.disabled = true;
            submitButton.textContent = 'Loading...';

            const username = registerForm.username.value;
            const email = registerForm.email.value;
            const password = registerForm.password.value;

            try {
                const result = await register(username, email, password);
                console.log('Registration successful:', result);
                // Redirect to the login page
                window.location.href = 'login.html';
            } catch (error) {
                console.error('Registration failed:', error);
                const message = error.details ? Object.values(error.details).join(', ') : 'Please check your input and try again.';
                errorMessage.textContent = `Registration failed: ${message}`;
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = 'Register';
            }
        });
    }
});
