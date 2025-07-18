const apiInstance = axios.create({
	baseURL: `https://api.restful-api.dev/objects`,
	timeout: 5000,
	headers: { "Content-Type": "application/json" },
});

// Create user via API, return user ID
async function createUser(apiInstance, name, email, password, direction) {
	const body = {
		name,
		data: { email, password, direction },
	};
	try {
		const response = await apiInstance.post("", body);
		return response.data.id;
	} catch (error) {
		let errorMsg = "There was a problem creating the user.";
		if (error.response)
			errorMsg += ` Server responded with status: ${error.response.status}.`;
		else if (error.message) errorMsg += ` ${error.message}`;
		alert(errorMsg);
	}
}

// Validate all form fields before submit
function validateFormFields(form) {
	const { firstName, lastName, email, password, direction } = form;
	if (
		!firstName.value.trim() ||
		!lastName.value.trim() ||
		!email.value.trim() ||
		!password.value.trim() ||
		!direction.value.trim()
	) {
		alert("Please fill in all fields before submitting the form.");
		return false;
	}
	return true;
}

// Save user data to localStorage for session persistence
function saveUserData(userId, name, email, password, direction) {
	localStorage.setItem("userID", userId);
	localStorage.setItem("userFullName", name);
	localStorage.setItem("userEmail", email);
	localStorage.setItem("userPassword", password);
	localStorage.setItem("userDirection", direction);
}

// Register form submit handler
document.addEventListener("DOMContentLoaded", () => {
	const form = document.getElementById("form-user");
	const loginBtn = document.getElementById("login-btn");

	// Handle registration form submission
	form.addEventListener("submit", async function (event) {
		event.preventDefault();
		if (!validateFormFields(form)) return;
		const { firstName, lastName, email, password, direction } = form;
		const name = `${firstName.value} ${lastName.value}`;
		const userId = await createUser(
			apiInstance,
			name,
			email.value,
			password.value,
			direction.value
		);
		if (userId) {
			alert(`User created successfully! Your ID is: ${userId}`);
			saveUserData(userId, name, email.value, password.value, direction.value);
			window.location.href = "../user-profile/user-profile.html";
		}
	});

	// Redirect to login page
	loginBtn.addEventListener("click", () => {
		window.location.href = "../login/login.html";
	});
});
