// --- Application Initialization ---
// Main entry point for the application
console.log("app.js loaded");

const App = {
	// Initialize the entire application
	async init() {
		console.log("App.init: Starting application initialization");

		try {
			// Note: User session is already checked by user-session.js
			// Initialize UI components
			await this.initializeUI();

			// Load and render data
			await this.loadInitialData();

			console.log(
				"App.init: Application initialization completed successfully"
			);
			return true;
		} catch (error) {
			console.error(
				"App.init: Error during application initialization:",
				error
			);
			return false;
		}
	},

	// Initialize UI components
	async initializeUI() {
		console.log("App.init: Initializing UI components");

		// Populate category dropdowns
		if (window.populateAllCategoryDropdowns) {
			populateAllCategoryDropdowns();
		}

		// Initialize category event listeners (add, delete, filter)
		if (window.initializeCategoryEventListeners) {
			initializeCategoryEventListeners();
		}

		// Set up task sidebars
		if (window.setupTaskSidebar) {
			setupTaskSidebar("add");
			setupTaskSidebar("edit");
		}

		console.log("App.init: UI components initialized");
	},

	// Load initial data and render
	async loadInitialData() {
		console.log("App.init: Loading initial data");

		// Render all task sections
		if (window.renderSectionTasks) {
			await renderSectionTasks("today");
			await renderSectionTasks("upcoming-today");
			await renderSectionTasks("tomorrow");
			await renderSectionTasks("thisweek");
		}

		console.log("App.init: Initial data loaded and rendered");
	},

	// Refresh all data (useful for manual refresh)
	async refresh() {
		console.log("App.refresh: Refreshing application data");
		await this.loadInitialData();
	},

	// Handle application errors
	handleError(error, context = "Unknown") {
		console.error(`App.handleError [${context}]:`, error);
	},

	// Show error message to user (placeholder)
	showErrorMessage(message) {
		console.error("App Error:", message);
	},
};

// Auto-initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
	console.log("App: DOM loaded, initializing application");
	App.init().catch((error) => {
		App.handleError(error, "Initialization");
	});
});

// Expose globally
window.App = App;

console.log("app.js: Application controller loaded");
