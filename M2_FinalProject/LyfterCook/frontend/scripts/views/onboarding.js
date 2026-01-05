/**
 * Chef Profile Onboarding
 * Guides new chefs to create their profile after registration
 */

import api from '../services/api.js';
import { AppState } from '../core/state.js';

document.addEventListener('DOMContentLoaded', async () => {
    // Ensure user is logged in
    if (!AppState.isAuthenticated()) {
        window.location.href = '/pages/auth/login.html';
        return;
    }

    const form = document.getElementById('chef-profile-form');
    const bioInput = document.getElementById('bio');
    const specialtyInput = document.getElementById('specialty');
    const locationInput = document.getElementById('location');
    const phoneInput = document.getElementById('phone');
    const charCount = document.querySelector('.char-count');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    const errorMessage = document.getElementById('error-message');

    // Character counter for bio
    bioInput.addEventListener('input', () => {
        const count = bioInput.value.length;
        charCount.textContent = `${count}/500 caracteres`;
        
        // Visual feedback when approaching limit
        if (count > 450) {
            charCount.style.color = '#dc2626';
        } else if (count > 400) {
            charCount.style.color = '#f59e0b';
        } else {
            charCount.style.color = '#6b7280';
        }
    });

    // Check if user already has profile (redirect if yes)
    try {
        const response = await api.get('/chefs/profile');
        if (response.data) {
            // Already has profile, redirect to dashboard
            console.log('Chef already has profile, redirecting to dashboard');
            window.location.href = '/pages/dashboard/overview.html';
            return;
        }
    } catch (error) {
        if (error.response?.status === 404) {
            // Expected: no profile exists yet, continue with onboarding
            console.log('No profile found, showing onboarding form');
        } else if (error.response?.status === 401) {
            // Unauthorized, redirect to login
            window.location.href = '/pages/auth/login.html';
            return;
        } else {
            console.error('Error checking profile:', error);
            // Continue with onboarding even if check fails
        }
    }

    // Form submission handler
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Hide previous errors
        errorMessage.style.display = 'none';
        
        // Disable form during submission
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline';
        
        // Disable all inputs
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => input.disabled = true);

        // Prepare form data
        const formData = {
            bio: bioInput.value.trim(),
            specialty: specialtyInput.value.trim(),
            location: locationInput.value.trim(),
            phone: phoneInput.value.trim() || null
        };

        // Client-side validation
        if (formData.bio.length < 10) {
            showError('La biografía debe tener al menos 10 caracteres');
            enableForm();
            return;
        }

        if (formData.specialty.length < 3) {
            showError('La especialidad debe tener al menos 3 caracteres');
            enableForm();
            return;
        }

        if (formData.location.length < 3) {
            showError('La ubicación debe tener al menos 3 caracteres');
            enableForm();
            return;
        }

        try {
            // Create chef profile
            const response = await api.post('/chefs/profile', formData);
            
            console.log('Chef profile created successfully:', response.data);
            
            // Success! Redirect to dashboard
            window.location.href = '/pages/dashboard/overview.html';
            
        } catch (error) {
            console.error('Error creating profile:', error);
            
            // Extract error message
            let message = 'Error al crear perfil. Por favor intenta de nuevo.';
            
            if (error.response?.data?.error) {
                message = error.response.data.error;
            } else if (error.response?.data?.message) {
                message = error.response.data.message;
            } else if (error.message) {
                message = `Error: ${error.message}`;
            }
            
            showError(message);
            enableForm();
        }
    });

    /**
     * Show error message
     */
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    /**
     * Re-enable form after error
     */
    function enableForm() {
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => input.disabled = false);
    }
});
