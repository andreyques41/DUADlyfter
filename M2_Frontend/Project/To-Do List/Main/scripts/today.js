// Debug information
console.log("today.js loaded");

// --- Helper Functions ---
// Save all tasks to localStorage as a JSON array
function saveTasks(tasks) {
	localStorage.setItem("tasks", JSON.stringify(tasks));
	console.log("Tasks saved to localStorage:", tasks);
}

// Load tasks from localStorage (returns array)
function loadTasks() {
	try {
		const tasks = JSON.parse(localStorage.getItem("tasks") || "[]");
		console.log("Loaded tasks from localStorage:", tasks);
		return tasks;
	} catch (error) {
		console.error("Error loading tasks from localStorage:", error);
		return [];
	}
}

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

// Helper: Get the index of the task being edited from the sidebar
function getEditTaskIndex() {
	const editSidebar = document.getElementById("edit-task-sidebar");
	return parseInt(editSidebar.getAttribute("data-edit-idx"), 10);
}

// Helper: Save, render, and close edit sidebar after task change
function updateTasksAndUI(tasks) {
	saveTasks(tasks);
	renderTodayTasks(tasks);
	const editSidebar = document.getElementById("edit-task-sidebar");
	if (editSidebar) editSidebar.classList.remove("open");
}

// Helper: Get today's date as YYYY-MM-DD string
function getTodayString() {
	const today = new Date();
	const yyyy = today.getFullYear();
	const mm = String(today.getMonth() + 1).padStart(2, "0");
	const dd = String(today.getDate()).padStart(2, "0");
	return `${yyyy}-${mm}-${dd}`;
}

// --- UI Rendering Functions ---
// Populate category dropdown for both forms
function populateCategoryDropdowns() {
	// Get all category items except the add button
	const catList = document.querySelectorAll(
		".cat-list .cat-item:not(.add-list)"
	);
	// Get both category selects (add/edit)
	const selects = [
		document.getElementById("sidebar-task-category"),
		document.getElementById("sidebar-edit-task-category"),
	].filter(Boolean);
	selects.forEach((select) => {
		select.innerHTML = '<option value="">Select category</option>';
		catList.forEach((cat) => {
			const option = document.createElement("option");
			option.value = cat.textContent.trim();
			option.textContent = cat.textContent.trim();
			select.appendChild(option);
		});
	});
	console.log("Category dropdowns populated");
}

// Create a task element for rendering
function createTaskElement(task, idx, tasks) {
	const li = document.createElement("li");
	li.className = "task-item";
	li.id = `task_${idx + 1}`;

	// Header: checkbox + task name
	const headerDiv = document.createElement("div");
	headerDiv.className = "task-header";
	const checkbox = document.createElement("input");
	checkbox.type = "checkbox";
	checkbox.className = "task-checkbox";
	checkbox.checked = !!task.completed;
	// Checkbox toggles completed state
	checkbox.addEventListener("change", function () {
		li.classList.toggle("completed", this.checked);
		task.completed = this.checked;
		saveTasks(tasks);
		console.log(
			`Task \"${task.text}\" marked as ${
				this.checked ? "completed" : "not completed"
			}`
		);
	});
	headerDiv.appendChild(checkbox);
	const nameDiv = document.createElement("div");
	nameDiv.className = "task-main-text";
	nameDiv.textContent = task.text;
	headerDiv.appendChild(nameDiv);
	li.appendChild(headerDiv);

	// Second line: logo, date, category
	const metaDiv = document.createElement("div");
	metaDiv.className = "task-meta";
	if (task.date) {
		const logo = document.createElement("img");
		logo.src = "../assets/logos/calendar.svg";
		logo.alt = "date";
		logo.className = "task-meta-logo";
		metaDiv.appendChild(logo);
		const dateSpan = document.createElement("span");
		dateSpan.className = "task-date";
		dateSpan.textContent = task.date;
		metaDiv.appendChild(dateSpan);
	}
	if (task.category) {
		const catSpan = document.createElement("span");
		catSpan.className = "task-category";
		catSpan.textContent = task.category;
		metaDiv.appendChild(catSpan);
	}
	li.appendChild(metaDiv);

	if (task.completed) li.classList.add("completed");

	// Add click event to open edit sidebar (except on checkbox)
	li.addEventListener("click", function (e) {
		if (e.target === checkbox) return;
		openEditSidebar(idx);
	});

	return li;
}

// Render all tasks in the Today list
function renderTodayTasks(tasks) {
	const parentList = document.querySelector("#today-view .task-list");
	parentList.innerHTML = "";
	tasks.forEach((task, idx) => {
		const li = createTaskElement(task, idx, tasks);
		parentList.appendChild(li);
	});
}

// Open edit sidebar and pre-fill form
function openEditSidebar(taskIdx) {
	const editSidebar = document.getElementById("edit-task-sidebar");
	const tasks = loadTasks();
	const task = tasks[taskIdx];
	if (!task) return;

	// Fill form fields with task data
	document.getElementById("sidebar-edit-task-name").value = task.text;
	const dateInput = document.getElementById("sidebar-edit-task-date");
	if (dateInput) {
		dateInput.value = task.date || "";
		// Set min date to today
		dateInput.min = getTodayString();
	}
	document.getElementById("sidebar-edit-task-category").value =
		task.category || "";

	// Store index for saving
	editSidebar.setAttribute("data-edit-idx", taskIdx);

	// Open sidebar
	editSidebar.classList.add("open");
}

// --- Sidebar open/close logic ---
const openSidebarBtn = document.getElementById("open-task-sidebar");
const addTaskSidebar = document.getElementById("task-sidebar");
const closeSidebarBtn = document.getElementById("close-task-sidebar");

// Open add task sidebar and set today's date
if (openSidebarBtn && addTaskSidebar) {
	openSidebarBtn.addEventListener("click", () => {
		// Set today's date as default and min for the date input
		const dateInput = document.getElementById("sidebar-task-date");
		if (dateInput) {
			const todayStr = getTodayString();
			dateInput.value = todayStr;
			dateInput.min = todayStr;
		}
		addTaskSidebar.classList.add("open");
	});
}
// Close add task sidebar
if (closeSidebarBtn && addTaskSidebar) {
	closeSidebarBtn.addEventListener("click", () => {
		addTaskSidebar.classList.remove("open");
	});
}

// Close edit sidebar logic (button at bottom)
const closeEditSidebarBtn = document.querySelector(
	"#edit-task-sidebar #close-task-sidebar"
);
const editTaskSidebar = document.getElementById("edit-task-sidebar");
if (closeEditSidebarBtn && editTaskSidebar) {
	closeEditSidebarBtn.addEventListener("click", () => {
		editTaskSidebar.classList.remove("open");
	});
}
// Close edit sidebar when X button is clicked (top right)
const closeEditSidebarXBtn = document.getElementById("close-edit-sidebar-x");
if (closeEditSidebarXBtn && editTaskSidebar) {
	closeEditSidebarXBtn.addEventListener("click", () => {
		editTaskSidebar.classList.remove("open");
	});
}

// --- Event Listeners for Forms ---
// Add task form logic for sidebar (all fields required)
const addTaskFormSidebar = document.getElementById("task-form-sidebar");
if (addTaskFormSidebar) {
	addTaskFormSidebar.addEventListener("submit", function (e) {
		e.preventDefault();
		const nameInput = document.getElementById("sidebar-task-name");
		const dateInput = document.getElementById("sidebar-task-date");
		const catSelect = document.getElementById("sidebar-task-category");
		if (validateTaskForm(nameInput, dateInput, catSelect)) {
			const value = nameInput.value.trim();
			const date = dateInput.value;
			const category = catSelect.value;
			const tasks = loadTasks();
			tasks.push({ text: value, completed: false, date, category });
			saveTasks(tasks);
			renderTodayTasks(tasks);
			console.log("Task added from sidebar:", value, date, category);
			clearTaskForm(nameInput, dateInput, catSelect);
			addTaskSidebar.classList.remove("open");
		} else {
			alert("Please fill in all fields.");
		}
	});
}

// Edit task form logic for sidebar (all fields required)
const editTaskFormSidebar = document.getElementById("edit-task-form-sidebar");
const deleteTaskBtn = document.getElementById("delete-task-btn");
if (editTaskFormSidebar) {
	editTaskFormSidebar.addEventListener("submit", function (e) {
		e.preventDefault();
		const nameInput = document.getElementById("sidebar-edit-task-name");
		const dateInput = document.getElementById("sidebar-edit-task-date");
		const catSelect = document.getElementById("sidebar-edit-task-category");
		const idx = getEditTaskIndex();
		if (validateTaskForm(nameInput, dateInput, catSelect) && !isNaN(idx)) {
			const value = nameInput.value.trim();
			const date = dateInput.value;
			const category = catSelect.value;
			const tasks = loadTasks();
			tasks[idx] = { ...tasks[idx], text: value, date, category };
			updateTasksAndUI(tasks);
			console.log("Task edited from sidebar:", value, date, category);
			clearTaskForm(nameInput, dateInput, catSelect);
		} else {
			alert("Please fill in all fields.");
		}
	});
}

// Delete task logic for edit form
if (deleteTaskBtn && editTaskSidebar) {
	deleteTaskBtn.addEventListener("click", function () {
		const idx = getEditTaskIndex();
		if (!isNaN(idx)) {
			const tasks = loadTasks();
			tasks.splice(idx, 1);
			updateTasksAndUI(tasks);
			console.log("Task deleted at index:", idx);
		}
	});
}

// --- Initial load of tasks and categories ---
populateCategoryDropdowns();
renderTodayTasks(loadTasks());
