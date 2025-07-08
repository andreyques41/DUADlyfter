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

/**
 * Validates the edit sidebar parameters
 * @param {number} taskIdx - The task index
 * @param {string} section - The section name
 * @returns {Object|null} Validation result with editSidebar and normalizedSection, or null if invalid
 */
function validateEditSidebarParams(taskIdx, section) {
	const editSidebar = document.getElementById("edit-task-sidebar");
	if (!editSidebar) {
		console.error("openTaskEditSidebar: Edit sidebar element not found");
		return null;
	}

	const validSections = ["today", "upcoming-today", "tomorrow", "thisweek"];
	if (!validSections.includes(section)) {
		console.warn("openTaskEditSidebar: Unknown section:", section);
		return null;
	}

	const normalizedSection = section === "upcoming-today" ? "today" : section;
	return { editSidebar, normalizedSection };
}

/**
 * Retrieves and validates the task to edit
 * @param {number} taskIdx - The task index
 * @param {string} section - The normalized section name
 * @returns {Object|null} The task object or null if not found
 */
async function getTaskToEdit(taskIdx, section) {
	const tasks = await getSectionTasks(section);
	const task = tasks[taskIdx];

	if (!task) {
		console.warn(
			`openTaskEditSidebar: No task found at idx=${taskIdx} in section='${section}'`
		);
		return null;
	}

	console.log(`openTaskEditSidebar: Editing task:`, task);
	return task;
}

/**
 * Populates the edit form with task data
 * @param {Object} task - The task object
 */
function populateEditForm(task) {
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
}

/**
 * Opens the task edit sidebar with the specified task
 * @param {number} taskIdx - The index of the task to edit
 * @param {string} section - The section containing the task
 */
async function openTaskEditSidebar(taskIdx, section) {
	console.log(
		`openTaskEditSidebar: Opening edit sidebar for idx=${taskIdx}, section='${section}'`
	);

	const validation = validateEditSidebarParams(taskIdx, section);
	if (!validation) return;

	const { editSidebar, normalizedSection } = validation;

	const task = await getTaskToEdit(taskIdx, normalizedSection);
	if (!task) return;

	populateEditForm(task);

	editSidebar.setAttribute("data-edit-idx", taskIdx);
	editSidebar.setAttribute("data-original-section", normalizedSection);
	editSidebar.classList.add("open");
	console.log(
		`openTaskEditSidebar: Edit sidebar opened successfully for section='${normalizedSection}', idx=${taskIdx}`
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
	sidebarForm.addEventListener("submit", async function (e) {
		console.log(`setupTaskSidebar: Form submitted for ${type} sidebar`);
		await handleTaskFormSubmit(e, type);
	});

	console.log(`setupTaskSidebar: ${type} sidebar setup complete`);
}

// =====================
// Task Form Submit Logic (Streamlined)
// =====================
async function handleTaskFormSubmit(e, type) {
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

	const all = await getAllTasks();
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
		await reRenderAffectedSections(targetSection, targetSection);
	} else {
		await reRenderAffectedSections(targetSection, targetSection);
		await reRenderAffectedSections(originalSection, originalSection);
	}

	clearTaskForm(nameInput, dateInput, catSelect);
	const sidebarId = isAdd ? "add-task-sidebar" : "edit-task-sidebar";
	document.getElementById(sidebarId).classList.remove("open");
	console.log(`handleTaskFormSubmit: ${type} operation completed successfully`);
}

function addTaskToSection(all, section, text, date, category) {
	console.log(`addTaskToSection: Adding task to section '${section}'`);
	all[section] = all[section] || [];
	const timestamp = AppUtils.getCurrentTimestamp();
	all[section].push({
		text,
		completed: false,
		date,
		category: category || "", // Ensure category is string, not null/undefined
		createdAt: timestamp,
		updatedAt: timestamp, // Set initial updatedAt same as createdAt
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
			updatedAt: AppUtils.getCurrentTimestamp(), // Update timestamp
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
				updatedAt: AppUtils.getCurrentTimestamp(), // Update timestamp
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

// --- Expose Main Functions Globally ---
window.openTaskEditSidebar = openTaskEditSidebar;
window.setupTaskSidebar = setupTaskSidebar;
window.openAddTaskSidebar = openAddTaskSidebar;
window.closeAddTaskSidebar = closeAddTaskSidebar;

// Attach delete button event listener ONCE (not inside setupTaskSidebar)
(function attachDeleteBtnListener() {
	const deleteBtn = document.getElementById("delete-task-btn");
	if (deleteBtn) {
		console.log("attachDeleteBtnListener: Attaching delete button listener");
		deleteBtn.addEventListener("click", async function () {
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
				await deleteTaskFromSection(section, idx);
				await reRenderAffectedSections(section, section);
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
