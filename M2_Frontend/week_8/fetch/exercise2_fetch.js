// Send POST request to create a user
async function createUser(name, email, password, direction, url) {
	const body = {
		name: name,
		data: {
			email: email,
			password: password,
			direction: direction,
		},
	};

	const requestOptions = {
		method: "POST", // HTTP method
		mode: "cors", // Cross-origin requests
		cache: "no-cache", // Prevent caching
		credentials: "same-origin", // Include credentials for same-origin
		headers: {
			"Content-Type": "application/json", // Set content type to JSON
		},
		redirect: "follow", // Follow redirects
		referrerPolicy: "no-referrer", // No referrer info
		body: JSON.stringify(body), // Stringify body for JSON
	};

	const response = await fetch(url, requestOptions);
	if (!response.ok) {
		throw new Error(`HTTP error! status: ${response.status}`);
	}

	logData(response);
}

// Parse and log server response
async function logData(response) {
	const data = await response.json();
	console.log(`Log of data:`, data);
}

// Example usage with error handling
(async () => {
	try {
		await createUser(
			"andy",
			"andy41@gmail.com",
			"sabio123",
			"grecia",
			"https://api.restful-api.dev/objects"
		);
	} catch (error) {
		console.error(error.message);
	}
})();
