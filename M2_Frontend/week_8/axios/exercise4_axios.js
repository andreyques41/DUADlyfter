const axios = require("axios");

// Create an axios instance for API requests
const apiInstance = axios.create({
	baseURL: `https://api.restful-api.dev/objects`,
	timeout: 1000,
	headers: {
		"Content-Type": "application/json", // Set content type to JSON
	},
});

// Sends a POST request to create a new user and returns the created user's ID
async function createUser(apiInstance, name, email, password, direction) {
	const body = {
		name: name,
		data: {
			email: email,
			password: password,
			direction: direction,
		},
	};

	try {
		const response = await apiInstance.post("", body);
		logData(response.data); // Log the response data
		return response.data.id; // Return the user ID from response data
	} catch (error) {
		if (error.response) {
			// Mimic fetch error handling
			throw new Error(
				`HTTP error! Status: ${error.response.status}. The user with id ${userId} does not exist`
			);
		} else {
			throw error;
		}
	}
}

// Sends a PATCH request to update a user's email by user ID
async function updateEmail(apiInstance, userId, newEmail) {
	try {
		// Fetch current user data
		const getResponse = await apiInstance.get(`/${userId}`);
		const currentData = getResponse.data;

		// Merge existing data with new email
		const updatedData = {
			...currentData.data,
			email: newEmail,
		};

		// Send PATCH request with merged data
		const response = await apiInstance.patch(`/${userId}`, {
			data: updatedData,
		});

		logData(response.data); // Log the response data
	} catch (error) {
		if (error.response) {
			// Mimic fetch error handling
			throw new Error(
				`HTTP error! Status: ${error.response.status}. The user with id ${userId} does not exist`
			);
		} else {
			throw error;
		}
	}
}

// Logs user data to the console
function logData(data) {
	console.log(`Log of data:`, data);
}

// Example usage: create a user, then update their email, with error handling
(async () => {
	try {
		const userId = await createUser(
			apiInstance,
			"andy",
			"andy41@gmail.com",
			"sabio123",
			"grecia"
		);

		await updateEmail(apiInstance, userId, "newemail@gmail.com");
	} catch (error) {
		console.error("An error occurred:", error.message);
	}
})();
