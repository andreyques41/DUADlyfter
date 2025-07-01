// --- Storage Helpers for Multiple Sections ---
// Handles all localStorage operations for tasks
console.log("storage.js loaded");
const TASK_SECTIONS = ["today", "tomorrow", "thisweek"];

function getAllTasks() {
	let all = {};
	try {
		all = JSON.parse(localStorage.getItem("tasks")) || {};
		// Validate structure: must be an object with today, tomorrow, thisweek as arrays
		const isValid =
			all &&
			typeof all === "object" &&
			!Array.isArray(all) &&
			["today", "tomorrow", "thisweek"].every((sec) => Array.isArray(all[sec]));
		if (!isValid) {
			console.warn(
				"getAllTasks: Detected invalid/corrupt storage, erasing all tasks"
			);
			all = {};
			saveAllTasks(all);
		}
		console.log("getAllTasks: loaded", all);
	} catch (e) {
		console.error("getAllTasks: error parsing localStorage", e);
		all = {};
	}
	// Ensure all sections exist
	TASK_SECTIONS.forEach((sec) => {
		if (!all[sec]) {
			console.log(`getAllTasks: initializing empty section '${sec}'`);
			all[sec] = [];
		}
	});
	return all;
}
function saveAllTasks(all) {
	localStorage.setItem("tasks", JSON.stringify(all));
	console.log("saveAllTasks: All tasks saved:", all);
}
function getSectionTasks(section) {
	const sectionTasks = getAllTasks()[section] || [];
	console.log(`getSectionTasks: section='${section}'`, sectionTasks);
	return sectionTasks;
}
function setSectionTasks(section, tasks) {
	const all = getAllTasks();
	all[section] = tasks;
	saveAllTasks(all);
	console.log(`setSectionTasks: section='${section}' updated`, tasks);
}

// Helper Functions ---

// Helper: Validate form fields (all required)
function validateTaskForm(nameInput, dateInput, catSelect) {
	const value = nameInput.value.trim();
	const date = dateInput.value;
	const category = catSelect.value;
	return value && date && category;
}

// Helper: Clear form fields
function clearTaskForm(nameInput, dateInput, catSelect) {
	nameInput.value = "";
	dateInput.value = "";
	catSelect.value = "";
}

// Helper: Get today's date as YYYY-MM-DD string
function getTodayString() {
	const today = new Date();
	const yyyy = today.getFullYear();
	const mm = String(today.getMonth() + 1).padStart(2, "0");
	const dd = String(today.getDate()).padStart(2, "0");
	return `${yyyy}-${mm}-${dd}`;
}
// Helper: Get the index of the task being edited from the sidebar
function getEditTaskIndex() {
	const editSidebar = document.getElementById("edit-task-sidebar");
	return parseInt(editSidebar.getAttribute("data-edit-idx"), 10);
}

// Helper: Get section for a given date string (YYYY-MM-DD)
function getSectionForDate(dateStr) {
	const todayStr = getTodayString();
	const today = new Date(todayStr);
	const taskDate = new Date(dateStr);
	const diffDays = Math.floor((taskDate - today) / (1000 * 60 * 60 * 24));
	if (diffDays === 0) {
		return "today";
	} else if (diffDays === 1) {
		return "tomorrow";
	} else {
		// Check if within this week (and not today/tomorrow)
		const weekDay = today.getDay(); // 0=Sun, 1=Mon, ...
		const daysLeftInWeek = 6 - weekDay;
		if (diffDays > 1 && diffDays <= daysLeftInWeek) {
			return "thisweek";
		}
	}
	return null;
}

// Helper: Delete a task by index and section
function deleteTaskFromSection(section, idx) {
	const all = getAllTasks();
	if (!all[section] || idx < 0 || idx >= all[section].length) return;
	all[section].splice(idx, 1);
	saveAllTasks(all);
}

// Expose globally
window.getAllTasks = getAllTasks;
window.saveAllTasks = saveAllTasks;
window.getSectionTasks = getSectionTasks;
window.setSectionTasks = setSectionTasks;
window.getSectionForDate = getSectionForDate;
window.deleteTaskFromSection = deleteTaskFromSection;
