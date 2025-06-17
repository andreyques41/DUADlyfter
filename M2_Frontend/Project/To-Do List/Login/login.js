const apiInstance = axios.create({
	baseURL: `https://api.restful-api.dev/objects`,
	timeout: 5000,
	headers: { "Content-Type": "application/json" },
});

// Login user by ID and password
async function loginUser(apiInstance, userId, password) {
	try {
		const response = await apiInstance.get(`/${userId}`);
		const userData = response.data.data;
		if (!userData || userData.password !== password) {
			alert("Invalid password");
			return null;
		}
		return response.data;
	} catch (error) {
		let errorMsg;
		if (error.response && error.response.status === 404)
			errorMsg = `User with ID "${userId}" does not exist.`;
		else if (error.response)
			errorMsg = `Server responded with status: ${error.response.status}.`;
		else if (error.message)
			errorMsg = `There was a problem when trying to login. ${error.message}`;
		else errorMsg = "There was a problem when trying to login.";
		alert(errorMsg);
	}
}

// Validate login form fields before submit
function validateFormFields(form) {
	const userId = form.userId.value.trim();
	const password = form.password.value.trim();
	if (!userId || !password) {
		alert("Please fill in all fields before submitting the form.");
		return false;
	}
	return true;
}

// Save user data to localStorage for session persistence
function saveUserData(userId, data) {
	const userData = data.data || {};
	localStorage.setItem("userID", userId);
	localStorage.setItem("userFullName", data.name || "");
	localStorage.setItem("userEmail", userData.email || "");
	localStorage.setItem("userPassword", userData.password || "");
	localStorage.setItem("userDirection", userData.direction || "");
}

// Prefill login form if data exists in localStorage
document.addEventListener("DOMContentLoaded", function () {
	const userId = localStorage.getItem("userID");
	const userPassword = localStorage.getItem("userPassword");
	const userIdInput = document.querySelector('input[name="userId"]');
	const passwordInput = document.querySelector('input[name="password"]');
	if (userId && userPassword) {
		if (userIdInput) userIdInput.value = userId;
		if (passwordInput) passwordInput.value = userPassword;
	}

	const form = document.getElementById("form-user");
	const registerBtn = document.getElementById("register-btn");
	const changePassBtn = document.getElementById("change-password-btn"); // correct id

	// Handle login form submission
	form.addEventListener("submit", async function (event) {
		event.preventDefault();
		if (!validateFormFields(form)) return;
		const userId = form.userId.value;
		const password = form.password.value;
		const data = await loginUser(apiInstance, userId, password);
		if (data) {
			saveUserData(userId, data);
			window.location.href = "../user-profile/user-profile.html";
		}
	});

	// Redirect to register page
	registerBtn.addEventListener("click", function () {
		window.location.href = "../register/register.html";
	});
	// Redirect to change password page
	changePassBtn.addEventListener("click", function () {
		window.location.href = "../Login/change-password.html";
	});

	// Password eye toggle logic
	// Use querySelector to ensure you get the correct elements even if there are multiple forms or elements
	const passwordInputField = document.querySelector("#password");
	const toggleBtn = document.querySelector("#toggle-password");
	const eyeIcon = document.querySelector("#eye-icon");

	if (toggleBtn && passwordInputField && eyeIcon) {
		toggleBtn.addEventListener("click", function (e) {
			e.preventDefault(); // Prevent form submission or focus loss
			const isPassword = passwordInputField.type === "password";
			passwordInputField.type = isPassword ? "text" : "password";
			eyeIcon.innerHTML = isPassword
				? `<path stroke="#888" stroke-width="2" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12Z"/><circle cx="12" cy="12" r="3.5" stroke="#888" stroke-width="2"/><line x1="5" y1="19" x2="19" y2="5" stroke="#888" stroke-width="2"/>`
				: `<path stroke="#888" stroke-width="2" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12Z"/><circle cx="12" cy="12" r="3.5" stroke="#888" stroke-width="2"/>`;
		});
	}
});
