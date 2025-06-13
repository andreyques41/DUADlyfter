// Create an axios instance for API requests
const apiInstance = axios.create({
	baseURL: `https://api.restful-api.dev/objects`,
	timeout: 5000,
	headers: {
		"Content-Type": "application/json", // Set content type to JSON
	},
});

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
		if (error.response && error.response.status === 404) {
			errorMsg = `User with ID "${userId}" does not exist.`;
		} else if (error.response) {
			errorMsg = `Server responded with status: ${error.response.status}.`;
		} else if (error.message) {
			errorMsg = `There was a problem when trying to login. ${error.message}`;
		} else {
			errorMsg = "There was a problem when trying to login.";
		}
		alert(errorMsg);
	}
}

// Function to check if all form fields are filled
function validateFormFields(form) {
	const userId = form.userId.value.trim();
	const password = form.password.value.trim();
	if (!userId || !password) {
		alert("Please fill in all fields before submitting the form.");
		return false;
	}
	return true;
}

function saveUserData(userId, data) {
	const userData = data.data || {};
	localStorage.setItem("userID", userId);
	localStorage.setItem("userFullName", data.name || "");
	localStorage.setItem("userEmail", userData.email || "");
	localStorage.setItem("userPassword", userData.password || "");
	localStorage.setItem("userDirection", userData.direction || "");
}

// Prefill login form if user data exists in localStorage
document.addEventListener("DOMContentLoaded", function () {
	const userId = localStorage.getItem("userID");
	const userPassword = localStorage.getItem("userPassword");
	if (userId && userPassword) {
		const userIdInput = document.querySelector('input[name="userId"]');
		const passwordInput = document.querySelector('input[name="password"]');
		if (userIdInput) userIdInput.value = userId;
		if (passwordInput) passwordInput.value = userPassword;
	}
});

// Add event listener to the form to handle user login on submit
document
	.getElementById("form-user")
	.addEventListener("submit", async function (event) {
		event.preventDefault();

		const form = event.target;
		if (!validateFormFields(form)) return;

		const userId = form.userId.value;
		const password = form.password.value;

		const data = await loginUser(apiInstance, userId, password);

		if (data) {
			saveUserData(userId, data);
			window.location.href = "../user-profile/user-profile.html";
		}
	});

// Add event listener for the register button to redirect to register.html
document.getElementById("register-btn").addEventListener("click", function () {
	window.location.href = "../register/register.html";
});

document
	.getElementById("changepass-btn")
	.addEventListener("click", function () {
		window.location.href = "../change-password/change-password.html";
	});
