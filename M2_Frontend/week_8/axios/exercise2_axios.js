const axios = require("axios");

// Create an axios instance for API requests
const apiInstance = axios.create({
	baseURL: `https://api.restful-api.dev/objects`,
	timeout: 1000,
	headers: {
		"Content-Type": "application/json", // Set content type to JSON
	},
});

// Sends a POST request to create a new user
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

// Call the function to execute the fetch and log process
(async () => {
	try {
		const userId = await createUser(
			apiInstance,
			"andy",
			"andy41@gmail.com",
			"sabio123",
			"grecia"
		);
	} catch (error) {
		console.error("An error occurred:", error.message);
	}
})();
