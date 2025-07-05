// --- Task Sidebar Logic (Add/Edit Task, Form, Helpers) ---
// Handles add/edit task sidebar UI, form logic, and helpers
// Exposes openAddTaskSidebar and closeAddTaskSidebar globally
console.log("task-sidebar.js loaded");

// =====================
// Add/Edit Task Sidebar UI Logic
// =====================
function openAddTaskSidebar(section) {
	console.log(
		`openAddTaskSidebar: Opening add sidebar for section '${section}'`
	);
	const addTaskForm = document.getElementById("add-task-form-sidebar");
	const taskSidebar = document.getElementById("add-task-sidebar");

	if (!addTaskForm || !taskSidebar) {
		console.error("openAddTaskSidebar: Required elements not found");
		return;
	}

	addTaskForm.setAttribute("data-section", section);
	console.log(`openAddTaskSidebar: Set form data-section to '${section}'`);

	// Clear form fields
	const nameInput = document.getElementById("sidebar-add-task-name");
	const dateInput = document.getElementById("sidebar-add-task-date");
	const catSelect = document.getElementById("sidebar-add-task-category");
	const todayStr = getTodayString();

	if (nameInput) nameInput.value = "";
	if (dateInput) {
		dateInput.value = todayStr;
		dateInput.min = todayStr;
		console.log(`openAddTaskSidebar: Set date to ${todayStr}`);
	}
	if (catSelect) catSelect.value = "";

	taskSidebar.classList.add("open");
	console.log(`openAddTaskSidebar: Sidebar opened successfully`);
}

function closeAddTaskSidebar() {
	console.log("closeAddTaskSidebar: Closing add sidebar");
	const taskSidebar = document.getElementById("add-task-sidebar");
	if (taskSidebar) {
		taskSidebar.classList.remove("open");
		console.log("closeAddTaskSidebar: Sidebar closed successfully");
	} else {
		console.warn("closeAddTaskSidebar: Sidebar element not found");
	}
}

function openTaskEditSidebar(taskIdx, section) {
	console.log(
		`openTaskEditSidebar: Opening edit sidebar for idx=${taskIdx}, section='${section}'`
	);

	const editSidebar = document.getElementById("edit-task-sidebar");
	if (!editSidebar) {
		console.error("openTaskEditSidebar: Edit sidebar element not found");
		return;
	}

	const validSections = ["today", "upcoming-today", "tomorrow", "thisweek"];
	if (!validSections.includes(section)) {
		console.warn("openTaskEditSidebar: Unknown section:", section);
		return;
	}

	const sec = section === "upcoming-today" ? "today" : section;
	const tasks = getSectionTasks(sec);
	const task = tasks[taskIdx];

	if (!task) {
		console.warn(
			`openTaskEditSidebar: No task found at idx=${taskIdx} in section='${sec}'`
		);
		return;
	}

	console.log(`openTaskEditSidebar: Editing task:`, task);

	// Populate form fields
	const nameInput = document.getElementById("sidebar-edit-task-name");
	const dateInput = document.getElementById("sidebar-edit-task-date");
	const catSelect = document.getElementById("sidebar-edit-task-category");

	if (nameInput) nameInput.value = task.text;
	if (dateInput) {
		dateInput.value = task.date || "";
		dateInput.min = getTodayString();
		console.log(
			`openTaskEditSidebar: Set date input - value='${dateInput.value}', min='${dateInput.min}'`
		);
	}
	if (catSelect) {
		catSelect.value = task.category || "";
		console.log(
			`openTaskEditSidebar: Set category input - value='${task.category || ""}'`
		);
	}

	editSidebar.setAttribute("data-edit-idx", taskIdx);
	editSidebar.setAttribute("data-original-section", sec);
	editSidebar.classList.add("open");
	console.log(
		`openTaskEditSidebar: Edit sidebar opened successfully for section='${sec}', idx=${taskIdx}`
	);
}

// =====================
// Generalized Task Sidebar Setup (Add/Edit)
// =====================
function setupTaskSidebar(type) {
	console.log(`setupTaskSidebar: Setting up ${type} sidebar`);
	const isAdd = type === "add";
	const sidebarId = isAdd ? "add-task-sidebar" : "edit-task-sidebar";
	const formId = isAdd ? "add-task-form-sidebar" : "edit-task-form-sidebar";
	const openBtnSelector = isAdd ? ".add-task-btn" : ".edit-task-btn";
	const closeBtnId = isAdd ? "close-add-task-sidebar" : "close-edit-sidebar-x";

	const sidebar = document.getElementById(sidebarId);
	const sidebarForm = document.getElementById(formId);
	const openSidebarBtns = document.querySelectorAll(openBtnSelector);
	const closeSidebarBtn = document.getElementById(closeBtnId);

	if (!sidebar || !sidebarForm) {
		console.error(
			`setupTaskSidebar: Required elements not found for ${type} sidebar`
		);
		return;
	}

	// Bind open logic (for add only; edit is opened programmatically)
	if (isAdd) {
		console.log(
			`setupTaskSidebar: Binding ${openSidebarBtns.length} open buttons for add sidebar`
		);
		openSidebarBtns.forEach(function (btn) {
			btn.addEventListener("click", function () {
				const section = this.getAttribute("data-section");
				console.log(
					`setupTaskSidebar: Add button clicked for section '${section}'`
				);
				openAddTaskSidebar(section);
			});
		});
	}

	// Bind close logic
	if (closeSidebarBtn) {
		closeSidebarBtn.addEventListener("click", function () {
			console.log(`setupTaskSidebar: Close button clicked for ${type} sidebar`);
			sidebar.classList.remove("open");
		});
	} else {
		console.warn(
			`setupTaskSidebar: Close button not found for ${type} sidebar`
		);
	}

	// Bind form submit logic
	sidebarForm.addEventListener("submit", function (e) {
		console.log(`setupTaskSidebar: Form submitted for ${type} sidebar`);
		handleTaskFormSubmit(e, type);
	});

	console.log(`setupTaskSidebar: ${type} sidebar setup complete`);
}

// =====================
// Task Form Submit Logic (Generalized for Add/Edit)
// =====================
function handleTaskFormSubmit(e, type) {
	e.preventDefault();
	console.log(`handleTaskFormSubmit: Processing ${type} form submission`);

	const isAdd = type === "add";
	const form = document.getElementById(
		isAdd ? "add-task-form-sidebar" : "edit-task-form-sidebar"
	);
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
		console.warn(
			`handleTaskFormSubmit: Task form validation failed for ${type}`
		);
		alert("Please fill in all fields.");
		return;
	}

	const value = nameInput.value.trim();
	const date = dateInput.value;
	const category = catSelect.value;
	console.log(
		`handleTaskFormSubmit: Form data - name: '${value}', date: '${date}', category: '${category}'`
	);

	const all = getAllTasks();
	const targetSection = getSectionForDate(date);
	let originalSection = targetSection;

	if (!targetSection) {
		console.warn(
			`handleTaskFormSubmit: Invalid date '${date}' for section assignment`
		);
		alert("Date must be today, tomorrow, or within this week.");
		return;
	}

	if (isAdd) {
		addTaskToSection(all, targetSection, value, date, category);
	} else {
		// For edit, get the original section from the sidebar's data attribute
		const editSidebar = document.getElementById("edit-task-sidebar");
		originalSection = editSidebar.getAttribute("data-original-section");
		if (!originalSection) {
			console.warn(
				"handleTaskFormSubmit: No original section found, using target section"
			);
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

	// Re-render affected sections
	if (targetSection === originalSection) {
		renderRelevantSections(targetSection);
	} else {
		renderRelevantSections(targetSection);
		renderRelevantSections(originalSection);
	}

	clearTaskForm(nameInput, dateInput, catSelect);
	const sidebarId = isAdd ? "add-task-sidebar" : "edit-task-sidebar";
	document.getElementById(sidebarId).classList.remove("open");
	console.log(`handleTaskFormSubmit: ${type} operation completed successfully`);
}

function addTaskToSection(all, section, text, date, category) {
	console.log(`addTaskToSection: Adding task to section '${section}'`);
	all[section] = all[section] || [];
	all[section].push({
		text,
		completed: false,
		date,
		category,
	});
	console.log(`addTaskToSection: Task added to section='${section}':`, {
		text,
		date,
		category,
	});
}

function editTaskInSection(
	all,
	originalSection,
	newSection,
	text,
	date,
	category
) {
	console.log(
		`editTaskInSection: Editing task - from '${originalSection}' to '${newSection}'`
	);
	const editSidebar = document.getElementById("edit-task-sidebar");
	const idx = parseInt(editSidebar.getAttribute("data-edit-idx"), 10);

	if (isNaN(idx)) {
		console.error("editTaskInSection: Invalid task index for edit");
		alert("Invalid task index for edit.");
		return;
	}

	if (!originalSection) originalSection = newSection;

	if (originalSection === newSection) {
		// Same section - just update the task
		all[newSection][idx] = {
			...all[newSection][idx],
			text,
			date,
			category,
		};
		console.log(
			`editTaskInSection: Task updated in section='${newSection}', idx=${idx}`
		);
	} else {
		// Different section - move the task
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
				`editTaskInSection: Task moved from '${originalSection}' to '${newSection}'`
			);
		} else {
			console.error(
				`editTaskInSection: Task not found at idx=${idx} in section='${originalSection}'`
			);
		}
	}
}

function renderRelevantSections(section) {
	console.log(`renderRelevantSections: Rendering for section '${section}'`);
	if (section === "today") {
		renderSectionTasks("today");
		renderSectionTasks("upcoming-today");
	} else {
		renderSectionTasks(section);
	}
}

// --- Expose Main Functions Globally ---
window.openTaskEditSidebar = openTaskEditSidebar;
window.setupTaskSidebar = setupTaskSidebar;
window.openAddTaskSidebar = openAddTaskSidebar;
window.closeAddTaskSidebar = closeAddTaskSidebar;

// Check availability of exposed functions
if (window.openTaskEditSidebar) {
	console.log("task-sidebar.js: openTaskEditSidebar function is available");
} else {
	console.warn("task-sidebar.js: openTaskEditSidebar function not found");
}

if (window.setupTaskSidebar) {
	console.log("task-sidebar.js: setupTaskSidebar function is available");
} else {
	console.warn("task-sidebar.js: setupTaskSidebar function not found");
}

if (window.openAddTaskSidebar) {
	console.log("task-sidebar.js: openAddTaskSidebar function is available");
} else {
	console.warn("task-sidebar.js: openAddTaskSidebar function not found");
}

if (window.closeAddTaskSidebar) {
	console.log("task-sidebar.js: closeAddTaskSidebar function is available");
} else {
	console.warn("task-sidebar.js: closeAddTaskSidebar function not found");
}

// Attach delete button event listener ONCE (not inside setupTaskSidebar)
(function attachDeleteBtnListener() {
	const deleteBtn = document.getElementById("delete-task-btn");
	if (deleteBtn) {
		console.log("attachDeleteBtnListener: Attaching delete button listener");
		deleteBtn.addEventListener("click", function () {
			console.log("attachDeleteBtnListener: Delete button clicked");
			const editSidebar = document.getElementById("edit-task-sidebar");
			const idx = parseInt(editSidebar.getAttribute("data-edit-idx"), 10);
			const section = editSidebar.getAttribute("data-original-section");

			if (isNaN(idx) || !section) {
				console.warn("attachDeleteBtnListener: Invalid delete parameters", {
					idx,
					section,
				});
				return;
			}

			if (confirm("Are you sure you want to delete this task?")) {
				console.log(
					`attachDeleteBtnListener: Deleting task at idx=${idx} from section='${section}'`
				);
				deleteTaskFromSection(section, idx);
				renderRelevantSections(section);
				editSidebar.classList.remove("open");
				console.log("attachDeleteBtnListener: Task deleted successfully");
			} else {
				console.log("attachDeleteBtnListener: Delete cancelled by user");
			}
		});
	} else {
		console.warn("attachDeleteBtnListener: Delete button not found");
	}
})();
