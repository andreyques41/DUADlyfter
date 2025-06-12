function updateUserCard() {
	document.getElementById("card-fullname").textContent =
		localStorage.getItem("userFullName") || "";
	document.getElementById("card-email").textContent =
		localStorage.getItem("userEmail") || "";
	document.getElementById("card-direction").textContent =
		localStorage.getItem("userDirection") || "";
}

function logOffUser() {
	// Remove user tokens from localStorage
	localStorage.removeItem("userID");
	localStorage.removeItem("userFullName");
	localStorage.removeItem("userEmail");
	localStorage.removeItem("userPassword");
	localStorage.removeItem("userDirection");
	// Optionally redirect to register or login page
	window.location.href = "register.html";
}

// Add event listener to the form to handle user registration on submit
// Add this script at the end of <body> or in a separate JS file
document.addEventListener("DOMContentLoaded", function () {
	updateUserCard();
	document.getElementById("logoff-btn").addEventListener("click", logOffUser);
});
