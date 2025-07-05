// --- API Synchronization for Task Storage ---
// Handles API sync operations, timestamp management, and conflict resolution
console.log("storage-sync.js loaded");

const apiInstance = axios.create({
	baseURL: APP_CONFIG.API_CONFIG.BASE_URL,
	timeout: APP_CONFIG.API_CONFIG.TIMEOUT,
	headers: { "Content-Type": "application/json" },
});

async function syncTasksFromAPI() {
	const userId = localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_ID);
	const userFullName = localStorage.getItem(
		APP_CONFIG.STORAGE_KEYS.USER_FULL_NAME
	);

	// Check if user is logged in
	if (!userId) {
		console.warn("syncTasksFromAPI: No user ID found, skipping sync");
		return null;
	}

	console.log("syncTasksFromAPI: Getting tasks for user:", userFullName);

	try {
		// Get current user data from API
		const getResponse = await apiInstance.get(`/${userId}`);
		const currentData = getResponse.data;

		console.log("syncTasksFromAPI: Successfully retrieved data from API");

		// Return the user data (which may include tasks)
		return currentData.data || {};
	} catch (error) {
		console.error("syncTasksFromAPI: Error getting tasks from API:", error);

		// Don't show alert for sync errors - just log them
		if (error.response) {
			console.error(
				"syncTasksFromAPI: Server response error:",
				error.response.status
			);
		} else if (error.message) {
			console.error("syncTasksFromAPI: Error message:", error.message);
		}

		// Return null to indicate sync failure
		return null;
	}
}

async function syncTasksToAPI(tasks, timestamp) {
	const userId = localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_ID);
	const userFullName = localStorage.getItem(
		APP_CONFIG.STORAGE_KEYS.USER_FULL_NAME
	);

	// Check if user is logged in
	if (!userId) {
		console.warn("syncTasksToAPI: No user ID found, skipping sync");
		return;
	}

	// Use provided timestamp or current time
	const lastModified = timestamp || AppUtils.getCurrentTimestamp();

	console.log(
		"syncTasksToAPI: Syncing tasks for user:",
		userFullName,
		"with timestamp:",
		lastModified
	);

	try {
		// Get current user data
		const getResponse = await apiInstance.get(`/${userId}`);
		const currentData = getResponse.data;

		// Check if API has newer data
		if (currentData.data && currentData.data.lastModified) {
			const comparison = AppUtils.compareTimestamps(
				lastModified,
				currentData.data.lastModified
			);

			if (comparison === "api_newer") {
				console.log("syncTasksToAPI: API has newer data, skipping upload");
				return currentData.data;
			}
		}

		// Merge tasks with existing user data, including timestamp
		const updatedData = {
			...currentData.data,
			tasks: tasks,
			lastModified: lastModified,
		};

		// Update user data with tasks and timestamp
		const response = await apiInstance.patch(`/${userId}`, {
			data: updatedData,
		});

		console.log(
			"syncTasksToAPI: Success! Tasks synced to API with timestamp:",
			lastModified
		);
		return response.data.data;
	} catch (error) {
		console.error("syncTasksToAPI: Error syncing tasks:", error);

		// Don't show alert for sync errors - just log them
		if (error.response) {
			console.error(
				"syncTasksToAPI: Server response error:",
				error.response.status
			);
		} else if (error.message) {
			console.error("syncTasksToAPI: Error message:", error.message);
		}

		// Return null to indicate sync failure
		return null;
	}
}

// Expose globally
window.syncTasksFromAPI = syncTasksFromAPI;
window.syncTasksToAPI = syncTasksToAPI;

// Check availability of exposed functions
if (window.syncTasksFromAPI) {
	console.log("storage-sync.js: syncTasksFromAPI function is available");
} else {
	console.warn("storage-sync.js: syncTasksFromAPI function not found");
}

if (window.syncTasksToAPI) {
	console.log("storage-sync.js: syncTasksToAPI function is available");
} else {
	console.warn("storage-sync.js: syncTasksToAPI function not found");
}
