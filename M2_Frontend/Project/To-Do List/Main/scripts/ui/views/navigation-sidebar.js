// --- Navigation Sidebar Logic ---
// Handles main sidebar navigation, toggle, and settings logic
// Exposes openTaskEditSidebar and setupTaskSidebar globally
console.log("navigation-sidebar.js loaded");

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

/**
 * Updates the active state of navigation items
 * @param {Element} activeItem - The navigation item to set as active
 * @param {string} env - The environment name for logging
 */
function updateActiveNavigation(activeItem, env) {
	navEnvItems.forEach((el) => el.classList.remove("active"));
	activeItem.classList.add("active");
	console.log("sidebar-ui.js: Set active class for:", env);
}

/**
 * Hides all main views and settings view
 */
function hideAllViews() {
	// Hide all main views
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
}

/**
 * Shows the selected view and handles special cases
 * @param {string} env - The environment/view to show
 */
function showSelectedView(env) {
	if (envViews[env]) {
		envViews[env].style.display = "block";
		console.log("sidebar-ui.js: Showing view:", env);

		// Special handling for sticky view
		if (env === "sticky") {
			console.log("sidebar-ui.js: Sticky view activated, triggering render");
			if (window.renderStickyWall) {
				window.renderStickyWall();
			} else {
				console.warn("sidebar-ui.js: renderStickyWall function not available");
			}
		}
	} else {
		console.warn("sidebar-ui.js: No view found for environment:", env);
	}
}

/**
 * Auto-closes any open task sidebars when navigating
 */
function autoCloseTaskSidebars() {
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
}

/**
 * Handles main navigation click events
 * @param {string} env - The environment/view to navigate to
 * @param {Element} clickedItem - The navigation item that was clicked
 */
function handleMainNavigation(env, clickedItem) {
	console.log("sidebar-ui.js: Navigation clicked for environment:", env);

	updateActiveNavigation(clickedItem, env);
	hideAllViews();
	showSelectedView(env);
	autoCloseTaskSidebars();
}

// Navigation click: switch main view, update active, auto-close add sidebar
navEnvItems.forEach((item) => {
	item.addEventListener("click", function () {
		const env = this.getAttribute("data-env");
		handleMainNavigation(env, this);
	});
});

// =====================
// Main Sidebar Navigation (Main Views) - Modularized Functions
// =====================

/**
 * Main navigation helper functions for better maintainability.
 * These functions were extracted from a large navigation click handler
 * to improve code organization and readability.
 */

/**
 * Updates the active state of navigation items
 * @param {Element} activeItem - The navigation item to set as active
 * @param {string} env - The environment name for logging
 */
function updateActiveNavigation(activeItem, env) {
	navEnvItems.forEach((el) => el.classList.remove("active"));
	activeItem.classList.add("active");
	console.log("sidebar-ui.js: Set active class for:", env);
}

/**
 * Hides all main views and settings view
 */
function hideAllViews() {
	// Hide all main views
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
}

/**
 * Shows the selected view and handles special cases
 * @param {string} env - The environment/view to show
 */
function showSelectedView(env) {
	if (envViews[env]) {
		envViews[env].style.display = "block";
		console.log("sidebar-ui.js: Showing view:", env);

		// Special handling for sticky view
		if (env === "sticky") {
			console.log("sidebar-ui.js: Sticky view activated, triggering render");
			if (window.renderStickyWall) {
				window.renderStickyWall();
			} else {
				console.warn("sidebar-ui.js: renderStickyWall function not available");
			}
		}
	} else {
		console.warn("sidebar-ui.js: No view found for environment:", env);
	}
}

/**
 * Auto-closes any open task sidebars when navigating
 */
function autoCloseTaskSidebars() {
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
}

/**
 * Handles main navigation click events
 * @param {string} env - The environment/view to navigate to
 * @param {Element} clickedItem - The navigation item that was clicked
 */
function handleMainNavigation(env, clickedItem) {
	console.log("sidebar-ui.js: Navigation clicked for environment:", env);

	updateActiveNavigation(clickedItem, env);
	hideAllViews();
	showSelectedView(env);
	autoCloseTaskSidebars();
}

// =====================
// Settings View Logic
// =====================
const settingsView = document.getElementById("settings-view");
const settingsBtn = document.getElementById("settings-btn");

/**
 * Closes all task sidebars when opening settings
 */
function closeTaskSidebarsForSettings() {
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
}

/**
 * Handles the settings button click event
 */
function handleSettingsClick() {
	console.log("sidebar-ui.js: Settings button clicked");

	// Hide all other views
	Object.values(envViews).forEach((value) => {
		if (value) value.style.display = "none";
	});

	closeTaskSidebarsForSettings();

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
}

if (settingsBtn) {
	console.log("sidebar-ui.js: Settings button found, attaching event listener");
	settingsBtn.addEventListener("click", handleSettingsClick);
} else {
	console.error("sidebar-ui.js: Settings button not found");
}

/**
 * Renders all task sections after deletion
 */
async function renderAllSectionsAfterDeletion() {
	if (window.renderSectionTasks) {
		await window.renderSectionTasks("today");
		await window.renderSectionTasks("upcoming-today");
		await window.renderSectionTasks("tomorrow");
		await window.renderSectionTasks("thisweek");
		console.log("sidebar-ui.js: All sections re-rendered after deletion");
	}
}

/**
 * Handles the delete all tasks operation
 */
async function handleDeleteAllTasks() {
	console.log("sidebar-ui.js: Delete all tasks button clicked");

	if (
		!confirm(
			"Are you sure you want to delete ALL tasks? This cannot be undone."
		)
	) {
		console.log("sidebar-ui.js: User cancelled deletion of all tasks");
		return;
	}

	console.log("sidebar-ui.js: User confirmed deletion of all tasks");

	try {
		if (window.saveAllTasks) {
			window.saveAllTasks({ today: [], tomorrow: [], thisweek: [] });
			console.log("sidebar-ui.js: All tasks cleared from storage");
		}

		await renderAllSectionsAfterDeletion();

		alert("All tasks deleted.");
		console.log("sidebar-ui.js: All tasks deletion completed successfully");
	} catch (error) {
		console.error("sidebar-ui.js: Error during task deletion:", error);
		alert("Error occurred while deleting tasks.");
	}
}

// Settings view event handling
if (settingsView) {
	settingsView.addEventListener("click", async function (e) {
		if (e.target && e.target.id === "delete-all-tasks-btn") {
			await handleDeleteAllTasks();
		}
	});
} else {
	console.warn("sidebar-ui.js: Settings view not found for event handling");
}
