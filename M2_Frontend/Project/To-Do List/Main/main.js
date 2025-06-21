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
	window.location.href = "../Authentication/login.html";
}

// Redirect if user not logged in (missing data)
function checkUserLoggedIn() {
	const userId = localStorage.getItem("userID");
	const userFullName = localStorage.getItem("userFullName");
	const userEmail = localStorage.getItem("userEmail");
	const userDirection = localStorage.getItem("userDirection");
	if (!userId || !userFullName || !userEmail || !userDirection) {
		window.location.href = "../Authentication/login.html";
	}
}

// Attach event listeners after DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
	checkUserLoggedIn();
	document.getElementById("signout-btn").addEventListener("click", logOffUser);

	const sidebar = document.getElementById("sidebar");
	const toggleBtn = document.getElementById("sidebar-toggle-btn");
	const collapsedBtn = document.getElementById("sidebar-toggle-btn-collapsed");

	// Hide sidebar
	toggleBtn.addEventListener("click", () => {
		sidebar.classList.add("sidebar-hidden");
		collapsedBtn.style.display = "flex";
	});

	// Show sidebar
	collapsedBtn.addEventListener("click", () => {
		sidebar.classList.remove("sidebar-hidden");
		collapsedBtn.style.display = "none";
	});
});
