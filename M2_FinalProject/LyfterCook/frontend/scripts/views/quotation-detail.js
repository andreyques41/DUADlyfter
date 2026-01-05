/**
 * Quotation Detail View
 * Displays quotation details and handles sending via email
 */

import api from '../services/api.js';
import { protectPage } from '../core/auth-guard.js';

document.addEventListener('DOMContentLoaded', async () => {
    if (!await protectPage()) return;

    const loadingState = document.getElementById('loading-state');
    const errorState = document.getElementById('error-state');
    const errorText = document.getElementById('error-text');
    const quotationContent = document.getElementById('quotation-content');

    // Get quotation ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const quotationId = urlParams.get('id');

    if (!quotationId) {
        showError('No se especificó ID de cotización');
        return;
    }

    try {
        // Fetch quotation data
        const response = await api.get(`/quotations/${quotationId}`);
        const quotation = response.data;

        // Hide loading, show content
        loadingState.style.display = 'none';
        quotationContent.style.display = 'block';

        // Render quotation
        renderQuotation(quotation);

        // Initialize send email modal
        initSendEmailModal(quotation);

    } catch (error) {
        console.error('Error fetching quotation:', error);
        const message = error.response?.data?.error || 'Error al cargar la cotización';
        showError(message);
    }

    function showError(message) {
        loadingState.style.display = 'none';
        errorState.style.display = 'block';
        errorText.textContent = message;
    }

    function renderQuotation(quotation) {
        // Quotation number
        document.getElementById('quotation-number').textContent = 
            `Cotización #${quotation.quotation_number}`;

        // Status badge
        const statusContainer = document.getElementById('quotation-status-container');
        const statusClass = `status-${quotation.status}`;
        const statusText = {
            'draft': 'Borrador',
            'sent': 'Enviada',
            'accepted': 'Aceptada',
            'rejected': 'Rechazada',
            'expired': 'Expirada'
        }[quotation.status] || quotation.status;
        
        statusContainer.innerHTML = `<span class="status-badge ${statusClass}">${statusText}</span>`;

        // Meta information
        const metaContainer = document.getElementById('quotation-meta');
        const metaItems = [];

        if (quotation.client) {
            metaItems.push({
                label: 'Cliente',
                value: quotation.client.name
            });
        }

        if (quotation.event_date) {
            metaItems.push({
                label: 'Fecha del Evento',
                value: new Date(quotation.event_date).toLocaleDateString('es-MX')
            });
        }

        if (quotation.number_of_people) {
            metaItems.push({
                label: 'Número de Personas',
                value: quotation.number_of_people
            });
        }

        if (quotation.valid_until) {
            metaItems.push({
                label: 'Válido Hasta',
                value: new Date(quotation.valid_until).toLocaleDateString('es-MX')
            });
        }

        metaContainer.innerHTML = metaItems.map(item => `
            <div class="meta-item">
                <span class="meta-label">${item.label}</span>
                <span class="meta-value">${item.value}</span>
            </div>
        `).join('');

        // Items table
        const itemsTable = document.getElementById('items-tbody');
        if (quotation.items && quotation.items.length > 0) {
            itemsTable.innerHTML = quotation.items.map(item => {
                const quantity = item.quantity || 1;
                const unitPrice = parseFloat(item.unit_price || 0);
                const subtotal = quantity * unitPrice;

                return `
                    <tr>
                        <td>
                            <div class="item-name">${item.name}</div>
                            ${item.description ? `<div class="item-description">${item.description}</div>` : ''}
                        </td>
                        <td>${quantity}</td>
                        <td class="price-cell">$${unitPrice.toFixed(2)}</td>
                        <td class="price-cell">$${subtotal.toFixed(2)}</td>
                    </tr>
                `;
            }).join('');
        } else {
            itemsTable.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #9ca3af;">No hay ítems en esta cotización</td></tr>';
        }

        // Total amount
        document.getElementById('total-amount').textContent = 
            `$${parseFloat(quotation.total_price || quotation.total_amount || 0).toFixed(2)}`;

        // PDF download link
        document.getElementById('download-pdf-btn').href = 
            `/api/quotations/${quotation.id}/pdf`;

        // Notes section
        if (quotation.notes) {
            const notesSection = document.getElementById('notes-section');
            notesSection.style.display = 'block';
            document.getElementById('notes-content').textContent = quotation.notes;
        }
    }

    function initSendEmailModal(quotation) {
        const sendBtn = document.getElementById('send-email-btn');
        const modal = document.getElementById('send-email-modal');
        const closeBtn = document.getElementById('close-modal');
        const cancelBtn = document.getElementById('cancel-send');
        const form = document.getElementById('send-email-form');
        const confirmBtn = document.getElementById('confirm-send');
        const btnText = confirmBtn.querySelector('.btn-text');
        const btnLoader = confirmBtn.querySelector('.btn-loader');
        const errorDiv = document.getElementById('send-error');
        const successDiv = document.getElementById('send-success');

        // Check if quotation has client with email
        if (!quotation.client?.email) {
            sendBtn.disabled = true;
            sendBtn.title = 'Esta cotización no tiene email de cliente asociado';
            sendBtn.innerHTML = '✉️ Sin Email de Cliente';
            return;
        }

        // Open modal
        sendBtn.addEventListener('click', () => {
            document.getElementById('modal-client-name').textContent = 
                quotation.client?.name || 'Sin cliente';
            document.getElementById('modal-client-email').textContent = 
                quotation.client?.email || 'Sin email';
            document.getElementById('modal-quotation-number').textContent = 
                quotation.quotation_number;
            
            modal.classList.add('show');
            errorDiv.style.display = 'none';
            successDiv.style.display = 'none';
        });

        // Close modal
        const closeModal = () => {
            modal.classList.remove('show');
            form.reset();
        };

        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
        
        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });

        // Submit form
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            errorDiv.style.display = 'none';
            successDiv.style.display = 'none';
            confirmBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoader.style.display = 'inline-flex';

            const payload = {
                send_to_client: true,
                custom_email: document.getElementById('custom-email').value.trim() || null,
                custom_message: document.getElementById('custom-message').value.trim() || null
            };

            try {
                // BACKEND TODO: Implement POST /quotations/:id/send
                // For now, this will fail with 404 until backend is ready
                const response = await api.post(`/quotations/${quotation.id}/send`, payload);

                // Success
                const sentTo = response.data.sent_to || payload.custom_email || quotation.client.email;
                successDiv.textContent = `✅ Email enviado exitosamente a ${sentTo}`;
                successDiv.style.display = 'block';

                // Close modal after 2 seconds
                setTimeout(() => {
                    closeModal();
                }, 2000);

            } catch (error) {
                console.error('Error sending email:', error);
                
                let message = 'Error al enviar email. Por favor intenta de nuevo.';
                
                if (error.response?.status === 404) {
                    message = '⚠️ Backend no implementado aún: POST /quotations/:id/send pendiente';
                } else if (error.response?.data?.error) {
                    message = error.response.data.error;
                }
                
                errorDiv.textContent = message;
                errorDiv.style.display = 'block';
            } finally {
                confirmBtn.disabled = false;
                btnText.style.display = 'inline';
                btnLoader.style.display = 'none';
            }
        });
    }
});
