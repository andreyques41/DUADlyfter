// frontend/scripts/core/config.js

// Define the base URL for the API.
// When running via Vite, use the dev proxy configured in `frontend/vite.config.js`.
// This avoids CORS and keeps frontend code environment-agnostic.
export const API_BASE_URL = '/api';

// --- Cloudinary Configuration ---
// IMPORTANT: Replace these with your actual Cloudinary credentials.
export const CLOUDINARY_CLOUD_NAME = 'YOUR_CLOUD_NAME'; // e.g., 'dabc123'
export const CLOUDINARY_UPLOAD_PRESET = 'YOUR_UPLOAD_PRESET'; // e.g., 'ab12cd34'
