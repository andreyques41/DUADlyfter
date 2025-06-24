// Debug information
console.log("today.js loaded");

// Populate category dropdown for both forms
function populateCategoryDropdowns() {
	const catList = document.querySelectorAll(
		".cat-list .cat-item:not(.add-list)"
	);
	const selects = [document.getElementById("sidebar-task-category")].filter(
		Boolean
	);
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

// Sidebar open/close logic
const openSidebarBtn = document.getElementById("open-add-task-sidebar");
const addTaskSidebar = document.getElementById("add-task-sidebar");
const closeSidebarBtn = document.getElementById("close-add-task-sidebar");

if (openSidebarBtn && addTaskSidebar) {
	openSidebarBtn.addEventListener("click", () => {
		// Set today's date as default and min for the date input
		const dateInput = document.getElementById("sidebar-task-date");
		if (dateInput) {
			const today = new Date();
			const yyyy = today.getFullYear();
			const mm = String(today.getMonth() + 1).padStart(2, "0");
			const dd = String(today.getDate()).padStart(2, "0");
			const todayStr = `${yyyy}-${mm}-${dd}`;
			dateInput.value = todayStr;
			dateInput.min = todayStr;
		}
		addTaskSidebar.classList.add("open");
	});
}
if (closeSidebarBtn && addTaskSidebar) {
	closeSidebarBtn.addEventListener("click", () => {
		addTaskSidebar.classList.remove("open");
	});
}

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
	const logo = document.createElement("img");
	logo.src = "logos/today.svg";
	logo.alt = "date";
	logo.className = "task-meta-logo";
	metaDiv.appendChild(logo);
	if (task.date) {
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

// Add task form logic for sidebar (all fields required)
const addTaskFormSidebar = document.getElementById("add-task-form-sidebar");
if (addTaskFormSidebar) {
	addTaskFormSidebar.addEventListener("submit", function (e) {
		e.preventDefault();
		const nameInput = document.getElementById("sidebar-task-name");
		const dateInput = document.getElementById("sidebar-task-date");
		const catSelect = document.getElementById("sidebar-task-category");
		const value = nameInput.value.trim();
		const date = dateInput.value;
		const category = catSelect.value;
		if (value && date && category) {
			const tasks = loadTasks();
			tasks.push({ text: value, completed: false, date, category });
			saveTasks(tasks);
			renderTodayTasks(tasks);
			console.log("Task added from sidebar:", value, date, category);
			nameInput.value = "";
			dateInput.value = "";
			catSelect.value = "";
			addTaskSidebar.classList.remove("open");
		} else {
			alert("Please fill in all fields.");
		}
	});
}

// Initial load of tasks and categories
populateCategoryDropdowns();
renderTodayTasks(loadTasks());
