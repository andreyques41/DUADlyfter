// --- Category Extraction from Task Data ---
// Extracts categories from task data and updates the sidebar and dropdowns
console.log("category-extraction.js loaded");

// Constants
const MAX_CATEGORIES = 10;
const FUNCTION_PREFIX = "syncCategoriesFromTaskData";

/**
 * Safe function execution with error handling
 * @param {Function} fn - Function to execute
 * @param {string} errorContext - Context for error logging
 * @param {*} defaultValue - Default value to return on error
 * @returns {*} Function result or default value
 */
function safeExecute(fn, errorContext, defaultValue = null) {
	try {
		return fn();
	} catch (error) {
		console.error(`${FUNCTION_PREFIX}: Error in ${errorContext}:`, error);
		return defaultValue;
	}
}

/**
 * Extracts unique categories from all task data
 * @param {Object} allTasksData - All tasks data object
 * @returns {Array} Array of unique category names (excluding empty categories)
 */
function extractCategoriesFromTasks(allTasksData) {
	if (!allTasksData || typeof allTasksData !== "object") {
		console.warn("extractCategoriesFromTasks: Invalid task data provided");
		return [];
	}

	const categories = new Set();

	Object.keys(allTasksData).forEach((sectionName) => {
		const sectionTasks = allTasksData[sectionName];

		if (!Array.isArray(sectionTasks)) {
			console.warn(
				`extractCategoriesFromTasks: Section '${sectionName}' is not an array, skipping`
			);
			return;
		}

		sectionTasks.forEach((task) => {
			if (task?.category && typeof task.category === "string") {
				const trimmedCategory = task.category.trim();
				if (trimmedCategory) categories.add(trimmedCategory);
			}
		});
	});

	const categoryArray = Array.from(categories);
	console.log(
		`extractCategoriesFromTasks: Found ${categoryArray.length} unique categories`
	);
	return categoryArray;
}

/**
 * Removes unused hardcoded categories from UI
 * @param {Array} unusedCategories - Categories to remove
 * @param {number} maxToRemove - Maximum number to remove
 * @returns {number} Number of categories actually removed
 */
function removeUnusedCategories(unusedCategories, maxToRemove) {
	let removedCount = 0;
	const categoriesToRemove = Math.min(unusedCategories.length, maxToRemove);

	for (let i = 0; i < categoriesToRemove; i++) {
		const categoryToRemove = unusedCategories[i];

		const removed = safeExecute(
			() => {
				const categoryItems = document.querySelectorAll(
					".cat-list .cat-item:not(.add-list)"
				);
				const categoryElement = Array.from(categoryItems).find((item) => {
					const categoryText = item.querySelector(".cat-text");
					return categoryText?.textContent.trim() === categoryToRemove;
				});

				if (categoryElement) {
					categoryElement.remove();
					if (window.removeCategoryFromDropdowns) {
						removeCategoryFromDropdowns(categoryToRemove);
					}
					return true;
				}
				return false;
			},
			`removing unused category '${categoryToRemove}'`,
			false
		);

		if (removed) removedCount++;
	}

	if (removedCount > 0) {
		console.log(
			`${FUNCTION_PREFIX}: Removed ${removedCount} unused hardcoded categories`
		);
	}

	return removedCount;
}

/**
 * Adds a single category to the UI
 * @param {string} categoryName - Category name to add
 * @returns {boolean} True if successfully added
 */
function addCategoryToUI(categoryName) {
	// Check category limit
	const canAdd = safeExecute(
		() => {
			return window.canAddMoreCategories ? canAddMoreCategories() : false;
		},
		"checking category limit",
		false
	);

	if (!canAdd) {
		console.warn(
			`${FUNCTION_PREFIX}: Cannot add category '${categoryName}' - limit reached`
		);
		return false;
	}

	// Create category display
	const categoryDisplay = safeExecute(() => {
		if (!window.createCategoryDisplay)
			throw new Error("createCategoryDisplay not available");
		return createCategoryDisplay(categoryName);
	}, `creating category display for '${categoryName}'`);

	if (!categoryDisplay) return false;

	// Insert into DOM
	const inserted = safeExecute(
		() => {
			const addCategoryItem = document.querySelector(".cat-list .add-list");
			if (!addCategoryItem) throw new Error("Add category button not found");

			addCategoryItem.parentNode.insertBefore(categoryDisplay, addCategoryItem);
			return true;
		},
		`inserting category '${categoryName}' into DOM`,
		false
	);

	if (!inserted) return false;

	// Set up event listeners
	safeExecute(() => {
		if (window.setupCategoryEventListeners) {
			setupCategoryEventListeners(categoryDisplay);
		}
	}, `setting up event listeners for '${categoryName}'`);

	// Add to dropdowns
	safeExecute(() => {
		if (window.addCategoryToDropdowns) {
			addCategoryToDropdowns(categoryName);
		}
	}, `adding '${categoryName}' to dropdowns`);

	return true;
}

/**
 * Synchronizes categories from task data with the sidebar and dropdowns
 * This function extracts categories from loaded tasks and ensures all task categories
 * are represented in the UI, prioritizing task categories over unused hardcoded ones
 * @param {Object} allTasksData - All tasks data object
 * @returns {Promise<boolean>} True if categories were synchronized successfully
 */
async function syncCategoriesFromTaskData(allTasksData) {
	console.log(`${FUNCTION_PREFIX}: Synchronizing categories from task data`);

	try {
		// Validate task data
		if (!allTasksData || typeof allTasksData !== "object") {
			console.warn(`${FUNCTION_PREFIX}: Invalid task data provided`);
			return false;
		}

		// Extract categories from task data
		const taskCategories = extractCategoriesFromTasks(allTasksData);

		// Get current categories from sidebar
		const currentCategories = safeExecute(
			() => {
				if (!window.getCurrentCategories)
					throw new Error("getCurrentCategories not available");
				return getCurrentCategories();
			},
			"getting current categories",
			[]
		);

		if (!currentCategories) return false;

		// Analyze category distribution
		const missingCategories = taskCategories.filter(
			(cat) => !currentCategories.includes(cat)
		);
		const categoriesUsedInTasks = currentCategories.filter((cat) =>
			taskCategories.includes(cat)
		);
		const unusedHardcodedCategories = currentCategories.filter(
			(cat) => !taskCategories.includes(cat)
		);

		console.log(
			`${FUNCTION_PREFIX}: Missing: ${missingCategories.length}, Used: ${categoriesUsedInTasks.length}, Unused: ${unusedHardcodedCategories.length}`
		);

		// Handle category limit scenario
		const availableSlots = MAX_CATEGORIES - categoriesUsedInTasks.length;

		// Remove unused categories if needed for space
		if (
			missingCategories.length > availableSlots &&
			unusedHardcodedCategories.length > 0
		) {
			const toRemove = missingCategories.length - availableSlots;
			removeUnusedCategories(unusedHardcodedCategories, toRemove);
		}

		// Add missing categories (up to available slots)
		let categoriesAdded = 0;
		const categoriesToProcess = missingCategories.slice(
			0,
			MAX_CATEGORIES - categoriesUsedInTasks.length
		);

		for (const categoryName of categoriesToProcess) {
			if (addCategoryToUI(categoryName)) {
				categoriesAdded++;
			}
		}

		// Update UI state if changes were made
		if (categoriesAdded > 0 || unusedHardcodedCategories.length > 0) {
			safeExecute(() => {
				if (window.updateAddCategoryButtonState) {
					updateAddCategoryButtonState();
				}
			}, "updating add category button state");
		}

		// Log results
		if (taskCategories.length > MAX_CATEGORIES) {
			console.warn(
				`${FUNCTION_PREFIX}: ${taskCategories.length} categories found, only ${MAX_CATEGORIES} allowed`
			);
		} else if (categoriesAdded > 0) {
			console.log(`${FUNCTION_PREFIX}: Added ${categoriesAdded} categories`);
		} else {
			console.log(`${FUNCTION_PREFIX}: All categories already synchronized`);
		}

		return true;
	} catch (error) {
		console.error(`${FUNCTION_PREFIX}: Synchronization failed:`, error);
		return false;
	}
}

/**
 * Common logic for initializing/refreshing categories from task data
 * @param {string} context - Context for logging (e.g., "initialization", "refresh")
 * @returns {Promise<void>}
 */
async function processCategoriesFromTaskData(context) {
	console.log(`${context}: Processing categories from task data`);

	try {
		const allTasksData = await getAllTasks();
		await syncCategoriesFromTaskData(allTasksData);

		// Re-populate dropdowns if initialization
		if (
			context.includes("initialization") &&
			window.populateAllCategoryDropdowns
		) {
			populateAllCategoryDropdowns();
		}

		console.log(`${context}: Categories processed successfully`);
	} catch (error) {
		console.error(`${context}: Error processing categories:`, error);
	}
}

/**
 * Initializes categories from task data during application startup
 * This function should be called after task data is loaded but before UI is finalized
 * @returns {Promise<void>}
 */
async function initializeCategoriesFromTaskData() {
	await processCategoriesFromTaskData("initializeCategoriesFromTaskData");
}

/**
 * Refreshes categories from current task data
 * This is a convenience function that can be called after task data changes
 * @returns {Promise<void>}
 */
async function refreshCategoriesFromTaskData() {
	await processCategoriesFromTaskData("refreshCategoriesFromTaskData");
}

// Expose functions globally
window.extractCategoriesFromTasks = extractCategoriesFromTasks;
window.syncCategoriesFromTaskData = syncCategoriesFromTaskData;
window.initializeCategoriesFromTaskData = initializeCategoriesFromTaskData;
window.refreshCategoriesFromTaskData = refreshCategoriesFromTaskData;
