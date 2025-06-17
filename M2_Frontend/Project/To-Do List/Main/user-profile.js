// Fill user profile card with stored data
function updateUserCard() {
	document.getElementById("card-fullname").textContent =
		localStorage.getItem("userFullName") || "";
	document.getElementById("card-email").textContent =
		localStorage.getItem("userEmail") || "";
	document.getElementById("card-direction").textContent =
		localStorage.getItem("userDirection") || "";
}

// Log off user and clear localStorage/session
function logOffUser() {
	localStorage.removeItem("userID");
	localStorage.removeItem("userFullName");
	localStorage.removeItem("userEmail");
	localStorage.removeItem("userPassword");
	localStorage.removeItem("userDirection");
	window.location.href = "../login/login.html";
}

// Redirect if user not logged in (missing data)
function checkUserLoggedIn() {
	const userId = localStorage.getItem("userID");
	const userFullName = localStorage.getItem("userFullName");
	const userEmail = localStorage.getItem("userEmail");
	const userDirection = localStorage.getItem("userDirection");
	if (!userId || !userFullName || !userEmail || !userDirection) {
		window.location.href = "../login/login.html";
	}
}

// Attach event listeners after DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
	checkUserLoggedIn();
	updateUserCard();
	document.getElementById("logoff-btn").addEventListener("click", logOffUser);
});
