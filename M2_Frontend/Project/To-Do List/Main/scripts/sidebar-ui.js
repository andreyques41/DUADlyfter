// --- Sidebar UI Logic (Navigation, Main Sidebar, Settings) ---
// Handles main sidebar navigation, toggle, and settings logic
// Exposes openTaskEditSidebar and setupTaskSidebar globally
console.log("sidebar-ui.js loaded");

// =====================
// Main Sidebar Toggle Logic
// =====================
const mainSidebar = document.getElementById("sidebar");
const mainSidebarToggleBtn = document.getElementById("sidebar-toggle-btn");
const mainSidebarCollapsedBtn = document.getElementById(
	"sidebar-toggle-btn-collapsed"
);

// Hide Main Sidebar
mainSidebarToggleBtn.addEventListener("click", () => {
	console.log("Sidebar hide button clicked");
	mainSidebar.classList.add("sidebar-hidden");
	mainSidebarCollapsedBtn.style.display = "flex";
	console.log("Sidebar hidden, collapsed button shown");
});
// Show Main Sidebar
mainSidebarCollapsedBtn.addEventListener("click", () => {
	console.log("Sidebar show button clicked");
	mainSidebar.classList.remove("sidebar-hidden");
	mainSidebarCollapsedBtn.style.display = "none";
	console.log("Sidebar shown, collapsed button hidden");
});

// =====================
// Main Sidebar Navigation (Main Views)
// =====================
const navEnvItems = document.querySelectorAll(".env-item");
const envViews = {
	today: document.getElementById("today-view"),
	upcoming: document.getElementById("upcoming-view"),
	sticky: document.getElementById("sticky-view"),
	finished: document.getElementById("finished-view"),
};
// Navigation click: switch main view, update active, auto-close add sidebar
navEnvItems.forEach((item) => {
	item.addEventListener("click", function () {
		const env = this.getAttribute("data-env");
		console.log("Sidebar navigation clicked:", env);
		// Remove active from all
		navEnvItems.forEach((el) => el.classList.remove("active"));
		this.classList.add("active");
		console.log("Set active class for:", env);
		// Hide all views
		Object.values(envViews).forEach((value) => {
			if (value) value.style.display = "none";
		});
		// Hide settings view if open
		const settingsView = document.getElementById("settings-view");
		if (settingsView && settingsView.style.display !== "none") {
			settingsView.style.display = "none";
			console.log("Settings view hidden due to main view navigation");
		}
		console.log("All views hidden");
		// Show selected view
		if (envViews[env]) {
			envViews[env].style.display = "block";
			console.log("Showing view:", env);
		} else {
			console.warn("No view found for:", env);
		}
		// Auto-close Add Task Sidebar if open
		const addTaskSidebar = document.getElementById("add-task-sidebar");
		if (addTaskSidebar && addTaskSidebar.classList.contains("open")) {
			closeAddTaskSidebar();
			console.log("Add Task Sidebar auto-closed due to main view navigation");
		}
	});
});

// =====================
// Settings View Logic
// =====================
const settingsView = document.getElementById("settings-view");
const settingsBtn = document.getElementById("settings-btn");
if (settingsBtn) {
	settingsBtn.addEventListener("click", function () {
		// Hide all other views
		Object.values(envViews).forEach((value) => {
			if (value) value.style.display = "none";
		});
		// Hide add/edit sidebars if open
		const addTaskSidebar = document.getElementById("add-task-sidebar");
		if (addTaskSidebar && addTaskSidebar.classList.contains("open")) {
			closeAddTaskSidebar();
		}
		const editTaskSidebar = document.getElementById("edit-task-sidebar");
		if (editTaskSidebar && editTaskSidebar.classList.contains("open")) {
			editTaskSidebar.classList.remove("open");
		}
		// Show settings view
		settingsView.style.display = "block";
		// Remove active from all nav items
		navEnvItems.forEach((el) => el.classList.remove("active"));
		console.log("Settings view shown");
	});
}
settingsView.addEventListener("click", function (e) {
	if (e.target && e.target.id === "delete-all-tasks-btn") {
		if (
			confirm(
				"Are you sure you want to delete ALL tasks? This cannot be undone."
			)
		) {
			saveAllTasks({ today: [], tomorrow: [], thisweek: [] });
			renderSectionTasks("today");
			renderSectionTasks("upcoming-today");
			renderSectionTasks("tomorrow");
			renderSectionTasks("thisweek");
			alert("All tasks deleted.");
			console.log("All tasks deleted from storage.");
		}
	}
});

// --- Expose Main Functions Globally ---
window.openTaskEditSidebar = openTaskEditSidebar;
window.setupTaskSidebar = setupTaskSidebar;
