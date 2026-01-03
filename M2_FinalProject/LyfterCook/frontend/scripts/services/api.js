// frontend/scripts/services/api.js
import { API_BASE_URL } from '../core/config.js';

function shouldRedirectOn401() {
    const path = window.location.pathname || '';
    // Don't redirect loops if we're already on an auth page.
    return !path.includes('/pages/auth/login.html') && !path.includes('/pages/auth/register.html');
}

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, error => {
    return Promise.reject(error);
});

api.interceptors.response.use(
    response => response,
    error => {
        const status = error?.response?.status;
        if (status === 401) {
            // Spec decision: any 401 means the session is not valid.
            localStorage.removeItem('token');

            if (shouldRedirectOn401()) {
                window.location.href = '/pages/auth/login.html';
            }
        }

        return Promise.reject(error);
    }
);

export default api;
