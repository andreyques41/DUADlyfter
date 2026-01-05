/**
 * Public Chef Profile View
 * Displays chef profile and handles contact form submission
 */

import api from '../services/api.js';

document.addEventListener('DOMContentLoaded', async () => {
    const loadingState = document.getElementById('loading-state');
    const errorState = document.getElementById('error-state');
    const errorText = document.getElementById('error-text');
    const chefContent = document.getElementById('chef-content');

    // Get chef ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const chefId = urlParams.get('id');

    if (!chefId) {
        showError('No se especificó ID de chef');
        return;
    }

    try {
        // Fetch chef profile
        const response = await api.get(`/public/chefs/${chefId}`);
        const chef = response.data;

        // Hide loading, show content
        loadingState.style.display = 'none';
        chefContent.style.display = 'block';

        // Render chef profile
        renderChefProfile(chef);

        // Initialize contact form
        initContactForm(chef);

    } catch (error) {
        console.error('Error fetching chef profile:', error);
        const message = error.response?.data?.error || 'Error al cargar el perfil del chef';
        showError(message);
    }

    function showError(message) {
        loadingState.style.display = 'none';
        errorState.style.display = 'block';
        errorText.textContent = message;
    }

    function renderChefProfile(chef) {
        // Chef name
        document.getElementById('chef-name').textContent = chef.name || 'Chef';

        // Chef specialty
        document.getElementById('chef-specialty').textContent = chef.specialty || 'Especialidad Culinaria';

        // Chef location
        if (chef.location) {
            document.getElementById('chef-location').textContent = `📍 ${chef.location}`;
        } else {
            document.getElementById('chef-location').style.display = 'none';
        }

        // Biography
        if (chef.bio) {
            const bioSection = document.getElementById('bio-section');
            bioSection.style.display = 'block';
            document.getElementById('chef-bio').textContent = chef.bio;
        }

        // Update page title
        document.title = `${chef.name} - LyfterCook`;
    }

    function initContactForm(chef) {
        const form = document.getElementById('contact-form');
        const messageInput = document.getElementById('contact-message');
        const charCount = document.querySelector('.char-count');
        const submitBtn = document.getElementById('contact-submit');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnLoader = submitBtn.querySelector('.btn-loader');
        const errorDiv = document.getElementById('contact-error');
        const successDiv = document.getElementById('contact-success');

        // Character counter
        messageInput.addEventListener('input', () => {
            const count = messageInput.value.length;
            charCount.textContent = `${count}/2000 caracteres`;

            // Visual feedback
            if (count > 1950) {
                charCount.style.color = '#dc2626';
            } else if (count > 1800) {
                charCount.style.color = '#f59e0b';
            } else {
                charCount.style.color = '#6b7280';
            }
        });

        // Form submission
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Hide previous messages
            errorDiv.style.display = 'none';
            successDiv.style.display = 'none';

            // Disable form
            submitBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoader.style.display = 'inline';

            // Disable all inputs
            const inputs = form.querySelectorAll('input, textarea');
            inputs.forEach(input => input.disabled = true);

            const formData = {
                chef_id: parseInt(chefId),
                name: document.getElementById('contact-name').value.trim(),
                email: document.getElementById('contact-email').value.trim(),
                phone: document.getElementById('contact-phone').value.trim() || null,
                message: messageInput.value.trim()
            };

            // Client-side validation
            if (formData.message.length < 10) {
                showFormError('El mensaje debe tener al menos 10 caracteres');
                enableForm();
                return;
            }

            if (formData.message.length > 2000) {
                showFormError('El mensaje no puede exceder 2000 caracteres');
                enableForm();
                return;
            }

            try {
                // BACKEND TODO: Implement POST /public/contact
                // For now, this will fail with 404 until backend is ready
                await api.post('/public/contact', formData);

                // Success
                successDiv.style.display = 'block';
                form.reset();
                charCount.textContent = '0/2000 caracteres';

                // Scroll to success message
                successDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });

                // Re-enable form after success
                setTimeout(() => {
                    enableForm();
                }, 1000);

            } catch (error) {
                console.error('Error sending contact message:', error);

                let message = 'Error al enviar mensaje. Por favor intenta de nuevo.';

                if (error.response?.status === 404) {
                    message = '⚠️ Backend no implementado aún: POST /public/contact pendiente';
                } else if (error.response?.data?.error) {
                    message = error.response.data.error;
                }

                showFormError(message);
                enableForm();
            }
        });

        function showFormError(message) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        function enableForm() {
            submitBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';

            const inputs = form.querySelectorAll('input, textarea');
            inputs.forEach(input => input.disabled = false);
        }
    }
});
