// frontend/scripts/services/auth.js
import api from './api.js';

/**
 * Registers a new user.
 * @param {string} username - The username.
 * @param {string} email - The user's email.
 * @param {string} password - The user's password.
 * @returns {Promise<object>} - The response data.
 */
export async function register(username, email, password) {
    try {
        const response = await api.post('/auth/register', { username, email, password });
        return response.data;
    } catch (error) {
        console.error('Registration failed:', error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Registration failed');
    }
}

/**
 * Logs in a user.
 * @param {string} username - The username.
 * @param {string} password - The user's password.
 * @returns {Promise<object>} - The response data.
 */
export async function login(username, password) {
    try {
        const response = await api.post('/auth/login', { username, password });
        if (response.data && response.data.data.token) {
            // Note: Storing JWT in localStorage is convenient for development but has security risks (XSS).
            // For production, consider using httpOnly cookies for better security.
            localStorage.setItem('token', response.data.data.token);
        }
        return response.data;
    } catch (error) {
        console.error('Login failed:', error.response ? error.response.data : error.message);
        throw error.response ? error.response.data : new Error('Login failed');
    }
}

/**
 * Logs out the current user.
 */
export function logout() {
    localStorage.removeItem('token');
}
