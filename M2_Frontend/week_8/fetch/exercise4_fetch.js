// Send POST request to create user and return user ID
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
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(body),
	};

	const response = await fetch(url, requestOptions);
	if (!response.ok) {
		throw new Error(
			`Failed to create user. HTTP status: ${response.status} (${response.statusText})`
		);
	}

	const data = await response.json();
	logUser(data);
	return data.id;
}

// Send PATCH request to update user's email by ID
async function updateEmail(url, userId, newEmail) {
	const cleanUrl = url.replace(/\/+$/, "");

	// Fetch current user data
	const getResponse = await fetch(`${cleanUrl}/${userId}`);
	if (!getResponse.ok) {
		throw new Error(
			`Failed to fetch user ${userId}. HTTP status: ${getResponse.status} (${getResponse.statusText})`
		);
	}
	const currentData = await getResponse.json();

	// Merge existing data with new email
	const updatedData = {
		...currentData.data,
		email: newEmail,
	};

	const requestOptions = {
		method: "PATCH",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({ data: updatedData }),
	};

	const response = await fetch(`${cleanUrl}/${userId}`, requestOptions);

	if (!response.ok) {
		throw new Error(
			`Failed to update email for user ${userId}. HTTP status: ${response.status} (${response.statusText})`
		);
	}

	const data = await response.json();
	logUser(data);
}

// Log user data
function logUser(data) {
	console.log("Log of data:", data);
}

// Example usage with error handling
(async () => {
	try {
		const userId = await createUser(
			"andy",
			"andy41@gmail.com",
			"sabio123",
			"grecia",
			"https://api.restful-api.dev/objects"
		);

		await updateEmail(
			"https://api.restful-api.dev/objects",
			userId,
			"newemail@gmail.com"
		);
	} catch (error) {
		console.error("An error occurred:", error.message);
	}
})();
