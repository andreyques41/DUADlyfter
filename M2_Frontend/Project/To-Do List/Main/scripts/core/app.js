// --- Application Initialization ---
// Main entry point for the application
console.log("app.js loaded");

const App = {
	/**
	 * Initializes the entire application
	 * Sets up UI components and loads initial data
	 * @returns {Promise<boolean>} True if initialization succeeds, false otherwise
	 */
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

	/**
	 * Initializes all UI components
	 * Sets up category dropdowns, event listeners, and task sidebars
	 * @returns {Promise<void>}
	 */
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

	/**
	 * Loads initial data and renders all task sections (optimized)
	 * @returns {Promise<void>}
	 */
	async loadInitialData() {
		console.log("App.init: Loading initial data");

		// Use optimized rendering that loads tasks once and renders all sections
		if (window.renderAllTasksWithFilter) {
			await renderAllTasksWithFilter();
		} else {
			// Fallback to individual section rendering if optimized function not available
			console.warn(
				"App.loadInitialData: Optimized render function not available, falling back to individual renders"
			);
			if (window.renderSectionTasks) {
				await renderSectionTasks("today");
				await renderSectionTasks("upcoming-today");
				await renderSectionTasks("tomorrow");
				await renderSectionTasks("thisweek");
				await renderSectionTasks("finished");
			}
		}

		console.log("App.init: Initial data loaded and rendered");
	},

	/**
	 * Refreshes all application data
	 * Useful for manual refresh operations
	 * @returns {Promise<void>}
	 */
	async refresh() {
		console.log("App.refresh: Refreshing application data");
		await this.loadInitialData();
	},

	/**
	 * Handles application errors with context
	 * @param {Error} error - The error object
	 * @param {string} [context="Unknown"] - Context where the error occurred
	 */
	handleError(error, context = "Unknown") {
		console.error(`App.handleError [${context}]:`, error);
	},

	/**
	 * Shows error message to the user
	 * @param {string} message - Error message to display
	 */
	showErrorMessage(message) {
		console.error("App Error:", message);
		// TODO: Implement user-facing error display
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
