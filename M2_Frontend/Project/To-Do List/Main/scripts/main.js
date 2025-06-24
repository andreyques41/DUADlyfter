console.log("main.js loaded");
// Fill user profile card with stored data
function updateUserCard() {
	console.log("updateUserCard called");
	document.getElementById("card-fullname").textContent =
		localStorage.getItem("userFullName") || "";
	document.getElementById("card-email").textContent =
		localStorage.getItem("userEmail") || "";
	document.getElementById("card-direction").textContent =
		localStorage.getItem("userDirection") || "";
}

// Log off user and clear localStorage/session
function logOffUser() {
	console.log("logOffUser called");
	localStorage.removeItem("userID");
	localStorage.removeItem("userFullName");
	localStorage.removeItem("userEmail");
	localStorage.removeItem("userPassword");
	localStorage.removeItem("userDirection");
	window.location.href = "../Authentication/login.html";
}

// Redirect if user not logged in (missing data)
function checkUserLoggedIn() {
	console.log("checkUserLoggedIn called");
	const userId = localStorage.getItem("userID");
	const userFullName = localStorage.getItem("userFullName");
	const userEmail = localStorage.getItem("userEmail");
	const userDirection = localStorage.getItem("userDirection");
	if (!userId || !userFullName || !userEmail || !userDirection) {
		console.log("User not logged in, redirecting to login.html");
		window.location.href = "../Authentication/login.html";
	}
}

// Attach event listeners after DOM is loaded
checkUserLoggedIn();
console.log("Attaching signout-btn event listener");
document.getElementById("signout-btn").addEventListener("click", logOffUser);
