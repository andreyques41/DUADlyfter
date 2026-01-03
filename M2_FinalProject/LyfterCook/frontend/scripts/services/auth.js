// frontend/scripts/services/auth.js
import api from './api.js';
import { appState } from '../core/state.js';

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
        const token = response?.data?.data?.token;
        const user = response?.data?.data?.user;

        if (token) {
            // Decision: store token in localStorage.
            appState.setToken(token);
        }

        if (user) {
            appState.setUser(user);
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
    appState.logout({ redirect: true });
}
