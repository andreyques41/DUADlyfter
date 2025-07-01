// --- App Initialization and User Session ---
// Main entry point: initializes app, sets up user session, and wires up UI
console.log("main.js loaded");

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
	}
}
function logOffUser() {
	console.log("logOffUser: Logging off user and clearing session data");
	localStorage.removeItem("userID");
	localStorage.removeItem("userFullName");
	localStorage.removeItem("userEmail");
	localStorage.removeItem("userPassword");
	localStorage.removeItem("userDirection");
	window.location.href = "../Authentication/login.html";
}

// User session and profile
checkUserLoggedIn();
console.log("Attaching signout-btn event listener");
document.getElementById("signout-btn").addEventListener("click", logOffUser);

// App setup
console.log("App setup: Populating categories and rendering all sections");
populateAllCategoryDropdowns();
renderSectionTasks("today");
renderSectionTasks("upcoming-today");
renderSectionTasks("tomorrow");
renderSectionTasks("thisweek");
setupTaskSidebar("add");
setupTaskSidebar("edit");
