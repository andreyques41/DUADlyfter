// frontend/scripts/views/dishes.js
import api from '../services/api.js';
import { protectPage } from '../core/auth-guard.js';
import { CLOUDINARY_CLOUD_NAME, CLOUDINARY_UPLOAD_PRESET } from '../core/config.js';

document.addEventListener('DOMContentLoaded', () => {
    if (!protectPage()) return; // Stop execution if not authenticated

    // --- DOM Elements ---
    const dishesContainer = document.getElementById('dishes-container');
    const addDishForm = document.getElementById('add-dish-form');
    const errorMessage = document.getElementById('error-message');
    const loadingMessage = document.getElementById('loading-message');
    const uploadWidgetButton = document.getElementById('upload-widget');
    const photoUrlInput = document.getElementById('dish-photo-url');
    const imagePreview = document.getElementById('image-preview');
    const submitButton = addDishForm.querySelector('button[type="submit"]');

    // Modal Elements
    const editModal = document.getElementById('edit-dish-modal');
    const editDishForm = document.getElementById('edit-dish-form');
    const closeButton = editModal.querySelector('.close-button');
    const editErrorMessage = document.getElementById('edit-error-message');
    const editSubmitButton = editDishForm.querySelector('button[type="submit"]');

    /**
     * Extracts a user-friendly error message from an API error response.
     */
    function getApiErrorMessage(error) {
        const apiError = error?.response?.data?.error;
        if (apiError) {
            if (apiError === 'Chef profile not found') {
                return 'Chef profile not found. Please create your chef profile first (POST /chefs/profile).';
            }
            return apiError;
        }

        return 'An unexpected error occurred. Please try again.';
    }

    // --- Functions ---

    /**
     * Fetches dishes from the API and renders them as cards.
     */
    async function fetchAndRenderDishes() {
        try {
            loadingMessage.textContent = 'Loading dishes...';
            dishesContainer.innerHTML = '';

            const response = await api.get('/dishes');
            const dishes = response.data.data;

            if (dishes && dishes.length > 0) {
                dishes.forEach(dish => {
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.id = `dish-card-${dish.id}`;
                    card.innerHTML = `
                        <div class="card-body">
                            <div style="display:flex; gap: var(--spacing-4); align-items: flex-start;">
                                <img src="${dish.photo_url || 'https://via.placeholder.com/250x150'}" alt="${dish.name}" style="width: 84px; height: 64px; object-fit: cover; border-radius: var(--radius-lg);" />
                                <div style="flex: 1;">
                                    <h4 style="margin: 0 0 var(--spacing-2) 0;">${dish.name}</h4>
                                    <p style="margin: 0; color: var(--color-gray-600);">$${dish.price}</p>
                                </div>
                            </div>
                            <div style="margin-top: var(--spacing-4); display:flex; gap: var(--spacing-2);">
                                <button class="btn btn-outline edit-button" data-id="${dish.id}">Edit</button>
                                <button class="btn btn-outline delete-button" data-id="${dish.id}">Delete</button>
                            </div>
                        </div>
                    `;
                    dishesContainer.appendChild(card);
                });
                loadingMessage.style.display = 'none';
            } else {
                loadingMessage.textContent = 'No dishes found. Add one using the form above.';
            }
        } catch (error) {
            console.error('Failed to fetch dishes:', error);
            loadingMessage.textContent = getApiErrorMessage(error);
            loadingMessage.style.display = 'block';
        }
    }

    /**
     * Handles the submission of the "Add Dish" form.
     */
    async function handleAddDish(event) {
        event.preventDefault();
        errorMessage.textContent = '';
        errorMessage.style.display = 'none';
        submitButton.disabled = true;
        submitButton.textContent = 'Adding...';

        const dishData = {
            name: addDishForm.name.value,
            price: addDishForm.price.value,
            description: addDishForm.description.value,
            photo_url: photoUrlInput.value,
        };

        try {
            await api.post('/dishes', dishData);
            addDishForm.reset();
            imagePreview.style.display = 'none';
            photoUrlInput.value = '';
            fetchAndRenderDishes();
        } catch (error) {
            console.error('Failed to add dish:', error);
            errorMessage.textContent = getApiErrorMessage(error);
            errorMessage.style.display = 'block';
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Add Dish';
        }
    }

    /**
     * Initializes the Cloudinary upload widget.
     */
    function initializeUploadWidget() {
        const cloudName = CLOUDINARY_CLOUD_NAME !== 'YOUR_CLOUD_NAME' ? CLOUDINARY_CLOUD_NAME : 'demo';
        const uploadPreset = CLOUDINARY_UPLOAD_PRESET !== 'YOUR_UPLOAD_PRESET' ? CLOUDINARY_UPLOAD_PRESET : 'docs_upload_example';

        const myWidget = cloudinary.createUploadWidget({
            cloudName: cloudName,
            uploadPreset: uploadPreset
        }, (error, result) => {
            if (!error && result && result.event === "success") {
                photoUrlInput.value = result.info.secure_url;
                imagePreview.src = result.info.secure_url;
                imagePreview.style.display = 'block';
            }
        });

        uploadWidgetButton.addEventListener("click", () => myWidget.open(), false);
    }

    /**
     * Opens the edit modal and populates it with dish data.
     */
    async function openEditModal(dishId) {
        try {
            const response = await api.get(`/dishes/${dishId}`);
            const dish = response.data.data;

            editDishForm['edit-dish-id'].value = dish.id;
            editDishForm['edit-dish-name'].value = dish.name;
            editDishForm['edit-dish-price'].value = dish.price;
            editDishForm['edit-dish-description'].value = dish.description || '';

            editModal.style.display = 'block';
        } catch (error) {
            console.error(`Failed to fetch dish ${dishId}:`, error);
            alert(getApiErrorMessage(error));
        }
    }

    /**
     * Handles the submission of the "Edit Dish" form.
     */
    async function handleUpdateDish(event) {
        event.preventDefault();
        editErrorMessage.textContent = '';
        editErrorMessage.style.display = 'none';
        editSubmitButton.disabled = true;
        editSubmitButton.textContent = 'Saving...';

        const dishId = editDishForm['edit-dish-id'].value;
        const dishData = {
            name: editDishForm['edit-dish-name'].value,
            price: editDishForm['edit-dish-price'].value,
            description: editDishForm['edit-dish-description'].value,
        };

        try {
            await api.put(`/dishes/${dishId}`, dishData);
            editModal.style.display = 'none';
            fetchAndRenderDishes();
        } catch (error) {
            console.error(`Failed to update dish ${dishId}:`, error);
            editErrorMessage.textContent = getApiErrorMessage(error);
            editErrorMessage.style.display = 'block';
        } finally {
            editSubmitButton.disabled = false;
            editSubmitButton.textContent = 'Save Changes';
        }
    }

    /**
     * Handles clicks on the dish cards for edit or delete actions.
     */
    async function handleCardClick(event) {
        const target = event.target;
        if (target.classList.contains('edit-button')) {
            openEditModal(target.dataset.id);
        } else if (target.classList.contains('delete-button')) {
            const dishId = target.dataset.id;
            const dishCard = target.closest('.dish-card');
            const dishName = dishCard.querySelector('h4').textContent;

            if (confirm(`Are you sure you want to delete the dish "${dishName}"?`)) {
                try {
                    await api.delete(`/dishes/${dishId}`);
                    fetchAndRenderDishes();
                } catch (error) {
                    console.error(`Failed to delete dish ${dishId}:`, error);
                    alert(getApiErrorMessage(error));
                }
            }
        }
    }

    // --- Event Listeners ---
    addDishForm.addEventListener('submit', handleAddDish);
    editDishForm.addEventListener('submit', handleUpdateDish);
    dishesContainer.addEventListener('click', handleCardClick);

    // Modal close listeners
    closeButton.addEventListener('click', () => editModal.style.display = 'none');
    window.addEventListener('click', (event) => {
        if (event.target == editModal) {
            editModal.style.display = 'none';
        }
    });

    // --- Initial Load ---
    fetchAndRenderDishes();
    initializeUploadWidget();
});
