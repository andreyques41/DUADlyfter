const apiInstance = axios.create({
	baseURL: `https://api.restful-api.dev/objects`,
	timeout: 5000,
	headers: { "Content-Type": "application/json" },
});

// Create user via API, return user ID
async function createUser(apiInstance, name, email, password) {
	console.log("createUser: Creating user:", name);
	
	const body = {
		name,
		data: { email, password },
	};
	
	try {
		const response = await apiInstance.post("", body);
		console.log("createUser: Success! User ID:", response.data.id);
		return response.data.id;
	} catch (error) {
		console.error("createUser: Error:", error);
		let errorMsg = "There was a problem creating the user.";
		if (error.response) {
			console.error("createUser: Server response error:", error.response);
			errorMsg += ` Server responded with status: ${error.response.status}.`;
		} else if (error.message) {
			console.error("createUser: Error message:", error.message);
			errorMsg += ` ${error.message}`;
		}
		alert(errorMsg);
	}
}

// Validate all form fields before submit
function validateFormFields(form) {
	const { firstName, lastName, email, password } = form;
	
	if (
		!firstName.value.trim() ||
		!lastName.value.trim() ||
		!email.value.trim() ||
		!password.value.trim()
	) {
		console.warn("validateFormFields: Empty fields detected");
		alert("Please fill in all fields before submitting the form.");
		return false;
	}
	console.log("validateFormFields: All fields valid");
	return true;
}

// Save user data to localStorage for session persistence
function saveUserData(userId, name, email, password) {
	localStorage.setItem("userID", userId);
	localStorage.setItem("userFullName", name);
	localStorage.setItem("userEmail", email);
	localStorage.setItem("userPassword", password);
	
	console.log("saveUserData: User data saved to localStorage");
}

// Register form submit handler
document.addEventListener("DOMContentLoaded", () => {
	console.log("Registration form setup started");
	
	const form = document.getElementById("form-user");
	const loginBtn = document.getElementById("login-btn");

	// Handle registration form submission
	form.addEventListener("submit", async function (event) {
		console.log("Form submitted");
		event.preventDefault();
		
		if (!validateFormFields(form)) return;
		
		const { firstName, lastName, email, password } = form;
		const name = `${firstName.value} ${lastName.value}`;
		
		const userId = await createUser(
			apiInstance,
			name,
			email.value,
			password.value
		);
		
		if (userId) {
			alert(`User created successfully! Your ID is: ${userId}`);
			saveUserData(userId, name, email.value, password.value);
			console.log("Redirecting to main page...");
			window.location.href = "../Main/main.html";
		} else {
			console.error("User creation failed - no userId returned");
		}
	});

	// Redirect to login page
	loginBtn.addEventListener("click", () => {
		console.log("Redirecting to login page...");
		window.location.href = "../Authentication/login.html";
	});

	// Password eye toggle logic
	const passwordInputField = document.querySelector("#password");
	const toggleBtn = document.querySelector("#toggle-password");
	const eyeIcon = document.querySelector("#eye-icon");

	if (toggleBtn && passwordInputField && eyeIcon) {
		toggleBtn.addEventListener("click", function (e) {
			e.preventDefault();
			const isPassword = passwordInputField.type === "password";
			passwordInputField.type = isPassword ? "text" : "password";
			eyeIcon.innerHTML = isPassword
				? `<path stroke="#888" stroke-width="2" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12Z"/><circle cx="12" cy="12" r="3.5" stroke="#888" stroke-width="2"/><line x1="5" y1="19" x2="19" y2="5" stroke="#888" stroke-width="2"/>`
				: `<path stroke="#888" stroke-width="2" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12Z"/><circle cx="12" cy="12" r="3.5" stroke="#888" stroke-width="2"/>`;
		});
	} else {
		console.warn("Password toggle elements not found");
	}
});
