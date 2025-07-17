// --- Task Element Factory ---
// Creates and manages task UI elements and their components
console.log("task-elements.js loaded");

/**
 * Creates a checkbox element for a task
 * @param {Object} taskObject - The task object
 * @param {number} taskIndex - Index of the task in the current section
 * @param {string} sectionName - Name of the current section
 * @returns {HTMLInputElement} The checkbox element
 */
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

/**
 * Creates a task header with checkbox and title
 * @param {Object} taskObject - The task object
 * @param {number} taskIndex - Index of the task in the current section
 * @param {string} sectionName - Name of the current section
 * @returns {HTMLElement} The task header element
 */
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

/**
 * Creates task metadata elements (date, category)
 * @param {Object} taskObject - The task object
 * @returns {HTMLElement} The task metadata element
 */
function createTaskMetadata(taskObject) {
	console.log(
		`createTaskMetadata: Creating metadata for task '${taskObject.text}'`
	);

	const taskMetadataContainer = document.createElement("div");
	taskMetadataContainer.className = "task-meta";

	// Add date if available
	if (taskObject.date) {
		const taskDateElement = document.createElement("span");
		taskDateElement.className = "task-date";
		taskDateElement.textContent = taskObject.date;
		taskMetadataContainer.appendChild(taskDateElement);
	}

	// Add category if available
	if (taskObject.category) {
		const taskCategoryElement = document.createElement("span");
		taskCategoryElement.className = "task-category";

		// Get the color class name for the category
		const colorClassName = getCategoryColorClassName(taskObject.category);

		// Create the structure: color box + category text
		const categoryColorBox = document.createElement("span");
		categoryColorBox.className = `category-color-box category-color-${colorClassName}`;
		const categoryTextNode = document.createTextNode(taskObject.category);
		taskCategoryElement.appendChild(categoryColorBox);
		taskCategoryElement.appendChild(categoryTextNode);

		taskMetadataContainer.appendChild(taskCategoryElement);
	}

	return taskMetadataContainer;
}

/**
 * Adds edit functionality to a task element
 * @param {HTMLElement} taskListElement - The task list element
 * @param {Object} taskObject - The task object
 * @param {number} taskIndex - Index of the task in the current section
 * @param {string} sectionName - Name of the current section
 */
function addTaskEditHandler(
	taskListElement,
	taskObject,
	taskIndex,
	sectionName
) {
	console.log(
		`addTaskEditHandler: Adding edit handler for task '${taskObject.text}'`
	);

	taskListElement.addEventListener("click", async (event) => {
		// Don't trigger edit if clicking on checkbox or delete button
		if (
			event.target.type === "checkbox" ||
			event.target.classList.contains("finished-task-delete-btn") ||
			event.target.classList.contains("delete-icon")
		) {
			return;
		}

		console.log(
			`addTaskEditHandler: Edit clicked for task '${taskObject.text}' at index ${taskIndex}`
		);

		// Open edit sidebar if function is available
		if (window.openTaskEditSidebar) {
			await openTaskEditSidebar(taskIndex, sectionName);
		} else {
			console.warn(
				"addTaskEditHandler: openTaskEditSidebar function not available"
			);
		}
	});

	// Add visual feedback for clickable elements
	taskListElement.style.cursor = "pointer";

	console.log(
		`addTaskEditHandler: Edit handler added for task '${taskObject.text}'`
	);
}

/**
 * Creates a complete task element
 * @param {Object} taskObject - The task object
 * @param {number} taskIndex - Index of the task in the current section
 * @param {string} sectionName - Name of the current section
 * @returns {HTMLElement} The complete task element
 */
function createTaskElement(taskObject, taskIndex, sectionName) {
	console.log(
		`createTaskElement: Creating task element for '${taskObject.text}'`
	);

	const taskListElement = document.createElement("li");
	taskListElement.className = "task-item";

	// Create task header (checkbox + title)
	const taskHeader = createTaskHeader(taskObject, taskIndex, sectionName);
	taskListElement.appendChild(taskHeader);

	// Create task metadata (date + category)
	const taskMetadata = createTaskMetadata(taskObject);
	taskListElement.appendChild(taskMetadata);

	// Add edit functionality for non-finished tasks
	if (sectionName !== "finished") {
		addTaskEditHandler(taskListElement, taskObject, taskIndex, sectionName);
	}

	// Add delete button for finished tasks
	if (sectionName === "finished") {
		addFinishedTaskDeleteButton(taskListElement, taskIndex, taskObject);
	}

	console.log(
		`createTaskElement: Task element created for '${taskObject.text}'`
	);

	return taskListElement;
}

/**
 * Adds a delete button to finished task elements
 * @param {HTMLElement} taskListElement - The task list element
 * @param {number} taskIndex - Index of the task in the finished section
 * @param {Object} taskObject - The task object
 */
function addFinishedTaskDeleteButton(taskListElement, taskIndex, taskObject) {
	console.log(
		`addFinishedTaskDeleteButton: Adding delete button for finished task '${taskObject.text}'`
	);

	const deleteButton = document.createElement("button");
	deleteButton.className = "finished-task-delete-btn";
	deleteButton.innerHTML = "&times;";
	deleteButton.title = "Delete task";
	deleteButton.setAttribute("aria-label", "Delete task");

	// Add click handler
	deleteButton.addEventListener("click", async (event) => {
		event.stopPropagation();

		// Confirm deletion
		const confirmDelete = confirm(
			`Are you sure you want to delete "${taskObject.text}"?`
		);
		if (!confirmDelete) return;

		console.log(
			`addFinishedTaskDeleteButton: Deleting finished task '${taskObject.text}' at index ${taskIndex}`
		);

		try {
			// Delete from storage
			await deleteTaskFromSection("finished", taskIndex);

			// Re-render finished section
			await renderSectionTasks("finished");

			console.log(
				`addFinishedTaskDeleteButton: Successfully deleted finished task '${taskObject.text}'`
			);
		} catch (error) {
			console.error(
				`addFinishedTaskDeleteButton: Error deleting finished task:`,
				error
			);
		}
	});

	// Append button to task element
	taskListElement.appendChild(deleteButton);

	console.log(
		`addFinishedTaskDeleteButton: Delete button added for finished task '${taskObject.text}'`
	);
}

// Expose functions globally
window.createTaskCheckbox = createTaskCheckbox;
window.createTaskHeader = createTaskHeader;
window.createTaskMetadata = createTaskMetadata;
window.addTaskEditHandler = addTaskEditHandler;
window.createTaskElement = createTaskElement;
window.addFinishedTaskDeleteButton = addFinishedTaskDeleteButton;
