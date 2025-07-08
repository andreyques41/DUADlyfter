// --- Core Storage Operations for Tasks ---
// Handles localStorage operations, validation, and core task management
console.log("storage-core.js loaded");

const TASK_SECTIONS = APP_CONFIG.TASK_SECTIONS;

// --- Helper Functions ---

// Helper: Calculate total tasks across all sections
function calculateTotalTasks(tasksObject) {
	return TASK_SECTIONS.reduce(
		(sum, sec) => sum + (tasksObject[sec]?.length || 0),
		0
	);
}

// Helper: Validate tasks structure
function validateTasksStructure(tasksObject) {
	return (
		tasksObject &&
		typeof tasksObject === "object" &&
		!Array.isArray(tasksObject) &&
		["today", "tomorrow", "thisweek"].every((sec) =>
			Array.isArray(tasksObject[sec])
		)
	);
}

// Helper: Ensure all required sections exist
function ensureAllSectionsExist(tasksObject) {
	TASK_SECTIONS.forEach((sec) => {
		if (!tasksObject[sec]) {
			console.log(
				`ensureAllSectionsExist: initializing empty section '${sec}'`
			);
			tasksObject[sec] = [];
		}
	});
	return tasksObject;
}

// Helper: Load tasks from API as fallback
async function loadTasksFromAPI() {
	console.log("loadTasksFromAPI: Attempting to load from API");

	try {
		const dataFromApi = await window.syncTasksFromAPI();
		if (dataFromApi && dataFromApi.tasks) {
			console.log("loadTasksFromAPI: Successfully loaded tasks from API");
			// Save the API data to localStorage with timestamp
			saveAllTasks(dataFromApi.tasks);
			return dataFromApi.tasks;
		} else {
			console.log("loadTasksFromAPI: API returned no valid tasks");
			return {};
		}
	} catch (error) {
		console.error("loadTasksFromAPI: Error loading from API", error);
		return {};
	}
}

// Helper: Sync with API if available and needed
async function syncWithAPIIfNeeded(localTasks) {
	console.log("syncWithAPIIfNeeded: Checking if sync is needed");

	try {
		const dataFromApi = await window.syncTasksFromAPI();
		if (!dataFromApi || !dataFromApi.tasks || !dataFromApi.lastModified) {
			console.log("syncWithAPIIfNeeded: API returned incomplete data");
			return localTasks;
		}

		const localLastModified = localStorage.getItem(
			APP_CONFIG.STORAGE_KEYS.TASKS_LAST_MODIFIED
		);
		const localTimestamp = localLastModified ? parseInt(localLastModified) : 0;
		const apiTimestamp = dataFromApi.lastModified;

		const comparison = AppUtils.compareTimestamps(localTimestamp, apiTimestamp);

		if (comparison === "api_newer") {
			console.log(
				"syncWithAPIIfNeeded: API data is newer, updating localStorage"
			);
			localStorage.setItem(
				APP_CONFIG.STORAGE_KEYS.TASKS_LAST_MODIFIED,
				apiTimestamp.toString()
			);
			localStorage.setItem(
				APP_CONFIG.STORAGE_KEYS.TASKS,
				JSON.stringify(dataFromApi.tasks)
			);
			return dataFromApi.tasks;
		} else {
			console.log("syncWithAPIIfNeeded: Local data is newer or same");
			return localTasks;
		}
	} catch (error) {
		console.error("syncWithAPIIfNeeded: Error during sync", error);
		return localTasks;
	}
}

// --- Main Storage Functions ---

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

		// Validate structure
		const isValid = validateTasksStructure(tasksFromStorage);

		if (!isValid) {
			console.warn(
				"getAllTasks: Detected invalid/corrupt storage, attempting to load from API"
			);
			tasksFromStorage = await loadTasksFromAPI();
		} else {
			// Valid localStorage data - check if we should sync with API
			tasksFromStorage = await syncWithAPIIfNeeded(tasksFromStorage);
		}

		console.log("getAllTasks: loaded", tasksFromStorage);
	} catch (e) {
		console.error("getAllTasks: error loading tasks", e);
		tasksFromStorage = {};
	}

	// Ensure all sections exist
	tasksFromStorage = ensureAllSectionsExist(tasksFromStorage);

	const totalTasks = calculateTotalTasks(tasksFromStorage);
	console.log(`getAllTasks: Total tasks loaded: ${totalTasks}`);

	return tasksFromStorage;
}

function saveAllTasks(allTasks) {
	try {
		const timestamp = AppUtils.getCurrentTimestamp();

		localStorage.setItem(
			APP_CONFIG.STORAGE_KEYS.TASKS,
			JSON.stringify(allTasks)
		);
		localStorage.setItem(
			APP_CONFIG.STORAGE_KEYS.TASKS_LAST_MODIFIED,
			timestamp.toString()
		);

		const totalTasks = calculateTotalTasks(allTasks);
		console.log(
			`saveAllTasks: Successfully saved ${totalTasks} tasks across all sections with timestamp ${timestamp}`
		);

		// Sync to API in background (don't wait for it)
		window.syncTasksToAPI(allTasks, timestamp).catch((error) => {
			console.error("saveAllTasks: Background sync failed:", error);
		});
	} catch (error) {
		console.error("saveAllTasks: Error saving tasks to localStorage", error);
	}
}

// --- Section-Specific Functions ---

async function getSectionTasks(section) {
	console.log(`getSectionTasks: Getting tasks for section '${section}'`);
	const allTasks = await getAllTasks();
	const sectionTasks = allTasks[section] || [];
	console.log(
		`getSectionTasks: section='${section}' has ${sectionTasks.length} tasks`
	);
	return sectionTasks;
}

async function setSectionTasks(section, tasks) {
	console.log(
		`setSectionTasks: Setting ${tasks.length} tasks for section '${section}'`
	);
	const allTasks = await getAllTasks();
	allTasks[section] = tasks;
	saveAllTasks(allTasks);
	console.log(`setSectionTasks: section='${section}' updated successfully`);
}

async function deleteTaskFromSection(section, idx) {
	console.log(
		`deleteTaskFromSection: Deleting task at idx=${idx} from section '${section}'`
	);
	const allTasks = await getAllTasks();
	if (!allTasks[section] || idx < 0 || idx >= allTasks[section].length) {
		console.warn(
			`deleteTaskFromSection: Invalid deletion - section='${section}', idx=${idx}, array length=${
				allTasks[section]?.length || 0
			}`
		);
		return;
	}

	const taskName = allTasks[section][idx]?.text || "unknown";
	allTasks[section].splice(idx, 1);
	saveAllTasks(allTasks);
	console.log(
		`deleteTaskFromSection: Successfully deleted task '${taskName}' from section '${section}'`
	);
}

// --- Form & Utility Helper Functions ---

// Expose globally
window.getAllTasks = getAllTasks;
window.saveAllTasks = saveAllTasks;
window.getSectionTasks = getSectionTasks;
window.setSectionTasks = setSectionTasks;
window.deleteTaskFromSection = deleteTaskFromSection;
