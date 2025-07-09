// --- Task List Rendering ---
// Core rendering logic for task lists and sections
console.log("task-render.js loaded");

/**
 * Gets the appropriate CSS selector for a task list section
 * @param {string} sectionName - Name of the section
 * @returns {string} CSS selector for the section's task list
 */
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

/**
 * Gets the actual section name for data retrieval
 * @param {string} displaySectionName - Display name of the section
 * @returns {string} Data section name
 */
function getDataSectionName(displaySectionName) {
	return displaySectionName === "upcoming-today" ? "today" : displaySectionName;
}

/**
 * Re-renders sections that need updates after task changes (legacy compatibility)
 * @param {string} dataSectionName - Name of the data section
 * @param {string} displaySectionName - Name of the display section
 * @returns {Promise<void>}
 */
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

/**
 * Renders tasks for a specific section
 * @param {string} sectionName - Name of the section to render
 * @returns {Promise<void>}
 */
async function renderSectionTasks(sectionName) {
	console.log(
		`renderSectionTasks: Rendering tasks for section '${sectionName}'`
	);

	const taskListSelector = getTaskListSelector(sectionName);
	if (!taskListSelector) {
		console.error(
			`renderSectionTasks: No selector found for section '${sectionName}'`
		);
		return;
	}

	const taskListContainer = document.querySelector(taskListSelector);
	if (!taskListContainer) {
		console.error(
			`renderSectionTasks: Task list container not found for selector '${taskListSelector}'`
		);
		return;
	}

	try {
		// Clear existing content
		taskListContainer.innerHTML = "";

		// Get tasks for this section
		const allTasksData = await getAllTasks();
		const dataSectionName = getDataSectionName(sectionName);
		const sectionTasks = allTasksData[dataSectionName] || [];

		console.log(
			`renderSectionTasks: Found ${sectionTasks.length} tasks for section '${sectionName}'`
		);

		// Render each task
		sectionTasks.forEach((taskObject, taskIndex) => {
			const taskElement = createTaskElement(taskObject, taskIndex, sectionName);
			taskListContainer.appendChild(taskElement);
		});

		console.log(
			`renderSectionTasks: Successfully rendered ${sectionTasks.length} tasks for section '${sectionName}'`
		);
	} catch (error) {
		console.error(
			`renderSectionTasks: Error rendering tasks for section '${sectionName}':`,
			error
		);
		taskListContainer.innerHTML = `<li class="error-message">Error loading tasks: ${error.message}</li>`;
	}
}

/**
 * Renders all tasks with optional category filtering
 * @param {string} [selectedCategory] - Optional category to filter by
 * @returns {Promise<void>}
 */
async function renderAllTasksWithFilter(selectedCategory = null) {
	console.log(
		`renderAllTasksWithFilter: Rendering all tasks${
			selectedCategory ? ` with category filter '${selectedCategory}'` : ""
		}`
	);

	try {
		// Define sections to render
		const sectionsToRender = [
			"today",
			"upcoming-today",
			"tomorrow",
			"thisweek",
			"finished",
		];

		// Render each section
		for (const sectionName of sectionsToRender) {
			await renderSectionTasks(sectionName);
		}

		// Apply category filter if specified
		if (selectedCategory && window.applyCategoryFilter) {
			applyCategoryFilter(selectedCategory);
		}

		console.log(
			`renderAllTasksWithFilter: All sections rendered successfully${
				selectedCategory ? ` with category filter '${selectedCategory}'` : ""
			}`
		);
	} catch (error) {
		console.error(
			`renderAllTasksWithFilter: Error rendering all tasks:`,
			error
		);
	}
}

// Expose functions globally
window.getTaskListSelector = getTaskListSelector;
window.getDataSectionName = getDataSectionName;
window.renderSectionTasks = renderSectionTasks;
window.renderAllTasksWithFilter = renderAllTasksWithFilter;
window.reRenderAffectedSections = reRenderAffectedSections;
