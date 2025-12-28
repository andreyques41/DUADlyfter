// frontend/scripts/views/clients.js
import api from '../services/api.js';
import { logout } from '../services/auth.js';

document.addEventListener('DOMContentLoaded', () => {
    // Basic protected route check
    if (!localStorage.getItem('token')) {
        window.location.href = '../auth/login.html';
        return; // Stop execution if not authenticated
    }

    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            logout();
            window.location.href = '../auth/login.html';
        });
    }

    // --- DOM Elements ---
    const clientsTableBody = document.getElementById('clients-table-body');
    const addClientForm = document.getElementById('add-client-form');
    const errorMessage = document.getElementById('error-message');
    const loadingMessage = document.getElementById('loading-message');
    const submitButton = addClientForm.querySelector('button');

    // Modal Elements
    const editModal = document.getElementById('edit-client-modal');
    const editClientForm = document.getElementById('edit-client-form');
    const closeButton = editModal.querySelector('.close-button');
    const editErrorMessage = document.getElementById('edit-error-message');
    const editSubmitButton = editClientForm.querySelector('button');

    // --- Functions ---

    /**
     * Fetches clients from the API and renders them in the table.
     */
    async function fetchAndRenderClients() {
        try {
            loadingMessage.textContent = 'Loading clients...';
            clientsTableBody.innerHTML = ''; // Clear existing rows

            const response = await api.get('/clients');
            const clients = response.data.data;

            if (clients && clients.length > 0) {
                clients.forEach(client => {
                    const row = document.createElement('tr');
                    row.id = `client-row-${client.id}`; // Add a unique ID to each row
                    row.innerHTML = `
                        <td>${client.name}</td>
                        <td>${client.email || ''}</td>
                        <td>${client.phone || ''}</td>
                        <td>${client.company || ''}</td>
                        <td>
                            <button class="edit-button" data-id="${client.id}">Edit</button>
                            <button class="delete-button" data-id="${client.id}">Delete</button>
                        </td>
                    `;
                    clientsTableBody.appendChild(row);
                });
                loadingMessage.style.display = 'none';
            } else {
                loadingMessage.textContent = 'No clients found. Add one using the form above.';
            }
        } catch (error) {
            console.error('Failed to fetch clients:', error);
            loadingMessage.textContent = 'Error loading clients.';
        }
    }

    /**
     * Handles the submission of the "Add Client" form.
     */
    async function handleAddClient(event) {
        event.preventDefault();
        errorMessage.textContent = '';
        submitButton.disabled = true;
        submitButton.textContent = 'Adding...';

        const formData = new FormData(addClientForm);
        const clientData = {
            name: formData.get('name'),
            email: formData.get('email'),
            phone: formData.get('phone'),
            company: formData.get('company'),
            notes: formData.get('notes'),
        };

        try {
            await api.post('/clients', clientData);
            addClientForm.reset(); // Clear the form
            fetchAndRenderClients(); // Refresh the list
        } catch (error) {
            console.error('Failed to add client:', error);
            errorMessage.textContent = 'Failed to add client. Please check the details and try again.';
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Add Client';
        }
    }

    /**
     * Opens the edit modal and populates it with client data.
     */
    async function openEditModal(clientId) {
        try {
            const response = await api.get(`/clients/${clientId}`);
            const client = response.data.data;

            editClientForm['edit-client-id'].value = client.id;
            editClientForm['edit-name'].value = client.name;
            editClientForm['edit-email'].value = client.email || '';
            editClientForm['edit-phone'].value = client.phone || '';
            editClientForm['edit-company'].value = client.company || '';
            editClientForm['edit-notes'].value = client.notes || '';

            editModal.style.display = 'block';
        } catch (error) {
            console.error(`Failed to fetch client ${clientId}:`, error);
            alert('Failed to load client details for editing.');
        }
    }

    /**
     * Handles the submission of the "Edit Client" form.
     */
    async function handleUpdateClient(event) {
        event.preventDefault();
        editErrorMessage.textContent = '';
        editSubmitButton.disabled = true;
        editSubmitButton.textContent = 'Saving...';

        const clientId = editClientForm['edit-client-id'].value;
        const clientData = {
            name: editClientForm['edit-name'].value,
            email: editClientForm['edit-email'].value,
            phone: editClientForm['edit-phone'].value,
            company: editClientForm['edit-company'].value,
            notes: editClientForm['edit-notes'].value,
        };

        try {
            await api.put(`/clients/${clientId}`, clientData);
            editModal.style.display = 'none';
            fetchAndRenderClients(); // Refresh the list
        } catch (error) {
            console.error(`Failed to update client ${clientId}:`, error);
            editErrorMessage.textContent = 'Failed to save changes. Please try again.';
        } finally {
            editSubmitButton.disabled = false;
            editSubmitButton.textContent = 'Save Changes';
        }
    }

    /**
     * Handles clicks on the table body for edit or delete actions.
     */
    function handleTableClick(event) {
        const target = event.target;
        if (target.classList.contains('edit-button')) {
            const clientId = target.dataset.id;
            openEditModal(clientId);
        } else if (target.classList.contains('delete-button')) {
            handleDeleteClient(event); // Reuse the delete handler
        }
    }

    /**
     * Handles the deletion of a client.
     */
    async function handleDeleteClient(event) {
        const target = event.target;
        const clientId = target.dataset.id;
        const clientRow = target.closest('tr');
        const clientName = clientRow.querySelector('td').textContent;

        if (confirm(`Are you sure you want to delete the client "${clientName}"?`)) {
            try {
                await api.delete(`/clients/${clientId}`);
                fetchAndRenderClients(); // Refresh the list
            } catch (error) {
                console.error(`Failed to delete client ${clientId}:`, error);
                alert('Failed to delete client. Please try again.');
            }
        }
    }

    // --- Event Listeners ---
    addClientForm.addEventListener('submit', handleAddClient);
    editClientForm.addEventListener('submit', handleUpdateClient);
    clientsTableBody.addEventListener('click', handleTableClick);

    // Modal close listeners
    closeButton.addEventListener('click', () => editModal.style.display = 'none');
    window.addEventListener('click', (event) => {
        if (event.target == editModal) {
            editModal.style.display = 'none';
        }
    });

    // --- Initial Load ---
    fetchAndRenderClients();
});
