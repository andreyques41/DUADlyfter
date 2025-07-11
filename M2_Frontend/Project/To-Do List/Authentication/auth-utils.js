// --- Authentication Utilities ---
// Shared authentication helper functions to avoid code duplication
console.log("auth-utils.js loaded");

// Create shared API instance for authentication validation
const authApiInstance = axios.create({
	baseURL: `https://api.restful-api.dev/objects`,
	timeout: 5000,
	headers: { "Content-Type": "application/json" },
});

// Session-level authentication cache to prevent redundant API validation calls
const authCache = {
	validatedUsers: new Map(),
	cacheDuration: 60000, // 1 minute cache for auth validation

	isValid(userId) {
		const cached = this.validatedUsers.get(userId);
		return cached && Date.now() - cached.timestamp < this.cacheDuration;
	},

	setValid(userId) {
		this.validatedUsers.set(userId, {
			valid: true,
			timestamp: Date.now(),
		});
		console.log(`authCache: User ${userId} validation cached for 1 minute`);
	},

	isValidCached(userId) {
		if (this.isValid(userId)) {
			console.log(`authCache: Using cached validation for user ${userId}`);
			return true;
		}
		return false;
	},

	clear() {
		this.validatedUsers.clear();
		console.log("authCache: Authentication cache cleared");
	},
};

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

/**
 * Enhanced login user function - validates user credentials against API
 * @param {Object} apiInstance - Axios instance to use
 * @param {string} userId - The user ID
 * @param {string} password - The user's password
 * @param {Object} options - Configuration options
 * @returns {Promise} API response data, true (offline mode), or null (invalid)
 */
async function loginUser(apiInstance, userId, password, options = {}) {
	const {
		returnFullData = true,
		showAlerts = true,
		allowOfflineMode = false,
	} = options;
	console.log("loginUser: Starting login process for userId:", userId);

	try {
		console.log("loginUser: Making API request to get user data");
		const response = await apiInstance.get(`/${userId}`);
		console.log("loginUser: API response received:", response.data);
		const userData = response.data.data;
		console.log("loginUser: Extracted user data:", userData);

		if (!userData || userData.password !== password) {
			console.warn("loginUser: Password validation failed");
			if (showAlerts) alert("Invalid password");
			return null;
		}

		console.log("loginUser: Login successful for user:", userId);
		return returnFullData ? response.data : true;
	} catch (error) {
		console.error("loginUser: Error during login process:", error);

		if (showAlerts) {
			let errorMsg;
			if (error.response && error.response.status === 404)
				errorMsg = `User with ID "${userId}" does not exist.`;
			else if (error.response)
				errorMsg = `Server responded with status: ${error.response.status}.`;
			else if (error.message)
				errorMsg = `There was a problem when trying to login. ${error.message}`;
			else errorMsg = "There was a problem when trying to login.";
			console.error("loginUser: Error message:", errorMsg);
			alert(errorMsg);
		}

		// For validation purposes, distinguish between user not found vs API issues
		if (error.response?.status === 404) {
			return null; // User definitely doesn't exist
		} else {
			// API might be down - for session validation, allow offline mode
			console.warn("loginUser: API unavailable - network/server issue");
			return allowOfflineMode ? true : null;
		}
	}
}

/**
 * Validates user credentials against the API (uses shared loginUser function with caching)
 * @param {string} userId - The user ID to validate
 * @param {string} email - The user's email to validate (for additional verification)
 * @param {string} password - The user's password to validate
 * @returns {Promise<boolean>} True if valid, false otherwise
 */
async function validateUserWithAPI(userId, email, password) {
	// Check cache first
	if (authCache.isValidCached(userId)) {
		return true;
	}

	console.log(
		"validateUserWithAPI: Validating user against API using loginUser..."
	);

	// Use the shared loginUser function with validation-specific options
	const result = await loginUser(authApiInstance, userId, password, {
		returnFullData: true,
		showAlerts: false, // Don't show alerts during session validation
		allowOfflineMode: true, // Allow offline mode for session validation
	});

	if (result === null) {
		// User doesn't exist or invalid credentials
		console.error("validateUserWithAPI: User validation failed");
		return false;
	} else if (result === true) {
		// API is down but allowing offline mode
		console.warn(
			"validateUserWithAPI: API unavailable - allowing offline mode"
		);
		// Cache this validation for offline mode
		authCache.setValid(userId);
		return true;
	} else {
		// Full user data returned - validate email matches for extra security
		const userData = result.data || {};
		const apiEmail = userData.email;

		if (apiEmail === email) {
			console.log(
				"validateUserWithAPI: User validated successfully against API"
			);
			// Cache this successful validation
			authCache.setValid(userId);
			return true;
		} else {
			console.error(
				"validateUserWithAPI: Email mismatch - stored data doesn't match API"
			);
			return false;
		}
	}
}

// Make functions globally available
window.AuthUtils = {
	validateLoginFields,
	validateRegistrationFields,
	validatePasswordChangeFields,
	saveUserDataToStorage,
	updatePasswordInStorage,
	loginUser,
	validateUserWithAPI,
	clearAuthCache: () => authCache.clear(), // Expose cache clearing for logout
};
