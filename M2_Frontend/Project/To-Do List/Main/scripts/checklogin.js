// --- User session and profile helpers ---
function checkUserLoggedIn() {
	const userId = localStorage.getItem("userID");
	const userFullName = localStorage.getItem("userFullName");
	const userEmail = localStorage.getItem("userEmail");
	const userDirection = localStorage.getItem("userDirection");
	console.log("checkUserLoggedIn: Checking user session...");
	if (!userId || !userFullName || !userEmail || !userDirection) {
		console.warn(
			"checkUserLoggedIn: User not logged in, redirecting to login.html"
		);
		window.location.href = "../Authentication/login.html";
		return false; // Prevent further execution
	}
	return true; // User is logged in
}

// User session and profile - run immediately
checkUserLoggedIn();