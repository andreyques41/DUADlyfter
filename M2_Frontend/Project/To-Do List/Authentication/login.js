const apiInstance = axios.create({
	baseURL: `https://api.restful-api.dev/objects`,
	timeout: 5000,
	headers: { "Content-Type": "application/json" },
});

// Note: loginUser function is now in auth-utils.js to avoid duplication
// Using AuthUtils.loginUser for consistency across all authentication modules

// Note: Using shared authentication utilities from auth-utils.js
// validateFormFields -> AuthUtils.validateLoginFields
// saveUserData -> AuthUtils.saveUserDataToStorage

// Prefill login form if data exists in localStorage
console.log("login.js loaded");
document.addEventListener("DOMContentLoaded", function () {
	const userId = localStorage.getItem("userID");
	const userPassword = localStorage.getItem("userPassword");
	const userIdInput = document.querySelector('input[name="userId"]');
	const passwordInput = document.querySelector('input[name="password"]');
	console.log("Prefilling login form", { userId, userPassword });
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
		console.log("Login form submitted");
		if (!AuthUtils.validateLoginFields(form)) return;
		const userId = form.userId.value;
		const password = form.password.value;
		console.log("Attempting login for user:", userId);
		const data = await AuthUtils.loginUser(apiInstance, userId, password);
		if (data) {
			const userData = data.data || {};
			AuthUtils.saveUserDataToStorage(
				userId,
				data.name || "",
				userData.email || "",
				userData.password || ""
			);
			console.log("Login successful, redirecting to main.html");
			window.location.href = "../Main/main.html";
		} else {
			console.log("Login failed for user:", userId);
		}
	});

	// Redirect to register page
	registerBtn.addEventListener("click", function () {
		console.log("Redirecting to register.html");
		window.location.href = "../Authentication/register.html";
	});
	// Redirect to change password page
	changePassBtn.addEventListener("click", function () {
		console.log("Redirecting to change-password.html");
		window.location.href = "../Authentication/change-password.html";
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
			console.log("Toggling password visibility. Was password:", isPassword);
			passwordInputField.type = isPassword ? "text" : "password";
			eyeIcon.innerHTML = isPassword
				? `<path stroke="#888" stroke-width="2" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12Z"/><circle cx="12" cy="12" r="3.5" stroke="#888" stroke-width="2"/><line x1="5" y1="19" x2="19" y2="5" stroke="#888" stroke-width="2"/>`
				: `<path stroke="#888" stroke-width="2" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12Z"/><circle cx="12" cy="12" r="3.5" stroke="#888" stroke-width="2"/>`;
		});
	}
});
