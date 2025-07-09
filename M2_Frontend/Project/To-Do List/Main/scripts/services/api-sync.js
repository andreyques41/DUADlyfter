// --- API Synchronization Service ---
// Handles API sync operations, timestamp management, and conflict resolution
console.log("api-sync.js loaded");

const apiInstance = axios.create({
	baseURL: APP_CONFIG.API_CONFIG.BASE_URL,
	timeout: APP_CONFIG.API_CONFIG.TIMEOUT,
	headers: { "Content-Type": "application/json" },
});

// --- Helper Functions ---

// Helper: Validate user session for API operations
function validateUserSession() {
	if (!UserSession.isLoggedIn()) {
		console.warn("API operation: User not logged in, skipping sync");
		return null;
	}
	return UserSession.getCurrentUser();
}

// Helper: Handle API errors with consistent logging
function handleAPIError(error, operation) {
	console.error(`${operation}: Error during API operation:`, error);

	// Don't show alert for sync errors - just log them
	if (error.response) {
		console.error(
			`${operation}: Server response error:`,
			error.response.status
		);
	} else if (error.message) {
		console.error(`${operation}: Error message:`, error.message);
	}
}

// Helper: Get user data from API
async function getUserDataFromAPI(userId) {
	try {
		const response = await apiInstance.get(`/${userId}`);
		return response.data;
	} catch (error) {
		handleAPIError(error, "getUserDataFromAPI");
		throw error;
	}
}

// Helper: Update user data via API
async function updateUserDataInAPI(userId, userData) {
	try {
		const response = await apiInstance.patch(`/${userId}`, {
			data: userData,
		});
		return response.data;
	} catch (error) {
		handleAPIError(error, "updateUserDataInAPI");
		throw error;
	}
}

// Helper: Check if API data is newer than local data
function isAPIDataNewer(localTimestamp, apiTimestamp) {
	if (!apiTimestamp) return false;

	const comparison = AppUtils.compareTimestamps(localTimestamp, apiTimestamp);
	return comparison === "api_newer";
}

// --- Main API Sync Functions ---

async function syncTasksFromAPI() {
	const currentUser = validateUserSession();
	if (!currentUser) return null;

	console.log(
		"syncTasksFromAPI: Getting tasks for user:",
		currentUser.fullName
	);

	try {
		const currentData = await getUserDataFromAPI(currentUser.id);
		console.log("syncTasksFromAPI: Successfully retrieved data from API");

		// Return the user data (which may include tasks)
		return currentData.data || {};
	} catch (error) {
		handleAPIError(error, "syncTasksFromAPI");
		return null;
	}
}

async function syncTasksToAPI(tasks, timestamp) {
	const currentUser = validateUserSession();
	if (!currentUser) return;

	// Use provided timestamp or current time
	const lastModified = timestamp || AppUtils.getCurrentTimestamp();

	console.log(
		"syncTasksToAPI: Syncing tasks for user:",
		currentUser.fullName,
		"with timestamp:",
		lastModified
	);

	try {
		const currentData = await getUserDataFromAPI(currentUser.id);

		// Check if API has newer data
		if (
			currentData.data &&
			isAPIDataNewer(lastModified, currentData.data.lastModified)
		) {
			console.log("syncTasksToAPI: API has newer data, skipping upload");
			return currentData.data;
		}

		// Merge tasks with existing user data, including timestamp
		const updatedData = {
			...currentData.data,
			tasks: tasks,
			lastModified: lastModified,
		};

		// Update user data with tasks and timestamp
		const response = await updateUserDataInAPI(currentUser.id, updatedData);

		console.log(
			"syncTasksToAPI: Success! Tasks synced to API with timestamp:",
			lastModified
		);
		return response.data;
	} catch (error) {
		handleAPIError(error, "syncTasksToAPI");
		return null;
	}
}

// Expose globally
window.syncTasksFromAPI = syncTasksFromAPI;
window.syncTasksToAPI = syncTasksToAPI;
