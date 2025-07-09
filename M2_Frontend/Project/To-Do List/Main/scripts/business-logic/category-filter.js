// --- Category Filter Management ---
// Handles filtering tasks by category across all sections
console.log("category-filter.js loaded");

// --- State Management ---
let currentActiveFilter = null;

// --- Core Filter Functions ---

// Apply category filter to all visible sections
function applyCategoryFilter(categoryName) {
	console.log(
		`applyCategoryFilter: Applying filter for category '${categoryName}'`
	);

	// Store the current active filter
	currentActiveFilter = categoryName;

	// Update visual state of category items
	updateCategoryFilterVisuals(categoryName);

	// Filter tasks in all sections
	filterTasksInAllSections(categoryName);

	console.log(
		`applyCategoryFilter: Filter applied successfully for '${categoryName}'`
	);
}

// Clear all category filters
function clearCategoryFilter() {
	console.log("clearCategoryFilter: Clearing all category filters");

	// Clear the active filter
	currentActiveFilter = null;

	// Update visual state
	updateCategoryFilterVisuals(null);

	// Show all tasks again
	showAllTasksInAllSections();

	console.log("clearCategoryFilter: All filters cleared successfully");
}

// Toggle category filter (apply if not active, clear if active)
function toggleCategoryFilter(categoryName) {
	console.log(
		`toggleCategoryFilter: Toggling filter for category '${categoryName}'`
	);

	if (currentActiveFilter === categoryName) {
		// Category is already active, clear the filter
		clearCategoryFilter();
	} else {
		// Apply the new filter
		applyCategoryFilter(categoryName);
	}
}

// --- Visual State Management ---

// Update visual state of category items to show active filter
function updateCategoryFilterVisuals(activeCategoryName) {
	console.log(
		`updateCategoryFilterVisuals: Updating visuals for active category '${activeCategoryName}'`
	);

	const categoryItems = document.querySelectorAll(".cat-item:not(.add-list)");

	categoryItems.forEach((item) => {
		// Get only the category text, not the delete button
		const catText = item.querySelector(".cat-text");
		const categoryName = catText
			? catText.textContent.trim()
			: item.textContent.trim();

		if (activeCategoryName === categoryName) {
			// Mark as active filter
			item.classList.add("filter-active");
		} else {
			// Remove active filter class
			item.classList.remove("filter-active");
		}
	});
}

// --- Task Filtering Logic ---

// Filter tasks in all sections based on category
function filterTasksInAllSections(categoryName) {
	console.log(
		`filterTasksInAllSections: Filtering all sections for category '${categoryName}'`
	);

	// Get all task items in all sections
	const allTaskItems = document.querySelectorAll(".task-item");

	allTaskItems.forEach((taskItem) => {
		const taskCategory = getTaskCategoryFromElement(taskItem);

		if (
			taskCategory === categoryName ||
			(!taskCategory && categoryName === "")
		) {
			// Show task (matches filter or both are empty)
			taskItem.style.display = "";
			taskItem.classList.remove("filtered-out");
		} else {
			// Hide task (doesn't match filter)
			taskItem.style.display = "none";
			taskItem.classList.add("filtered-out");
		}
	});
}

// Show all tasks in all sections (clear filters)
function showAllTasksInAllSections() {
	console.log("showAllTasksInAllSections: Showing all tasks");

	const allTaskItems = document.querySelectorAll(".task-item");

	allTaskItems.forEach((taskItem) => {
		taskItem.style.display = "";
		taskItem.classList.remove("filtered-out");
	});
}

// --- Helper Functions ---

// Extract category from a task element
function getTaskCategoryFromElement(taskElement) {
	const categorySpan = taskElement.querySelector(".task-category");
	return categorySpan ? categorySpan.textContent.trim() : "";
}

// Get current active filter
function getCurrentActiveFilter() {
	return currentActiveFilter;
}

// Check if a category filter is currently active
function isCategoryFilterActive() {
	return currentActiveFilter !== null;
}

// --- Event Handling ---

// Note: Event listeners are handled by categories.js to avoid conflicts
// This file only provides the filter functionality that categories.js calls

// Initialize category filter event listeners (handled by categories.js)
function initializeCategoryFilterEvents() {
	console.log(
		"initializeCategoryFilterEvents: Event handling is managed by categories.js"
	);
	// No direct event listeners needed here
}

// Refresh event listeners after categories change (handled by categories.js)
function refreshCategoryFilterEvents() {
	console.log(
		"refreshCategoryFilterEvents: Event handling is managed by categories.js"
	);
	// No direct event listeners needed here
}

// --- API for Task Updates ---

// Update task visibility when tasks are added/modified
function updateTaskFilterVisibility(taskElement) {
	if (!isCategoryFilterActive()) {
		// No filter active, show the task
		taskElement.style.display = "";
		taskElement.classList.remove("filtered-out");
		return;
	}

	const taskCategory = getTaskCategoryFromElement(taskElement);

	if (
		taskCategory === currentActiveFilter ||
		(!taskCategory && currentActiveFilter === "")
	) {
		// Task matches current filter
		taskElement.style.display = "";
		taskElement.classList.remove("filtered-out");
	} else {
		// Task doesn't match current filter
		taskElement.style.display = "none";
		taskElement.classList.add("filtered-out");
	}
}

// --- Filter State Management ---

// Reapply current active filter (useful after DOM changes)
function reapplyCurrentFilter() {
	console.log("reapplyCurrentFilter: Reapplying current filter state");

	if (currentActiveFilter !== null) {
		console.log(
			`reapplyCurrentFilter: Reapplying filter for category '${currentActiveFilter}'`
		);
		// Reapply the visual state and task filtering
		updateCategoryFilterVisuals(currentActiveFilter);
		filterTasksInAllSections(currentActiveFilter);
	} else {
		console.log("reapplyCurrentFilter: No active filter to reapply");
		updateCategoryFilterVisuals(null);
		showAllTasksInAllSections();
	}
}

// --- Public API ---

// Expose globally
window.CategoryFilter = {
	apply: applyCategoryFilter,
	clear: clearCategoryFilter,
	toggle: toggleCategoryFilter,
	getCurrentFilter: getCurrentActiveFilter,
	isActive: isCategoryFilterActive,
	updateTaskVisibility: updateTaskFilterVisibility,
	reapplyFilter: reapplyCurrentFilter,
	initializeEvents: initializeCategoryFilterEvents,
	refreshEvents: refreshCategoryFilterEvents,
};
