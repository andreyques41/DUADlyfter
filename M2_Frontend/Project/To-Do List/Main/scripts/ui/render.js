// --- Task List Rendering ---
// Handles rendering of task lists and task items in the UI
console.log("render.js loaded");

// --- Helper Functions ---

// Helper: Get list selector for a section
function getTaskListSelector(sectionName) {
	console.log(
		`getTaskListSelector: Getting selector for section '${sectionName}'`
	);

	const selectorMap = {
		today: "#today-view .task-list",
		"upcoming-today": "#upcoming-today-list",
		tomorrow: "#upcoming-tomorrow-list",
		thisweek: "#upcoming-thisweek-list",
		finished: "#finished-view .finished-list",
	};

	const selector = selectorMap[sectionName];
	if (!selector) {
		console.warn(`getTaskListSelector: Unknown section '${sectionName}'`);
	}

	return selector;
}

// Helper: Get the actual section name for data retrieval
function getDataSectionName(displaySectionName) {
	return displaySectionName === "upcoming-today" ? "today" : displaySectionName;
}

// Helper: Create checkbox element for task
function createTaskCheckbox(taskObject, taskIndex, sectionName) {
	console.log(
		`createTaskCheckbox: Creating checkbox for task '${taskObject.text}'`
	);

	const taskCheckbox = document.createElement("input");
	taskCheckbox.type = "checkbox";
	taskCheckbox.className = "task-checkbox";
	taskCheckbox.checked = !!taskObject.completed;

	// Checkbox toggles completed state - using task object reference instead of index
	taskCheckbox.addEventListener("change", async function () {
		console.log(
			`createTaskCheckbox: Checkbox changed - task='${taskObject.text}', completed=${this.checked}`
		);
		await handleTaskCompletionToggle(
			taskObject,
			taskIndex,
			sectionName,
			this.checked
		);
	});

	return taskCheckbox;
}

// Helper: Handle task completion toggle with section movement
async function handleTaskCompletionToggle(
	taskObject,
	taskIndex,
	sectionName,
	isCompleted
) {
	console.log(
		`handleTaskCompletionToggle: ${
			isCompleted ? "Completing" : "Uncompleting"
		} task '${taskObject.text}' from section '${sectionName}'`
	);

	try {
		// Update task object with new completion state and timestamp
		taskObject.completed = isCompleted;
		taskObject.updatedAt = AppUtils.getCurrentTimestamp(); // Update modified timestamp

		// Get all tasks data
		const allTasksData = await getAllTasks();
		const dataSectionName = getDataSectionName(sectionName);

		if (sectionName === "finished") {
			// Task is in finished section and being unchecked - move back to original section
			// Find the task by matching the task object properties instead of relying on index
			const taskInFinished = allTasksData.finished.find((task, idx) => {
				return (
					task.text === taskObject.text &&
					task.date === taskObject.date &&
					task.category === taskObject.category
				);
			});

			if (!taskInFinished) {
				console.error(
					`handleTaskCompletionToggle: Task '${taskObject.text}' not found in finished section`
				);
				// Fallback to full re-render
				await renderSectionTasks("finished");
				return;
			}

			// Determine original section based on task date
			let originalSection = getSectionForDate(taskInFinished.date);
			if (!originalSection) {
				console.warn(
					`handleTaskCompletionToggle: Could not determine original section for task with date '${taskInFinished.date}', defaulting to 'today'`
				);
				originalSection = "today";
			}

			// Mark as incomplete and move back
			taskInFinished.completed = false;
			taskInFinished.updatedAt = AppUtils.getCurrentTimestamp();

			// Remove from finished and add to original section
			const finishedIndex = allTasksData.finished.indexOf(taskInFinished);
			allTasksData.finished.splice(finishedIndex, 1);
			allTasksData[originalSection] = allTasksData[originalSection] || [];
			allTasksData[originalSection].push(taskInFinished);

			console.log(
				`handleTaskCompletionToggle: Moved task '${taskInFinished.text}' from finished back to '${originalSection}'`
			);

			// Save data first, then re-render sections
			saveAllTasks(allTasksData);

			// For today tasks, we need to refresh both today views since they show the same data
			if (originalSection === "today") {
				// Re-render both today sections and finished to ensure synchronization
				await renderSectionTasks("finished");
				await renderSectionTasks("today");
				await renderSectionTasks("upcoming-today");
			} else {
				// For other sections, re-render both sections
				await renderSectionTasks("finished");
				await renderSectionTasks(originalSection);
			}
		} else {
			// Task is in regular section and being completed - move to finished
			// Find the task by matching properties instead of relying on index
			const sectionTasks = allTasksData[dataSectionName] || [];
			const taskInSection = sectionTasks.find((task, idx) => {
				return (
					task.text === taskObject.text &&
					task.date === taskObject.date &&
					task.category === taskObject.category
				);
			});

			if (!taskInSection) {
				console.error(
					`handleTaskCompletionToggle: Task '${taskObject.text}' not found in section '${dataSectionName}'`
				);
				// Fallback to full re-render
				await renderSectionTasks(sectionName);
				return;
			}

			// Mark as completed and update timestamp
			taskInSection.completed = true;
			taskInSection.updatedAt = AppUtils.getCurrentTimestamp();

			// Remove from current section and add to finished
			const sectionIndex = sectionTasks.indexOf(taskInSection);
			allTasksData[dataSectionName].splice(sectionIndex, 1);
			allTasksData.finished = allTasksData.finished || [];
			allTasksData.finished.push(taskInSection);

			console.log(
				`handleTaskCompletionToggle: Moved task '${taskInSection.text}' from '${dataSectionName}' to finished`
			);

			// Save data first, then re-render sections
			saveAllTasks(allTasksData);

			// For today tasks, we need to refresh both today views since they show the same data
			if (dataSectionName === "today") {
				// Re-render both today sections to ensure synchronization
				await renderSectionTasks("today");
				await renderSectionTasks("upcoming-today");
				await renderSectionTasks("finished");
			} else {
				// For other sections, re-render both sections
				await renderSectionTasks(sectionName);
				await renderSectionTasks("finished");
			}
		}
	} catch (error) {
		console.error(
			`handleTaskCompletionToggle: Error during task completion toggle:`,
			error
		);
		// On any error, try to re-render all visible sections
		try {
			await renderSectionTasks(sectionName);
			if (sectionName !== "finished") {
				await renderSectionTasks("finished");
			}
		} catch (renderError) {
			console.error(
				"handleTaskCompletionToggle: Error during fallback re-render:",
				renderError
			);
		}
	}
}

// Helper: Re-render sections that need updates after task changes (legacy compatibility)
async function reRenderAffectedSections(dataSectionName, displaySectionName) {
	console.log(
		`reRenderAffectedSections: Re-rendering sections for '${dataSectionName}'`
	);

	// Keep both 'today' and 'upcoming-today' in sync
	if (dataSectionName === "today") {
		await renderSectionTasks("today");
		await renderSectionTasks("upcoming-today");
	} else {
		await renderSectionTasks(displaySectionName);
	}
}

// Helper: Create task header with checkbox and title
function createTaskHeader(taskObject, taskIndex, sectionName) {
	console.log(
		`createTaskHeader: Creating header for task '${taskObject.text}'`
	);

	const taskHeaderContainer = document.createElement("div");
	taskHeaderContainer.className = "task-header";

	const taskCheckbox = createTaskCheckbox(taskObject, taskIndex, sectionName);
	taskHeaderContainer.appendChild(taskCheckbox);

	const taskTitleElement = document.createElement("div");
	taskTitleElement.className = "task-main-text";
	taskTitleElement.textContent = taskObject.text;
	taskHeaderContainer.appendChild(taskTitleElement);

	return taskHeaderContainer;
}

// Helper: Create task metadata (date, category)
function createTaskMetadata(taskObject) {
	console.log(
		`createTaskMetadata: Creating metadata for task '${taskObject.text}'`
	);

	const taskMetadataContainer = document.createElement("div");
	taskMetadataContainer.className = "task-meta";

	// Add date if present
	if (taskObject.date) {
		const dateIconElement = document.createElement("img");
		dateIconElement.src = "../assets/logos/calendar.svg";
		dateIconElement.alt = "date";
		dateIconElement.className = "task-meta-logo";
		taskMetadataContainer.appendChild(dateIconElement);

		const taskDateElement = document.createElement("span");
		taskDateElement.className = "task-date";
		taskDateElement.textContent = taskObject.date;
		taskMetadataContainer.appendChild(taskDateElement);
	}

	// Add category if present
	if (taskObject.category) {
		const taskCategoryElement = document.createElement("span");
		taskCategoryElement.className = "task-category";
		taskCategoryElement.textContent = taskObject.category;
		taskMetadataContainer.appendChild(taskCategoryElement);
	}

	return taskMetadataContainer;
}

// Helper: Add click handler for task editing
function addTaskEditHandler(
	taskListElement,
	taskCheckbox,
	taskIndex,
	sectionName,
	taskObject
) {
	console.log(
		`addTaskEditHandler: Adding edit handler for task '${taskObject.text}'`
	);

	taskListElement.addEventListener("click", async function (clickEvent) {
		if (clickEvent.target === taskCheckbox) {
			console.log(
				`addTaskEditHandler: Checkbox click ignored for edit sidebar`
			);
			return;
		}

		console.log(
			`addTaskEditHandler: Opening edit sidebar for index=${taskIndex}, section='${sectionName}', task='${taskObject.text}'`
		);

		try {
			await openTaskEditSidebar(taskIndex, sectionName);
		} catch (error) {
			console.error(`addTaskEditHandler: Error opening edit sidebar:`, error);
		}
	});
}

// --- Main Functions ---

async function renderSectionTasks(sectionName) {
	console.log(`renderSectionTasks: Rendering section '${sectionName}'`);

	const taskListSelector = getTaskListSelector(sectionName);
	if (!taskListSelector) {
		return;
	}

	const taskListContainer = document.querySelector(taskListSelector);
	if (!taskListContainer) {
		console.warn(
			`renderSectionTasks: Task list container not found for section '${sectionName}' with selector '${taskListSelector}'`
		);
		return;
	}

	// Clear existing content
	taskListContainer.innerHTML = "";

	// Get tasks for this section
	const dataSectionName = getDataSectionName(sectionName);
	const sectionTasksArray = await getSectionTasks(dataSectionName);

	console.log(
		`renderSectionTasks: Found ${sectionTasksArray.length} tasks for section '${sectionName}'`
	);

	if (sectionTasksArray.length === 0) {
		console.log(
			`renderSectionTasks: No tasks to render for section '${sectionName}'`
		);
		return;
	}

	// Render each task
	sectionTasksArray.forEach((taskObject, taskIndex) => {
		try {
			const taskListElement = createTaskElement(
				taskObject,
				taskIndex,
				sectionName
			);
			taskListContainer.appendChild(taskListElement);
		} catch (error) {
			console.error(
				`renderSectionTasks: Error creating task element for section '${sectionName}', index ${taskIndex}:`,
				error
			);
		}
	});

	console.log(
		`renderSectionTasks: Successfully rendered ${sectionTasksArray.length} tasks for section '${sectionName}'`
	);
}

// Creates a complete task element for the UI
function createTaskElement(taskObject, taskIndex, sectionName) {
	console.log(
		`createTaskElement: Creating task element for index=${taskIndex}, section='${sectionName}', task='${taskObject.text}'`
	);

	// Create main task container
	const taskListElement = document.createElement("li");
	taskListElement.className = "task-item";
	taskListElement.id = `task_${taskIndex + 1}`;

	// Create task header (checkbox + title)
	const taskHeaderContainer = createTaskHeader(
		taskObject,
		taskIndex,
		sectionName
	);
	taskListElement.appendChild(taskHeaderContainer);

	// Create task metadata (date + category)
	const taskMetadataContainer = createTaskMetadata(taskObject);
	taskListElement.appendChild(taskMetadataContainer);

	// Apply completed state styling if needed
	if (taskObject.completed) {
		taskListElement.classList.add("completed");
	}

	// Apply category filter visibility if needed
	if (window.CategoryFilter && window.CategoryFilter.updateTaskVisibility) {
		window.CategoryFilter.updateTaskVisibility(taskListElement);
	}

	// Add click handler for editing (get checkbox reference from header)
	// Only add edit functionality if not in finished section
	const taskCheckbox = taskHeaderContainer.querySelector(".task-checkbox");
	if (sectionName !== "finished") {
		addTaskEditHandler(
			taskListElement,
			taskCheckbox,
			taskIndex,
			sectionName,
			taskObject
		);
	}

	console.log(
		`createTaskElement: Successfully created task element for '${taskObject.text}'`
	);
	return taskListElement;
}

// Helper: Re-render all sections and apply current filter state
async function renderAllTasksWithFilter() {
	console.log("renderAllTasksWithFilter: Re-rendering all sections");

	// Render all sections
	await renderSectionTasks("today");
	await renderSectionTasks("upcoming-today");
	await renderSectionTasks("tomorrow");
	await renderSectionTasks("thisweek");
	await renderSectionTasks("finished");

	// Reapply current category filter if active
	if (window.CategoryFilter && window.CategoryFilter.isActive()) {
		const currentFilter = window.CategoryFilter.getCurrentFilter();
		console.log(
			`renderAllTasksWithFilter: Reapplying filter for category '${currentFilter}'`
		);

		// First reapply the visual state to categories
		if (window.CategoryFilter.reapplyFilter) {
			window.CategoryFilter.reapplyFilter();
		}

		// Then get all task items and apply filter
		const allTaskItems = document.querySelectorAll(".task-item");
		allTaskItems.forEach((taskItem) => {
			if (window.CategoryFilter.updateTaskVisibility) {
				window.CategoryFilter.updateTaskVisibility(taskItem);
			}
		});
	}

	console.log(
		"renderAllTasksWithFilter: All sections rendered with filter applied"
	);
}

// Expose globally
window.renderSectionTasks = renderSectionTasks;
window.renderAllTasksWithFilter = renderAllTasksWithFilter;

// Expose utility functions used by other modules
window.reRenderAffectedSections = reRenderAffectedSections;
