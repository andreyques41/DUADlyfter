// --- User Session Management ---
// Handles user authentication and session management
console.log("user-session.js loaded");

const UserSession = {
    // Check if user is logged in (comprehensive check)
    isLoggedIn() {
        const userId = localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_ID);
        const userFullName = localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_FULL_NAME);
        const userEmail = localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_EMAIL);
        const userPassword = localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_PASSWORD);
        
        console.log("UserSession.isLoggedIn: Checking user session...");
        console.log("UserSession.isLoggedIn: User data from localStorage:", {
            userId,
            userFullName,
            userEmail,
            userPassword: userPassword ? "***" : null,
        });

        const isValid = !!(userId && userFullName && userEmail && userPassword);
        
        if (!isValid) {
            console.warn("UserSession.isLoggedIn: User not logged in - missing data:");
            console.log("UserSession.isLoggedIn: Missing data - userId:", !!userId, "userFullName:", !!userFullName, "userEmail:", !!userEmail, "userPassword:", !!userPassword);
        } else {
            console.log("UserSession.isLoggedIn: User is logged in successfully");
        }
        
        return isValid;
    },

    // Check login and redirect if not logged in (blocking check)
    checkUserLoggedInOrRedirect() {
        console.log("UserSession.checkUserLoggedInOrRedirect: Running user session check...");
        
        if (!this.isLoggedIn()) {
            console.warn("UserSession.checkUserLoggedInOrRedirect: User not logged in, redirecting to login.html");
            window.location.href = "../Authentication/login.html";
            return false; // Prevent further execution
        }
        
        console.log("UserSession.checkUserLoggedInOrRedirect: User session validated");
        return true;
    },

    // Get current user info
    getCurrentUser() {
        const user = {
            id: localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_ID),
            fullName: localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_FULL_NAME),
            email: localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_EMAIL),
            direction: localStorage.getItem(APP_CONFIG.STORAGE_KEYS.USER_DIRECTION)
        };
        
        console.log("UserSession.getCurrentUser: Retrieved user info", user.fullName);
        return user;
    },

    // Log out user
    logout() {
        console.log("UserSession.logout: Starting user logout process");
        try {
            // Clear all user-related data
            Object.values(APP_CONFIG.STORAGE_KEYS).forEach(key => {
                if (key.startsWith('user') || key.includes('user')) {
                    localStorage.removeItem(key);
                }
            });

            // Clear specific session data
            localStorage.removeItem(APP_CONFIG.STORAGE_KEYS.USER_ID);
            localStorage.removeItem(APP_CONFIG.STORAGE_KEYS.USER_FULL_NAME);
            localStorage.removeItem(APP_CONFIG.STORAGE_KEYS.USER_EMAIL);
            localStorage.removeItem(APP_CONFIG.STORAGE_KEYS.USER_PASSWORD);
            localStorage.removeItem(APP_CONFIG.STORAGE_KEYS.USER_DIRECTION);

            console.log("UserSession.logout: Session data cleared successfully");
            
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
        console.log(`UserSession.init: Session initialized for user: ${user.fullName}`);
        
        // Set up logout button
        const signoutBtn = document.getElementById("signout-btn");
        if (signoutBtn) {
            signoutBtn.addEventListener("click", this.logout.bind(this));
            console.log("UserSession.init: Logout button configured");
        }

        return true;
    }
};

// Expose globally
window.UserSession = UserSession;

// Legacy compatibility
window.logOffUser = UserSession.logout;
window.checkUserLoggedIn = UserSession.checkUserLoggedInOrRedirect;

// Immediately check user session when this script loads (replaces checklogin.js functionality)
console.log("user-session.js: Running immediate user session check...");
UserSession.checkUserLoggedInOrRedirect();

console.log("user-session.js: User session management loaded");
