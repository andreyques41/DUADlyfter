// --- App Configuration and Constants ---
// Central configuration for the entire application
console.log("config.js loaded");

const APP_CONFIG = {
	TASK_SECTIONS: ["today", "tomorrow", "thisweek"],
	DEFAULT_CATEGORIES: ["Personal", "Work", "Family"],
	API_CONFIG: {
		BASE_URL: "https://api.restful-api.dev/objects",
		TIMEOUT: 5000,
	},
	STORAGE_KEYS: {
		TASKS: "tasks",
		TASKS_LAST_MODIFIED: "tasksLastModified",
		USER_ID: "userID",
		USER_FULL_NAME: "userFullName",
		USER_EMAIL: "userEmail",
		USER_PASSWORD: "userPassword",
	},
};

// Utility functions
const AppUtils = {
	/**
	 * Gets today's date as YYYY-MM-DD string
	 * @returns {string} Today's date in YYYY-MM-DD format
	 */
	getTodayString() {
		const today = new Date();
		const yyyy = today.getFullYear();
		const mm = String(today.getMonth() + 1).padStart(2, "0");
		const dd = String(today.getDate()).padStart(2, "0");
		const todayStr = `${yyyy}-${mm}-${dd}`;
		console.log(`AppUtils.getTodayString: Today is ${todayStr}`);
		return todayStr;
	},

	/**
	 * Gets current timestamp in milliseconds
	 * @returns {number} Current timestamp
	 */
	getCurrentTimestamp() {
		const timestamp = Date.now();
		console.log(
			`AppUtils.getCurrentTimestamp: Generated timestamp ${timestamp}`
		);
		return timestamp;
	},

	/**
	 * Compares two timestamps to determine which is newer
	 * @param {number} localTimestamp - Local timestamp to compare
	 * @param {number} apiTimestamp - API timestamp to compare
	 * @returns {string} "api_newer", "local_newer", or "equal"
	 */
	compareTimestamps(localTimestamp, apiTimestamp) {
		const local = localTimestamp || 0;
		const api = apiTimestamp || 0;

		console.log(`AppUtils.compareTimestamps: Local: ${local}, API: ${api}`);

		if (api > local) {
			console.log("AppUtils.compareTimestamps: API data is newer");
			return "api_newer";
		} else if (local > api) {
			console.log("AppUtils.compareTimestamps: Local data is newer");
			return "local_newer";
		} else {
			console.log("AppUtils.compareTimestamps: Timestamps are equal");
			return "equal";
		}
	},

	/**
	 * Determines which section a task belongs to based on its date
	 * @param {string} dateStr - Date string in YYYY-MM-DD format
	 * @returns {string|null} Section name ("today", "tomorrow", "thisweek") or null if not found
	 */
	getSectionForDate(dateStr) {
		console.log(
			`AppUtils.getSectionForDate: Determining section for date '${dateStr}'`
		);
		const todayStr = this.getTodayString();
		const today = new Date(todayStr);
		const taskDate = new Date(dateStr);
		const diffDays = Math.floor((taskDate - today) / (1000 * 60 * 60 * 24));

		let section = null;
		if (diffDays === 0) {
			section = "today";
		} else if (diffDays === 1) {
			section = "tomorrow";
		} else {
			// Check if within this week (and not today/tomorrow)
			const weekDay = today.getDay(); // 0=Sun, 1=Mon, ...
			const daysLeftInWeek = 6 - weekDay;
			if (diffDays > 1 && diffDays <= daysLeftInWeek) {
				section = "thisweek";
			}
		}

		console.log(
			`AppUtils.getSectionForDate: Date '${dateStr}' (${diffDays} days from today) -> section '${section}'`
		);
		return section;
	},
};

// Form validation utilities
const FormUtils = {
	/**
	 * Validates task form fields for required data
	 * @param {HTMLInputElement} nameInput - Task name input element
	 * @param {HTMLInputElement} dateInput - Task date input element
	 * @param {HTMLSelectElement} catSelect - Task category select element
	 * @returns {boolean} True if validation passes, false otherwise
	 */
	validateTaskForm(nameInput, dateInput, catSelect) {
		const value = nameInput.value.trim();
		const date = dateInput.value;
		const category = catSelect.value;
		// Category is optional - only name and date are required
		const isValid = value && date;
		console.log(
			`FormUtils.validateTaskForm: Validation ${
				isValid ? "passed" : "failed"
			} - name: ${!!value}, date: ${!!date}, category: ${!!category} (optional)`
		);
		return isValid;
	},

	/**
	 * Clears all fields in a task form
	 * @param {HTMLInputElement} nameInput - Task name input element
	 * @param {HTMLInputElement} dateInput - Task date input element
	 * @param {HTMLSelectElement} catSelect - Task category select element
	 */
	clearTaskForm(nameInput, dateInput, catSelect) {
		console.log("FormUtils.clearTaskForm: Clearing form fields");
		nameInput.value = "";
		dateInput.value = "";
		catSelect.value = "";
	},
};

// Expose globally
window.APP_CONFIG = APP_CONFIG;
window.AppUtils = AppUtils;
window.FormUtils = FormUtils;

// Legacy compatibility for functions used directly in UI code
window.getSectionForDate = AppUtils.getSectionForDate;
window.validateTaskForm = FormUtils.validateTaskForm;
window.clearTaskForm = FormUtils.clearTaskForm;
window.getTodayString = AppUtils.getTodayString;

console.log("config.js: App configuration and utilities loaded");
