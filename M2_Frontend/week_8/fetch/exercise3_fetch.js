// Fetch and log user by ID from API
async function getUser(url, userId) {
	// Remove any trailing slash from the URL to avoid double slashes
	const cleanUrl = url.replace(/\/+$/, "");

	const requestOptions = {
		method: "GET", // HTTP GET method
		mode: "cors", // Allow cross-origin requests
		cache: "no-cache", // Prevent caching
		credentials: "same-origin", // Send credentials for same-origin
		headers: {
			"Content-Type": "application/json", // Expect JSON response
		},
		redirect: "follow", // Follow HTTP redirects
		referrerPolicy: "no-referrer", // Do not send referrer info
	};

	// Fetch user data from API
	const response = await fetch(`${cleanUrl}/${userId}`, requestOptions);

	// Throw error if response is not OK
	if (!response.ok) {
		throw new Error(
			`HTTP error! Status: ${response.status}. The user with id ${userId} does not exist`
		);
	}

	// Parse and log the user data
	await logUser(response);
}

// Parse and log user data
async function logUser(response) {
	const data = await response.json();
	console.log(`Log of data:`, data);
}

// Example usage with error handling
(async () => {
	try {
		await getUser("https://api.restful-api.dev/objects", 2);
		await getUser("https://api.restful-api.dev/objects", 25);
	} catch (error) {
		console.error(error.message);
	}
})();
