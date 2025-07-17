// --- User Session Management ---
// Handles user authentication and session management
console.log("user-session.js loaded");

const UserSession = {
	// Check if user is logged in (comprehensive check with API validation)
	async isLoggedIn() {
		const userId = localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_ID);
		const userFullName = localStorage.getItem(
			APP_CONFIG.STORAGE_KEYS.USER_FULL_NAME
		);
		const userEmail = localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_EMAIL);
		const userPassword = localStorage.getItem(
			APP_CONFIG.STORAGE_KEYS.USER_PASSWORD
		);

		console.log("UserSession.isLoggedIn: Checking user session...");
		console.log("UserSession.isLoggedIn: User data from localStorage:", {
			userId,
			userFullName,
			userEmail,
			userPassword: userPassword ? "***" : null,
		});

		// First check if localStorage data exists
		const hasLocalData = !!(
			userId &&
			userFullName &&
			userEmail &&
			userPassword
		);

		if (!hasLocalData) {
			console.warn(
				"UserSession.isLoggedIn: User not logged in - missing data:"
			);
			console.log(
				"UserSession.isLoggedIn: Missing data - userId:",
				!!userId,
				"userFullName:",
				!!userFullName,
				"userEmail:",
				!!userEmail,
				"userPassword:",
				!!userPassword
			);
			return false;
		}

		// Validate against API using shared auth utils
		if (window.AuthUtils && window.AuthUtils.validateUserWithAPI) {
			const isValidWithAPI = await window.AuthUtils.validateUserWithAPI(
				userId,
				userEmail,
				userPassword
			);

			if (!isValidWithAPI) {
				console.error(
					"UserSession.isLoggedIn: API validation failed - clearing invalid session"
				);
				this.clearInvalidSession();
				return false;
			}
		} else {
			console.warn(
				"UserSession.isLoggedIn: AuthUtils not available - proceeding with local validation only"
			);
		}

		console.log("UserSession.isLoggedIn: User is logged in successfully");
		return true;
	},

	// Clear invalid session data
	clearInvalidSession() {
		console.log(
			"UserSession.clearInvalidSession: Clearing invalid session data"
		);
		try {
			Object.values(APP_CONFIG.STORAGE_KEYS).forEach((key) => {
				localStorage.removeItem(key);
			});
			localStorage.clear();
		} catch (error) {
			console.error(
				"UserSession.clearInvalidSession: Error clearing session:",
				error
			);
		}
	},

	// Check login and redirect if not logged in (blocking check)
	async checkUserLoggedInOrRedirect() {
		console.log(
			"UserSession.checkUserLoggedInOrRedirect: Running user session check..."
		);

		const isValid = await this.isLoggedIn();

		if (!isValid) {
			console.warn(
				"UserSession.checkUserLoggedInOrRedirect: Invalid session, redirecting to login"
			);
			window.location.href = "../Authentication/login.html";
			return false; // Prevent further execution
		}

		console.log(
			"UserSession.checkUserLoggedInOrRedirect: User session validated"
		);
		return true;
	},

	// Get current user info
	getCurrentUser() {
		const user = {
			id: localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_ID),
			fullName: localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_FULL_NAME),
			email: localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_EMAIL),
		};

		console.log(
			"UserSession.getCurrentUser: Retrieved user info",
			user.fullName
		);
		return user;
	},

	// Log out user
	logout() {
		console.log("UserSession.logout: Starting user logout process");
		try {
			// Clear session caches before clearing localStorage
			if (window.AuthUtils && window.AuthUtils.clearAuthCache) {
				window.AuthUtils.clearAuthCache();
			}
			if (window.clearAPICache) {
				window.clearAPICache();
			}

			// Clear ALL application data from localStorage
			Object.values(APP_CONFIG.STORAGE_KEYS).forEach((key) => {
				localStorage.removeItem(key);
				console.log(`UserSession.logout: Removed ${key} from localStorage`);
			});

			// Also clear any other potential data by clearing everything
			// (this ensures we don't miss anything)
			localStorage.clear();

			console.log(
				"UserSession.logout: All localStorage data and session caches cleared successfully"
			);

			// Redirect to login page
			window.location.href = "../Authentication/login.html";
		} catch (error) {
			console.error("UserSession.logout: Error during logout:", error);
			// Still try to redirect even if there's an error
			window.location.href = "../Authentication/login.html";
		}
	},

	// Initialize user session (call on app start)
	async init() {
		console.log("UserSession.init: Initializing user session");

		const isValid = await this.isLoggedIn();
		if (!isValid) {
			console.warn("UserSession.init: No valid session found");
			return false;
		}

		const user = this.getCurrentUser();
		console.log(
			`UserSession.init: Session initialized for user: ${user.fullName}`
		);

		return true;
	},
};

// Expose globally
window.UserSession = UserSession;

// Set up logout button when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
	const signoutBtn = document.getElementById("signout-btn");
	if (signoutBtn) {
		signoutBtn.addEventListener("click", () => UserSession.logout());
		console.log("UserSession: Logout button configured");
	} else {
		console.warn("UserSession: Logout button not found in DOM");
	}
});

// Immediately check user session when this script loads (replaces checklogin.js functionality)
(async () => {
	console.log("user-session.js: Running immediate user session check...");
	if (await UserSession.checkUserLoggedInOrRedirect()) {
		// Only initialize if user is logged in
		await UserSession.init();
	}
})();

console.log("user-session.js: User session management loaded");
