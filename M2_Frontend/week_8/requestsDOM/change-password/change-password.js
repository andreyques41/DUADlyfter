// Create an axios instance for API requests
const apiInstance = axios.create({
	baseURL: `https://api.restful-api.dev/objects`,
	timeout: 5000,
	headers: {
		"Content-Type": "application/json", // Set content type to JSON
	},
});

// Function to check if old password is correct and if new password and confirmation match
function checkPasswords(
	oldPassword,
	currentPassword,
	newPassword,
	confirmNewPassword
) {
	if (oldPassword !== currentPassword) {
		alert("The old password is not correct");
		return false;
	}
	if (newPassword !== confirmNewPassword) {
		alert("The new password and its confirmation should match");
		return false;
	}
	return true;
}

// Sends a PATCH request to update a user's password by user ID
async function changePassword(apiInstance, form) {
	try {
		const userId = form.userId.value; // Get user ID from form input
		// Fetch current user data
		const getResponse = await apiInstance.get(`/${userId}`);
		const currentData = getResponse.data;

		const oldPassword = form.oldPassword.value;
		const newPassword = form.newPassword.value;
		const confirmNewPassword = form.confirmNewPassword.value;

		if (
			!checkPasswords(
				oldPassword,
				currentData.data.password,
				newPassword,
				confirmNewPassword
			)
		) {
			return false;
		}

		// Merge existing data with new password, keep other fields (like email, direction)
		const updatedData = {
			...currentData.data,
			password: newPassword,
		};

		// Send PATCH request with merged data
		const response = await apiInstance.patch(`/${userId}`, {
			data: updatedData,
		});

		updateUserData(newPassword);
		return true;
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
	const oldPassword = form.oldPassword.value.trim();
	const newPassword = form.newPassword.value.trim();
	const confirmNewPassword = form.confirmNewPassword.value.trim();
	if (!oldPassword || !newPassword || !confirmNewPassword) {
		alert("Please fill in all fields before submitting the form.");
		return false;
	}
	return true;
}

function updateUserData(newPassword) {
	localStorage.setItem("userPassword", newPassword || "");
}

// Add event listener to the form to handle user login on submit
document
	.getElementById("form-user")
	.addEventListener("submit", async function (event) {
		event.preventDefault();

		console.log("Form submitted"); // Debug: confirm handler is firing

		const form = event.target;
		if (!validateFormFields(form)) return;

		const result = await changePassword(apiInstance, form);
		if (!result) return;
		alert("Password was successfully changed!");
		window.location.href = "../user-profile/user-profile.html";
	});

// Add event listener for the login button to redirect to login.html
document.getElementById("login-btn").addEventListener("click", function () {
	window.location.href = "../login/login.html";
});
