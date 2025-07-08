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
	// Get today's date as YYYY-MM-DD string
	getTodayString() {
		const today = new Date();
		const yyyy = today.getFullYear();
		const mm = String(today.getMonth() + 1).padStart(2, "0");
		const dd = String(today.getDate()).padStart(2, "0");
		const todayStr = `${yyyy}-${mm}-${dd}`;
		console.log(`AppUtils.getTodayString: Today is ${todayStr}`);
		return todayStr;
	},

	// Get current timestamp
	getCurrentTimestamp() {
		const timestamp = Date.now();
		console.log(
			`AppUtils.getCurrentTimestamp: Generated timestamp ${timestamp}`
		);
		return timestamp;
	},

	// Compare timestamps
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

	// Get section for a given date string
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
	// Validate task form fields
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

	// Clear form fields
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
