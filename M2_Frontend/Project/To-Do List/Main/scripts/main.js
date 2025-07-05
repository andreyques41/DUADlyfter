// --- App Initialization and User Session ---
// Main entry point: initializes app, sets up user session, and wires up UI
console.log("main.js loaded");

function logOffUser() {
	console.log("logOffUser: Logging off user and clearing session data");
	localStorage.removeItem("userID");
	localStorage.removeItem("userFullName");
	localStorage.removeItem("userEmail");
	localStorage.removeItem("userPassword");
	localStorage.removeItem("userDirection");
	window.location.href = "../Authentication/login.html";
}


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
