// --- Authentication Utilities ---
// Shared authentication helper functions to avoid code duplication
console.log("auth-utils.js loaded");

/**
 * Validates login form fields (userId and password)
 * @param {HTMLFormElement} form - The login form
 * @returns {boolean} - True if validation passes
 */
function validateLoginFields(form) {
	const userId = form.userId.value.trim();
	const password = form.password.value.trim();
	console.log("validateLoginFields: Validating form fields", {
		userId: userId || "empty",
		password: password ? "***" : "empty",
	});

	if (!userId || !password) {
		console.warn("validateLoginFields: Validation failed - missing fields");
		alert("Please fill in all fields before submitting the form.");
		return false;
	}

	console.log("validateLoginFields: Form validation passed");
	return true;
}

/**
 * Validates registration form fields (firstName, lastName, email, password)
 * @param {HTMLFormElement} form - The registration form
 * @returns {boolean} - True if validation passes
 */
function validateRegistrationFields(form) {
	const { firstName, lastName, email, password } = form;

	if (
		!firstName.value.trim() ||
		!lastName.value.trim() ||
		!email.value.trim() ||
		!password.value.trim()
	) {
		console.warn("validateRegistrationFields: Empty fields detected");
		alert("Please fill in all fields before submitting the form.");
		return false;
	}

	console.log("validateRegistrationFields: All fields valid");
	return true;
}

/**
 * Validates change password form fields (oldPassword, newPassword, confirmNewPassword)
 * @param {HTMLFormElement} form - The change password form
 * @returns {boolean} - True if validation passes
 */
function validatePasswordChangeFields(form) {
	const oldPassword = form.oldPassword?.value?.trim() || "";
	const newPassword = form.newPassword?.value?.trim() || "";
	const confirmNewPassword = form.confirmNewPassword?.value?.trim() || "";

	if (!oldPassword || !newPassword || !confirmNewPassword) {
		console.warn(
			"validatePasswordChangeFields: Form validation failed - empty fields"
		);
		alert("Please fill in all fields before submitting the form.");
		return false;
	}

	console.log("validatePasswordChangeFields: Form validation passed");
	return true;
}

/**
 * Save user data to localStorage for session persistence
 * @param {string} userId - The user ID
 * @param {string} fullName - The user's full name
 * @param {string} email - The user's email
 * @param {string} password - The user's password
 */
function saveUserDataToStorage(userId, fullName, email, password) {
	try {
		localStorage.setItem("userID", userId || "");
		localStorage.setItem("userFullName", fullName || "");
		localStorage.setItem("userEmail", email || "");
		localStorage.setItem("userPassword", password || "");

		console.log("saveUserDataToStorage: User data saved to localStorage", {
			userId: userId || "empty",
			fullName: fullName || "empty",
			email: email || "empty",
			password: password ? "***" : "empty",
		});
	} catch (error) {
		console.error(
			"saveUserDataToStorage: Error saving to localStorage:",
			error
		);
	}
}

/**
 * Update password in localStorage
 * @param {string} newPassword - The new password to save
 */
function updatePasswordInStorage(newPassword) {
	try {
		localStorage.setItem("userPassword", newPassword || "");
		console.log("updatePasswordInStorage: Password updated in localStorage");
	} catch (error) {
		console.error(
			"updatePasswordInStorage: Error updating localStorage:",
			error
		);
	}
}

// Make functions globally available
window.AuthUtils = {
	validateLoginFields,
	validateRegistrationFields,
	validatePasswordChangeFields,
	saveUserDataToStorage,
	updatePasswordInStorage,
};
