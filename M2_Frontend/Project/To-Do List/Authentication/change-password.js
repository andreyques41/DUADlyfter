const apiInstance = axios.create({
	baseURL: `https://api.restful-api.dev/objects`,
	timeout: 5000,
	headers: { "Content-Type": "application/json" },
});

// Check old password and new password match
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

// Change user password via API
async function changePassword(apiInstance, form) {
	try {
		const userId = form.userId.value;
		const getResponse = await apiInstance.get(`/${userId}`);
		const currentData = getResponse.data;
		const oldPassword = form.oldPassword.value;
		const newPassword = form.newPassword.value;
		const confirmNewPassword = form.confirmNewPassword.value;

		// Validate passwords before sending update
		if (
			!checkPasswords(
				oldPassword,
				currentData.data.password,
				newPassword,
				confirmNewPassword
			)
		)
			return false;

		const updatedData = { ...currentData.data, password: newPassword };
		await apiInstance.patch(`/${userId}`, { data: updatedData });
		updateUserData(newPassword);
		return true;
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

// Validate change password form fields before submit
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

// Update password in localStorage
function updateUserData(newPassword) {
	localStorage.setItem("userPassword", newPassword || "");
}

// Attach event listeners after DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
	const form = document.getElementById("form-user");
	const loginBtn = document.getElementById("login-btn");

	// Handle password change form submission
	form.addEventListener("submit", async function (event) {
		event.preventDefault();
		if (!validateFormFields(form)) return;
		const result = await changePassword(apiInstance, form);
		if (!result) return;
		alert("Password was successfully changed!");
		window.location.href = "../user-profile/user-profile.html";
	});

	// Redirect to login page
	loginBtn.addEventListener("click", function () {
		window.location.href = "../Authentication/login.html";
	});

	// Password eye toggle logic for all password fields
	const passwordToggles = [
		{
			input: document.querySelector("#old_password"),
			btn: document.querySelector("#toggle-old-password"),
			icon: document.querySelector("#eye-icon-old"),
		},
		{
			input: document.querySelector("#new_password"),
			btn: document.querySelector("#toggle-new-password"),
			icon: document.querySelector("#eye-icon-new"),
		},
		{
			input: document.querySelector("#confirm_new_password"),
			btn: document.querySelector("#toggle-confirm-password"),
			icon: document.querySelector("#eye-icon-confirm"),
		},
	];

	passwordToggles.forEach(({ input, btn, icon }) => {
		if (btn && input && icon) {
			btn.addEventListener("click", function (e) {
				e.preventDefault();
				const isPassword = input.type === "password";
				input.type = isPassword ? "text" : "password";
				icon.innerHTML = isPassword
					? `<path stroke="#888" stroke-width="2" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12Z"/><circle cx="12" cy="12" r="3.5" stroke="#888" stroke-width="2"/><line x1="5" y1="19" x2="19" y2="5" stroke="#888" stroke-width="2"/>`
					: `<path stroke="#888" stroke-width="2" d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12Z"/><circle cx="12" cy="12" r="3.5" stroke="#888" stroke-width="2"/>`;
			});
		}
	});
});
