// --- Task Completion Logic ---
// Handles task completion state changes and section movement
console.log("task-completion.js loaded");

/**
 * Handles task completion toggle with section movement
 * @param {Object} taskObject - The task object being toggled
 * @param {number} taskIndex - Index of the task in the current section
 * @param {string} sectionName - Name of the current section
 * @param {boolean} isCompleted - New completion state
 * @returns {Promise<void>}
 */
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
		taskObject.updatedAt = AppUtils.getCurrentTimestamp();

		// Get all tasks data
		const allTasksData = await getAllTasks();
		const dataSectionName = getDataSectionName(sectionName);

		if (sectionName === "finished") {
			// Task is in finished section and being unchecked - move back to original section
			await moveTaskFromFinishedToOriginalSection(taskObject, allTasksData);
		} else {
			// Task is in regular section and being completed - move to finished
			await moveTaskFromSectionToFinished(
				taskObject,
				dataSectionName,
				allTasksData
			);
		}
	} catch (error) {
		console.error(
			`handleTaskCompletionToggle: Error during task completion toggle:`,
			error
		);
		// On any error, try to re-render all visible sections
		await handleCompletionToggleError(sectionName);
	}
}

/**
 * Moves a task from finished section back to its original section
 * @param {Object} taskObject - The task object to move
 * @param {Object} allTasksData - All tasks data
 * @returns {Promise<void>}
 */
async function moveTaskFromFinishedToOriginalSection(taskObject, allTasksData) {
	// Find the task by matching the task object properties instead of relying on index
	const taskInFinished = allTasksData.finished.find((task) => {
		return (
			task.text === taskObject.text &&
			task.date === taskObject.date &&
			task.category === taskObject.category
		);
	});

	if (!taskInFinished) {
		console.error(
			`moveTaskFromFinishedToOriginalSection: Task '${taskObject.text}' not found in finished section`
		);
		// Fallback to full re-render
		await renderSectionTasks("finished");
		return;
	}

	// Determine original section based on task date
	let originalSection = getSectionForDate(taskInFinished.date);
	if (!originalSection) {
		console.warn(
			`moveTaskFromFinishedToOriginalSection: Could not determine original section for task with date '${taskInFinished.date}', defaulting to 'today'`
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
		`moveTaskFromFinishedToOriginalSection: Moved task '${taskInFinished.text}' from finished back to '${originalSection}'`
	);

	// Save data first, then re-render sections
	await saveAllTasks(allTasksData);

	// Re-render affected sections
	await reRenderSectionsAfterTaskMove(originalSection, "finished");
}

/**
 * Moves a task from a regular section to finished section
 * @param {Object} taskObject - The task object to move
 * @param {string} dataSectionName - Name of the data section
 * @param {Object} allTasksData - All tasks data
 * @returns {Promise<void>}
 */
async function moveTaskFromSectionToFinished(
	taskObject,
	dataSectionName,
	allTasksData
) {
	// Find the task by matching properties instead of relying on index
	const sectionTasks = allTasksData[dataSectionName] || [];
	const taskInSection = sectionTasks.find((task) => {
		return (
			task.text === taskObject.text &&
			task.date === taskObject.date &&
			task.category === taskObject.category
		);
	});

	if (!taskInSection) {
		console.error(
			`moveTaskFromSectionToFinished: Task '${taskObject.text}' not found in section '${dataSectionName}'`
		);
		// Fallback to full re-render
		await renderSectionTasks(dataSectionName);
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
		`moveTaskFromSectionToFinished: Moved task '${taskInSection.text}' from '${dataSectionName}' to finished`
	);

	// Save data first, then re-render sections
	await saveAllTasks(allTasksData);

	// Re-render affected sections
	await reRenderSectionsAfterTaskMove(dataSectionName, "finished");
}

/**
 * Re-renders sections after a task has been moved (optimized version)
 * @param {string} sourceSection - The section the task was moved from
 * @param {string} targetSection - The section the task was moved to
 * @returns {Promise<void>}
 */
async function reRenderSectionsAfterTaskMove(sourceSection, targetSection) {
	try {
		// Load tasks once for all affected sections
		const allTasksData = await getAllTasks();

		// For today tasks, we need to refresh both today views since they show the same data
		if (sourceSection === "today") {
			// Re-render both today sections and target section using cached data
			renderSectionTasksFromCache("today", allTasksData);
			renderSectionTasksFromCache("upcoming-today", allTasksData);
			renderSectionTasksFromCache(targetSection, allTasksData);
		} else {
			// For other sections, re-render both sections using cached data
			renderSectionTasksFromCache(sourceSection, allTasksData);
			renderSectionTasksFromCache(targetSection, allTasksData);
		}
	} catch (error) {
		console.error(
			`reRenderSectionsAfterTaskMove: Error loading tasks for re-render:`,
			error
		);
		// Fallback to individual section renders
		await renderSectionTasks(sourceSection);
		await renderSectionTasks(targetSection);
	}
}

/**
 * Handles errors during completion toggle by attempting to re-render sections (optimized version)
 * @param {string} sectionName - Name of the current section
 * @returns {Promise<void>}
 */
async function handleCompletionToggleError(sectionName) {
	try {
		// Load tasks once for error recovery
		const allTasksData = await getAllTasks();

		// Re-render the current section and finished section using cached data
		renderSectionTasksFromCache(sectionName, allTasksData);
		if (sectionName !== "finished") {
			renderSectionTasksFromCache("finished", allTasksData);
		}
	} catch (renderError) {
		console.error(
			"handleCompletionToggleError: Error during fallback re-render:",
			renderError
		);
		// Last resort - try individual renders
		try {
			await renderSectionTasks(sectionName);
			if (sectionName !== "finished") {
				await renderSectionTasks("finished");
			}
		} catch (finalError) {
			console.error(
				"handleCompletionToggleError: Final fallback also failed:",
				finalError
			);
		}
	}
}

// Expose functions globally
window.handleTaskCompletionToggle = handleTaskCompletionToggle;
