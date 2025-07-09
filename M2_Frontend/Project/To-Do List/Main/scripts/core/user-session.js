// --- User Session Management ---
// Handles user authentication and session management
console.log("user-session.js loaded");

const UserSession = {
	// Check if user is logged in (comprehensive check)
	isLoggedIn() {
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

		const isValid = !!(userId && userFullName && userEmail && userPassword);

		if (!isValid) {
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
		} else {
			console.log("UserSession.isLoggedIn: User is logged in successfully");
		}

		return isValid;
	},

	// Check login and redirect if not logged in (blocking check)
	checkUserLoggedInOrRedirect() {
		console.log(
			"UserSession.checkUserLoggedInOrRedirect: Running user session check..."
		);

		if (!this.isLoggedIn()) {
			console.warn(
				"UserSession.checkUserLoggedInOrRedirect: User not logged in, redirecting to login.html"
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
			// Clear ALL application data from localStorage
			Object.values(APP_CONFIG.STORAGE_KEYS).forEach((key) => {
				localStorage.removeItem(key);
				console.log(`UserSession.logout: Removed ${key} from localStorage`);
			});

			// Also clear any other potential data by clearing everything
			// (this ensures we don't miss anything)
			localStorage.clear();

			console.log("UserSession.logout: All localStorage data cleared successfully");

			// Redirect to login page
			window.location.href = "../Authentication/login.html";
		} catch (error) {
			console.error("UserSession.logout: Error during logout:", error);
			// Still try to redirect even if there's an error
			window.location.href = "../Authentication/login.html";
		}
	},

	// Initialize user session (call on app start)
	init() {
		console.log("UserSession.init: Initializing user session");

		if (!this.isLoggedIn()) {
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
console.log("user-session.js: Running immediate user session check...");
if (UserSession.checkUserLoggedInOrRedirect()) {
	// Only initialize if user is logged in
	UserSession.init();
}

console.log("user-session.js: User session management loaded");
