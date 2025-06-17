const axios = require("axios");

// Create an axios instance for API requests
const apiInstance = axios.create({
	baseURL: `https://api.restful-api.dev/objects`,
	timeout: 1000,
	headers: {
		"Content-Type": "application/json", // Set content type to JSON
	},
});

// Fetches and logs a user by ID from the API
async function getUser(apiInstance, userId) {
	try {
		const response = await apiInstance.get(`/${userId}`);
		logData(response.data); // Log the response data
	} catch (error) {
		if (error.response) {
			// Handle HTTP errors
			throw new Error(
				`HTTP error! Status: ${error.response.status}. The user with id ${userId} does not exist`
			);
		} else {
			throw error;
		}
	}
}

// Logs the response data from the server (Axios response)
function logData(data) {
	console.log(`Log of data:`, data);
}

// Example usage: fetch and log users with error handling
(async () => {
	try {
		await getUser(apiInstance, 2); // Fetch user with ID 2
		await getUser(apiInstance, 25); // Fetch user with ID 25
	} catch (error) {
		console.error(error.message);
	}
})();
