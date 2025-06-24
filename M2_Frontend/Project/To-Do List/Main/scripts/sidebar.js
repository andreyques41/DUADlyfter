// Remove DOMContentLoaded wrapper, run code at top level
console.log("sidebar.js loaded");
const sidebar = document.getElementById("sidebar");
const toggleBtn = document.getElementById("sidebar-toggle-btn");
const collapsedBtn = document.getElementById("sidebar-toggle-btn-collapsed");

// Hide sidebar
toggleBtn.addEventListener("click", () => {
	console.log("Sidebar hide button clicked");
	sidebar.classList.add("sidebar-hidden");
	collapsedBtn.style.display = "flex";
});

// Show sidebar
collapsedBtn.addEventListener("click", () => {
	console.log("Sidebar show button clicked");
	sidebar.classList.remove("sidebar-hidden");
	collapsedBtn.style.display = "none";
});

// Sidebar navigation for Tasks (Today, Upcoming, Sticky Wall)
const envItems = document.querySelectorAll(".env-item");
const views = {
	today: document.getElementById("today-view"),
	upcoming: document.getElementById("upcoming-view"),
	sticky: document.getElementById("sticky-view"),
	finished: document.getElementById("finished-view"),
};

envItems.forEach((item) => {
	item.addEventListener("click", function () {
		console.log("Sidebar navigation clicked:", this.getAttribute("data-env"));
		// Remove active from all
		envItems.forEach((el) => el.classList.remove("active"));
		this.classList.add("active");
		// Hide all views
		Object.values(views).forEach((v) => (v.style.display = "none"));
		// Show selected view
		const env = this.getAttribute("data-env");
		if (views[env]) {
			views[env].style.display = "block";
			console.log("Showing view:", env);
		}
	});
});
