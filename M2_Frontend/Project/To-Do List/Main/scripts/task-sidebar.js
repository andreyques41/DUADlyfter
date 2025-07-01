// --- Task Sidebar Logic (Add/Edit Task, Form, Helpers) ---
// Handles add/edit task sidebar UI, form logic, and helpers
// Exposes openAddTaskSidebar and closeAddTaskSidebar globally
console.log("task-sidebar.js loaded");

// =====================
// Add/Edit Task Sidebar UI Logic
// =====================
function openAddTaskSidebar(section) {
	const addTaskForm = document.getElementById("add-task-form-sidebar");
	const taskSidebar = document.getElementById("add-task-sidebar");
	addTaskForm.setAttribute("data-section", section);
	console.log(`Open add task sidebar button clicked for section='${section}'`);
	// Clear form fields
	const nameInput = document.getElementById("sidebar-add-task-name");
	const dateInput = document.getElementById("sidebar-add-task-date");
	const catSelect = document.getElementById("sidebar-add-task-category");
	const todayStr = getTodayString();
	if (nameInput) nameInput.value = "";
	if (dateInput) {
		dateInput.value = todayStr;
		dateInput.min = todayStr;
	}
	if (catSelect) catSelect.value = "";
	taskSidebar.classList.add("open");
	console.log(`Add sidebar opened for section='${section}'`);
}
function closeAddTaskSidebar() {
	const taskSidebar = document.getElementById("add-task-sidebar");
	taskSidebar.classList.remove("open");
	console.log(`Add sidebar closed`);
}

function openTaskEditSidebar(taskIdx, section) {
	console.log(`openTaskEditSidebar: idx=${taskIdx}, section='${section}'`);
	let editSidebar, nameId, dateId, catId, sec;
	editSidebar = document.getElementById("edit-task-sidebar");
	nameId = "sidebar-edit-task-name";
	dateId = "sidebar-edit-task-date";
	catId = "sidebar-edit-task-category";
	const validSections = ["today", "upcoming-today", "tomorrow", "thisweek"];
	if (!validSections.includes(section)) {
		console.warn("openTaskEditSidebar: Unknown section:", section);
		return;
	}
	sec = section === "upcoming-today" ? "today" : section;
	const tasks = getSectionTasks(sec);
	const task = tasks[taskIdx];
	if (!task) {
		console.warn(
			`openTaskEditSidebar: No task found at idx=${taskIdx} in section='${sec}'`
		);
		return;
	}
	console.log(`Editing task:`, task);
	document.getElementById(nameId).value = task.text;
	const dateInput = document.getElementById(dateId);
	if (dateInput) {
		dateInput.value = task.date || "";
		dateInput.min = getTodayString();
		console.log(
			`Set date input for edit: value='${dateInput.value}', min='${dateInput.min}'`
		);
	}
	document.getElementById(catId).value = task.category || "";
	console.log(`Set category input for edit: value='${task.category || ""}'`);
	editSidebar.setAttribute("data-edit-idx", taskIdx);
	editSidebar.setAttribute("data-original-section", sec); // Set the original section for edit logic
	editSidebar.classList.add("open");
	console.log(`Edit sidebar opened for section='${sec}', idx=${taskIdx}`);
}

// =====================
// Generalized Task Sidebar Setup (Add/Edit)
// =====================
function setupTaskSidebar(type) {
	const isAdd = type === "add";
	const sidebarId = isAdd ? "add-task-sidebar" : "edit-task-sidebar";
	const formId = isAdd ? "add-task-form-sidebar" : "edit-task-form-sidebar";
	const openBtnSelector = isAdd ? ".add-task-btn" : ".edit-task-btn";
	const closeBtnId = isAdd ? "close-add-task-sidebar" : "close-edit-sidebar-x";
	const sidebar = document.getElementById(sidebarId);
	const sidebarForm = document.getElementById(formId);
	const openSidebarBtns = document.querySelectorAll(openBtnSelector);
	const closeSidebarBtn = document.getElementById(closeBtnId);

	// Bind open logic (for add only; edit is opened programmatically)
	if (isAdd) {
		openSidebarBtns.forEach(function (btn) {
			btn.addEventListener("click", function () {
				const section = this.getAttribute("data-section");
				openAddTaskSidebar(section);
			});
		});
	}
	// Bind close logic
	if (closeSidebarBtn) {
		closeSidebarBtn.addEventListener("click", function () {
			sidebar.classList.remove("open");
			console.log(
				`${type.charAt(0).toUpperCase() + type.slice(1)} sidebar closed`
			);
		});
	}
	// Bind form submit logic
	if (sidebarForm) {
		sidebarForm.addEventListener("submit", function (e) {
			handleTaskFormSubmit(e, type);
		});
	}
}

// =====================
// Task Form Submit Logic (Generalized for Add/Edit)
// =====================
function handleTaskFormSubmit(e, type) {
	e.preventDefault();
	const isAdd = type === "add";
	const formId = isAdd ? "add-task-form-sidebar" : "edit-task-form-sidebar";
	const form = document.getElementById(formId);
	const nameInput = document.getElementById(
		isAdd ? "sidebar-add-task-name" : "sidebar-edit-task-name"
	);
	const dateInput = document.getElementById(
		isAdd ? "sidebar-add-task-date" : "sidebar-edit-task-date"
	);
	const catSelect = document.getElementById(
		isAdd ? "sidebar-add-task-category" : "sidebar-edit-task-category"
	);

	if (!validateTaskForm(nameInput, dateInput, catSelect)) {
		console.warn(`Task form validation failed for ${type}`);
		alert("Please fill in all fields.");
		return;
	}
	const value = nameInput.value.trim();
	const date = dateInput.value;
	const category = catSelect.value;
	const all = getAllTasks();
	const targetSection = getSectionForDate(date);
	let originalSection = targetSection;

	if (!targetSection) {
		alert("Date must be today, tomorrow, or within this week.");
		console.warn(`Task form: Invalid date '${date}' for section assignment`);
		return;
	}
	if (isAdd) {
		addTaskToSection(all, targetSection, value, date, category);
	} else {
		// For edit, get the original section from the sidebar's data attribute
		const editSidebar = document.getElementById("edit-task-sidebar");
		originalSection = editSidebar.getAttribute("data-original-section");
		if (!originalSection) {
			// fallback: try to get from the current view or from the form
			originalSection = targetSection;
		}
		editTaskInSection(
			all,
			originalSection,
			targetSection,
			value,
			date,
			category
		);
	}
	saveAllTasks(all);

	if (targetSection === originalSection) {
		renderRelevantSections(targetSection);
	} else {
		renderRelevantSections(targetSection);
		renderRelevantSections(originalSection);
	}
	clearTaskForm(nameInput, dateInput, catSelect);
	const sidebarId = isAdd ? "add-task-sidebar" : "edit-task-sidebar";
	document.getElementById(sidebarId).classList.remove("open");
	console.log(
		`${
			type.charAt(0).toUpperCase() + type.slice(1)
		} sidebar closed after submit`
	);
}

function addTaskToSection(all, section, text, date, category) {
	all[section] = all[section] || [];
	all[section].push({
		text,
		completed: false,
		date,
		category,
	});
	console.log(`Task added to section='${section}':`, { text, date, category });
}
function editTaskInSection(
	all,
	originalSection,
	newSection,
	text,
	date,
	category
) {
	const editSidebar = document.getElementById("edit-task-sidebar");
	const idx = parseInt(editSidebar.getAttribute("data-edit-idx"), 10);
	if (isNaN(idx)) {
		alert("Invalid task index for edit.");
		console.warn("Edit sidebar: Invalid task index");
		return;
	}
	if (!originalSection) originalSection = newSection;
	if (originalSection === newSection) {
		all[newSection][idx] = {
			...all[newSection][idx],
			text,
			date,
			category,
		};
		console.log(`Task edited in section='${newSection}', idx=${idx}:`, {
			text,
			date,
			category,
		});
	} else {
		const task = all[originalSection][idx];
		if (task) {
			all[originalSection].splice(idx, 1);
			all[newSection] = all[newSection] || [];
			all[newSection].push({
				...task,
				text,
				date,
				category,
			});
			console.log(
				`Task moved from section='${originalSection}' to section='${newSection}':`,
				{ text, date, category }
			);
			all[originalSection] = all[originalSection].filter(Boolean);
		}
	}
}
function renderRelevantSections(section) {
	if (section === "today") {
		renderSectionTasks("today");
		renderSectionTasks("upcoming-today");
	} else {
		renderSectionTasks(section);
	}
}

// --- Expose Main Functions Globally ---
window.openAddTaskSidebar = openAddTaskSidebar;
window.closeAddTaskSidebar = closeAddTaskSidebar;
window.openTaskEditSidebar = openTaskEditSidebar;
window.setupTaskSidebar = setupTaskSidebar;

// Attach delete button event listener ONCE (not inside setupTaskSidebar)
(function attachDeleteBtnListener() {
	const deleteBtn = document.getElementById("delete-task-btn");
	if (deleteBtn) {
		deleteBtn.addEventListener("click", function () {
			const editSidebar = document.getElementById("edit-task-sidebar");
			const idx = parseInt(editSidebar.getAttribute("data-edit-idx"), 10);
			const section = editSidebar.getAttribute("data-original-section");
			if (isNaN(idx) || !section) return;
			if (confirm("Are you sure you want to delete this task?")) {
				deleteTaskFromSection(section, idx);
				renderRelevantSections(section);
				editSidebar.classList.remove("open");
				console.log(`Task deleted from section='${section}', idx=${idx}`);
			}
		});
	}
})();
