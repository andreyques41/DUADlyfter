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

if (!mainSidebar || !mainSidebarToggleBtn || !mainSidebarCollapsedBtn) {
	console.error("sidebar-ui.js: Required sidebar elements not found");
} else {
	console.log(
		"sidebar-ui.js: Sidebar elements found, setting up toggle functionality"
	);
}

// Hide Main Sidebar
mainSidebarToggleBtn.addEventListener("click", () => {
	console.log("sidebar-ui.js: Sidebar hide button clicked");
	mainSidebar.classList.add("sidebar-hidden");
	mainSidebarCollapsedBtn.style.display = "flex";
	console.log("sidebar-ui.js: Sidebar hidden, collapsed button shown");
});
// Show Main Sidebar
mainSidebarCollapsedBtn.addEventListener("click", () => {
	console.log("sidebar-ui.js: Sidebar show button clicked");
	mainSidebar.classList.remove("sidebar-hidden");
	mainSidebarCollapsedBtn.style.display = "none";
	console.log("sidebar-ui.js: Sidebar shown, collapsed button hidden");
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

console.log("sidebar-ui.js: Found", navEnvItems.length, "navigation items");
console.log(
	"sidebar-ui.js: Available views:",
	Object.keys(envViews).filter((key) => envViews[key])
);

// Navigation click: switch main view, update active, auto-close add sidebar
navEnvItems.forEach((item) => {
	item.addEventListener("click", function () {
		const env = this.getAttribute("data-env");
		console.log("sidebar-ui.js: Navigation clicked for environment:", env);

		// Remove active from all
		navEnvItems.forEach((el) => el.classList.remove("active"));
		this.classList.add("active");
		console.log("sidebar-ui.js: Set active class for:", env);

		// Hide all views
		Object.values(envViews).forEach((value) => {
			if (value) value.style.display = "none";
		});

		// Hide settings view if open
		const settingsView = document.getElementById("settings-view");
		if (settingsView && settingsView.style.display !== "none") {
			settingsView.style.display = "none";
			console.log(
				"sidebar-ui.js: Settings view hidden due to main view navigation"
			);
		}

		console.log("sidebar-ui.js: All views hidden");

		// Show selected view
		if (envViews[env]) {
			envViews[env].style.display = "block";
			console.log("sidebar-ui.js: Showing view:", env);

			// Special handling for sticky view
			if (env === "sticky") {
				console.log("sidebar-ui.js: Sticky view activated, triggering render");
				if (window.renderStickyWall) {
					window.renderStickyWall();
				} else {
					console.warn(
						"sidebar-ui.js: renderStickyWall function not available"
					);
				}
			}
		} else {
			console.warn("sidebar-ui.js: No view found for environment:", env);
		}

		// Auto-close Add Task Sidebar if open
		const addTaskSidebar = document.getElementById("add-task-sidebar");
		if (addTaskSidebar && addTaskSidebar.classList.contains("open")) {
			if (window.closeAddTaskSidebar) {
				window.closeAddTaskSidebar();
				console.log(
					"sidebar-ui.js: Add Task Sidebar auto-closed due to main view navigation"
				);
			}
		}

		// Auto-close Edit Task Sidebar if open
		const editTaskSidebar = document.getElementById("edit-task-sidebar");
		if (editTaskSidebar && editTaskSidebar.classList.contains("open")) {
			editTaskSidebar.classList.remove("open");
			console.log(
				"sidebar-ui.js: Edit Task Sidebar auto-closed due to main view navigation"
			);
		}
	});
});

// =====================
// Settings View Logic
// =====================
const settingsView = document.getElementById("settings-view");
const settingsBtn = document.getElementById("settings-btn");

if (settingsBtn) {
	console.log("sidebar-ui.js: Settings button found, attaching event listener");
	settingsBtn.addEventListener("click", function () {
		console.log("sidebar-ui.js: Settings button clicked");

		// Hide all other views
		Object.values(envViews).forEach((value) => {
			if (value) value.style.display = "none";
		});

		// Hide add/edit sidebars if open
		const addTaskSidebar = document.getElementById("add-task-sidebar");
		if (addTaskSidebar && addTaskSidebar.classList.contains("open")) {
			if (window.closeAddTaskSidebar) {
				window.closeAddTaskSidebar();
				console.log(
					"sidebar-ui.js: Add Task Sidebar closed when opening settings"
				);
			}
		}

		const editTaskSidebar = document.getElementById("edit-task-sidebar");
		if (editTaskSidebar && editTaskSidebar.classList.contains("open")) {
			editTaskSidebar.classList.remove("open");
			console.log(
				"sidebar-ui.js: Edit Task Sidebar closed when opening settings"
			);
		}

		// Show settings view
		if (settingsView) {
			settingsView.style.display = "block";
			console.log("sidebar-ui.js: Settings view shown");
		} else {
			console.error("sidebar-ui.js: Settings view element not found");
		}

		// Remove active from all nav items
		navEnvItems.forEach((el) => el.classList.remove("active"));
		console.log("sidebar-ui.js: Removed active class from all nav items");
	});
} else {
	console.warn("sidebar-ui.js: Settings button not found");
}

// Settings view event handling
if (settingsView) {
	settingsView.addEventListener("click", function (e) {
		if (e.target && e.target.id === "delete-all-tasks-btn") {
			console.log("sidebar-ui.js: Delete all tasks button clicked");
			if (
				confirm(
					"Are you sure you want to delete ALL tasks? This cannot be undone."
				)
			) {
				console.log("sidebar-ui.js: User confirmed deletion of all tasks");
				try {
					if (window.saveAllTasks) {
						window.saveAllTasks({ today: [], tomorrow: [], thisweek: [] });
						console.log("sidebar-ui.js: All tasks cleared from storage");
					}

					// Re-render all sections
					if (window.renderSectionTasks) {
						window.renderSectionTasks("today");
						window.renderSectionTasks("upcoming-today");
						window.renderSectionTasks("tomorrow");
						window.renderSectionTasks("thisweek");
						console.log(
							"sidebar-ui.js: All sections re-rendered after deletion"
						);
					}

					alert("All tasks deleted.");
					console.log(
						"sidebar-ui.js: All tasks deletion completed successfully"
					);
				} catch (error) {
					console.error("sidebar-ui.js: Error during task deletion:", error);
					alert("Error occurred while deleting tasks.");
				}
			} else {
				console.log("sidebar-ui.js: User cancelled deletion of all tasks");
			}
		}
	});
} else {
	console.warn("sidebar-ui.js: Settings view not found for event handling");
}
