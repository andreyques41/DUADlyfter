// Create an axios instance for API requests
const apiInstance = axios.create({
	baseURL: `https://api.restful-api.dev/objects`,
	timeout: 5000,
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
		return response.data.id; // Return the user ID from response data
	} catch (error) {
		let errorMsg = "There was a problem creating the user.";
		if (error.response) {
			errorMsg += ` Server responded with status: ${error.response.status}.`;
		} else if (error.message) {
			errorMsg += ` ${error.message}`;
		}
		alert(errorMsg);
	}
}

// Function to check if all form fields are filled
function validateFormFields(form) {
	const firstName = form.firstName.value.trim();
	const lastName = form.lastName.value.trim();
	const email = form.email.value.trim();
	const password = form.password.value.trim();
	const direction = form.direction.value.trim();

	if (!firstName || !lastName || !email || !password || !direction) {
		alert("Please fill in all fields before submitting the form.");
		return false;
	}
	return true;
}

function saveUserToken(userId, name, email, password, direction) {
	localStorage.setItem("userID", userId);
	localStorage.setItem("userFullName", name);
	localStorage.setItem("userEmail", email);
	localStorage.setItem("userPassword", password);
	localStorage.setItem("userDirection", direction);
}

// Add event listener to the form to handle user registration on submit
document
	.getElementById("form-user")
	.addEventListener("submit", async function (event) {
		event.preventDefault();

		const form = event.target;
		// Validate fields before proceeding
		if (!validateFormFields(form)) {
			return;
		}

		const firstName = form.firstName.value;
		const lastName = form.lastName.value;
		const email = form.email.value;
		const password = form.password.value;
		const direction = form.direction.value;

		// Combine first and last name for the API
		const name = `${firstName} ${lastName}`;

		const userId = await createUser(
			apiInstance,
			name,
			email,
			password,
			direction
		);
		if (userId) {
			alert(`User created successfully! Your ID is: ${userId}`);
			saveUserToken(userId, name, email, password, direction);
			window.location.href = "user-profile.html";
		}
	});
