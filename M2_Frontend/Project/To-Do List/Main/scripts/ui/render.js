// --- Task List Rendering ---
// Handles rendering of task lists and task items in the UI
console.log("render.js loaded");

function renderSectionTasks(section) {
	console.log(`renderSectionTasks: rendering section '${section}'`);
	let listSelector = "";
	switch (section) {
		case "today":
			listSelector = "#today-view .task-list";
			break;
		case "upcoming-today":
			listSelector = "#upcoming-today-list";
			break;
		case "tomorrow":
			listSelector = "#upcoming-tomorrow-list";
			break;
		case "thisweek":
			listSelector = "#upcoming-thisweek-list";
			break;
		default:
			console.warn(`renderSectionTasks: Unknown section '${section}'`);
			return;
	}
	const parentList = document.querySelector(listSelector);
	if (!parentList) {
		console.warn(
			`renderSectionTasks: parent list not found for section '${section}' with selector '${listSelector}'`
		);
		return;
	}
	parentList.innerHTML = "";
	const tasks = getSectionTasks(
		section === "upcoming-today" ? "today" : section
	);
	console.log(
		`renderSectionTasks: found ${tasks.length} tasks for section '${section}'`
	);

	if (tasks.length === 0) {
		console.log(
			`renderSectionTasks: No tasks to render for section '${section}'`
		);
	}

	tasks.forEach((task, idx) => {
		try {
			const li = createTaskElement(task, idx, section);
			parentList.appendChild(li);
		} catch (error) {
			console.error(
				`renderSectionTasks: Error creating task element for section '${section}', index ${idx}:`,
				error
			);
		}
	});
	console.log(
		`renderSectionTasks: Successfully rendered ${tasks.length} tasks for section '${section}'`
	);
}

// --- Generalized Task Element Creation ---
function createTaskElement(task, idx, section) {
	console.log(
		`createTaskElement: Creating task element for idx=${idx}, section='${section}', task='${task.text}'`
	);
	const li = document.createElement("li");
	li.className = "task-item";
	li.id = `task_${idx + 1}`;

	const headerDiv = document.createElement("div");
	headerDiv.className = "task-header";
	const checkbox = document.createElement("input");
	checkbox.type = "checkbox";
	checkbox.className = "task-checkbox";
	checkbox.checked = !!task.completed;

	// Checkbox toggles completed state
	checkbox.addEventListener("change", function () {
		console.log(
			`createTaskElement: Task checkbox changed - task='${task.text}', completed=${this.checked}`
		);
		li.classList.toggle("completed", this.checked);
		task.completed = this.checked;
		const all = getAllTasks();
		const sec = section === "upcoming-today" ? "today" : section;

		if (!all[sec] || !all[sec][idx]) {
			console.error(
				`createTaskElement: Invalid task reference - section='${sec}', idx=${idx}`
			);
			return;
		}

		all[sec][idx].completed = this.checked;
		saveAllTasks(all);
		console.log(
			`createTaskElement: Task '${task.text}' in [${sec}] marked as ${
				this.checked ? "completed" : "not completed"
			}`
		);

		// --- Keep both 'today' and 'upcoming-today' in sync ---
		if (sec === "today") {
			renderSectionTasks("today");
			renderSectionTasks("upcoming-today");
		} else {
			renderSectionTasks(section);
		}
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
	li.addEventListener("click", function (event) {
		if (event.target === checkbox) {
			console.log(`createTaskElement: Checkbox click ignored for edit sidebar`);
			return;
		}
		console.log(
			`createTaskElement: opening edit sidebar for idx=${idx}, section='${section}', task='${task.text}'`
		);
		try {
			openTaskEditSidebar(idx, section);
		} catch (error) {
			console.error(`createTaskElement: Error opening edit sidebar:`, error);
		}
	});

	console.log(
		`createTaskElement: Successfully created task element for '${task.text}'`
	);
	return li;
}

// Expose globally
window.renderSectionTasks = renderSectionTasks;
window.createTaskElement = createTaskElement;

// Check availability of exposed functions
if (window.renderSectionTasks) {
	console.log("render.js: renderSectionTasks function is available");
} else {
	console.warn("render.js: renderSectionTasks function not found");
}

if (window.createTaskElement) {
	console.log("render.js: createTaskElement function is available");
} else {
	console.warn("render.js: createTaskElement function not found");
}
