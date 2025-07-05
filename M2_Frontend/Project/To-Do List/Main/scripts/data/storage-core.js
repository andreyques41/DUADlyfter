// --- Core Storage Operations for Tasks ---
// Handles localStorage operations, validation, and core task management
console.log("storage-core.js loaded");

const TASK_SECTIONS = APP_CONFIG.TASK_SECTIONS;

async function getAllTasks() {
	console.log("getAllTasks: Retrieving all tasks from localStorage");
	let tasksFromStorage = {};

	try {
		const stored = localStorage.getItem(APP_CONFIG.STORAGE_KEYS.TASKS);
		tasksFromStorage = stored ? JSON.parse(stored) : {};
		console.log(
			"getAllTasks: Raw data from localStorage:",
			stored ? "found" : "empty"
		);

		// Validate structure: must be an object with today, tomorrow, thisweek as arrays
		const isValid =
			tasksFromStorage &&
			typeof tasksFromStorage === "object" &&
			!Array.isArray(tasksFromStorage) &&
			["today", "tomorrow", "thisweek"].every((sec) =>
				Array.isArray(tasksFromStorage[sec])
			);

		if (!isValid) {
			console.warn(
				"getAllTasks: Detected invalid/corrupt storage, attempting to load from API"
			);

			// Try to load from API as fallback (requires storage-sync.js)
			if (window.syncTasksFromAPI) {
				const dataFromApi = await window.syncTasksFromAPI();
				if (dataFromApi && dataFromApi.tasks) {
					tasksFromStorage = dataFromApi.tasks;
					console.log("getAllTasks: Loaded tasks from API as fallback");
					// Save the API data to localStorage with timestamp
					saveAllTasks(tasksFromStorage);
				} else {
					tasksFromStorage = {};
					console.log("getAllTasks: Using empty tasks as final fallback");
				}
			} else {
				tasksFromStorage = {};
				console.log("getAllTasks: No API sync available, using empty tasks");
			}
		} else {
			// Valid localStorage data - check if we should sync with API
			if (window.syncTasksFromAPI && window.compareTimestamps) {
				const dataFromApi = await window.syncTasksFromAPI();
				if (dataFromApi && dataFromApi.tasks && dataFromApi.lastModified) {
					const localLastModified = localStorage.getItem(
						APP_CONFIG.STORAGE_KEYS.TASKS_LAST_MODIFIED
					);
					const localTimestamp = localLastModified
						? parseInt(localLastModified)
						: 0;
					const apiTimestamp = dataFromApi.lastModified;

					const comparison = AppUtils.compareTimestamps(
						localTimestamp,
						apiTimestamp
					);

					// If API data is newer, use it
					if (comparison === "api_newer") {
						console.log(
							"getAllTasks: API data is newer, updating localStorage"
						);
						tasksFromStorage = dataFromApi.tasks;
						localStorage.setItem(
							APP_CONFIG.STORAGE_KEYS.TASKS_LAST_MODIFIED,
							apiTimestamp.toString()
						);
						localStorage.setItem(
							APP_CONFIG.STORAGE_KEYS.TASKS,
							JSON.stringify(tasksFromStorage)
						);
					} else {
						console.log(
							"getAllTasks: Local data is newer or same, keeping localStorage"
						);
					}
				}
			}
		}

		console.log("getAllTasks: loaded", tasksFromStorage);
	} catch (e) {
		console.error("getAllTasks: error loading tasks", e);
		tasksFromStorage = {};
	}

	// Ensure all sections exist
	TASK_SECTIONS.forEach((sec) => {
		if (!tasksFromStorage[sec]) {
			console.log(`getAllTasks: initializing empty section '${sec}'`);
			tasksFromStorage[sec] = [];
		}
	});

	const totalTasks = TASK_SECTIONS.reduce(
		(sum, sec) => sum + (tasksFromStorage[sec]?.length || 0),
		0
	);
	console.log(`getAllTasks: Total tasks loaded: ${totalTasks}`);

	return tasksFromStorage;
}

function saveAllTasks(all) {
	try {
		const timestamp = AppUtils.getCurrentTimestamp();

		localStorage.setItem(APP_CONFIG.STORAGE_KEYS.TASKS, JSON.stringify(all));
		localStorage.setItem(
			APP_CONFIG.STORAGE_KEYS.TASKS_LAST_MODIFIED,
			timestamp.toString()
		);

		const totalTasks = TASK_SECTIONS.reduce(
			(sum, sec) => sum + (all[sec]?.length || 0),
			0
		);
		console.log(
			`saveAllTasks: Successfully saved ${totalTasks} tasks across all sections with timestamp ${timestamp}`
		);

		// Sync to API in background (don't wait for it) - requires storage-sync.js
		if (window.syncTasksToAPI) {
			window.syncTasksToAPI(all, timestamp).catch((error) => {
				console.error("saveAllTasks: Background sync failed:", error);
			});
		}
	} catch (error) {
		console.error("saveAllTasks: Error saving tasks to localStorage", error);
	}
}

function getSectionTasks(section) {
	console.log(`getSectionTasks: Getting tasks for section '${section}'`);
	const all = getAllTasks();
	const sectionTasks = all[section] || [];
	console.log(
		`getSectionTasks: section='${section}' has ${sectionTasks.length} tasks`
	);
	return sectionTasks;
}

function setSectionTasks(section, tasks) {
	console.log(
		`setSectionTasks: Setting ${tasks.length} tasks for section '${section}'`
	);
	const all = getAllTasks();
	all[section] = tasks;
	saveAllTasks(all);
	console.log(`setSectionTasks: section='${section}' updated successfully`);
}

function deleteTaskFromSection(section, idx) {
	console.log(
		`deleteTaskFromSection: Deleting task at idx=${idx} from section '${section}'`
	);
	const all = getAllTasks();
	if (!all[section] || idx < 0 || idx >= all[section].length) {
		console.warn(
			`deleteTaskFromSection: Invalid deletion - section='${section}', idx=${idx}, array length=${
				all[section]?.length || 0
			}`
		);
		return;
	}

	const taskName = all[section][idx]?.text || "unknown";
	all[section].splice(idx, 1);
	saveAllTasks(all);
	console.log(
		`deleteTaskFromSection: Successfully deleted task '${taskName}' from section '${section}'`
	);
}

// Helper Functions ---

// Helper: Validate form fields (all required)
function validateTaskForm(nameInput, dateInput, catSelect) {
	return FormUtils.validateTaskForm(nameInput, dateInput, catSelect);
}

// Helper: Clear form fields
function clearTaskForm(nameInput, dateInput, catSelect) {
	return FormUtils.clearTaskForm(nameInput, dateInput, catSelect);
}

// Helper: Get today's date as YYYY-MM-DD string
function getTodayString() {
	return AppUtils.getTodayString();
}

// Helper: Get the index of the task being edited from the sidebar
function getEditTaskIndex() {
	return FormUtils.getEditTaskIndex();
}

// Helper: Get section for a given date string (YYYY-MM-DD)
function getSectionForDate(dateStr) {
	return AppUtils.getSectionForDate(dateStr);
}

// Expose globally
window.getAllTasks = getAllTasks;
window.saveAllTasks = saveAllTasks;
window.getSectionTasks = getSectionTasks;
window.setSectionTasks = setSectionTasks;
window.getSectionForDate = getSectionForDate;
window.deleteTaskFromSection = deleteTaskFromSection;

// Check availability of exposed functions
if (window.getAllTasks) {
	console.log("storage-core.js: getAllTasks function is available");
} else {
	console.warn("storage-core.js: getAllTasks function not found");
}

if (window.saveAllTasks) {
	console.log("storage-core.js: saveAllTasks function is available");
} else {
	console.warn("storage-core.js: saveAllTasks function not found");
}

if (window.getSectionTasks) {
	console.log("storage-core.js: getSectionTasks function is available");
} else {
	console.warn("storage-core.js: getSectionTasks function not found");
}

if (window.setSectionTasks) {
	console.log("storage-core.js: setSectionTasks function is available");
} else {
	console.warn("storage-core.js: setSectionTasks function not found");
}

if (window.getSectionForDate) {
	console.log("storage-core.js: getSectionForDate function is available");
} else {
	console.warn("storage-core.js: getSectionForDate function not found");
}

if (window.deleteTaskFromSection) {
	console.log("storage-core.js: deleteTaskFromSection function is available");
} else {
	console.warn("storage-core.js: deleteTaskFromSection function not found");
}
