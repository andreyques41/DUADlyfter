// --- Category Operations ---
// Handles CRUD operations for categories (create, read, update, delete)
console.log("category-operations.js loaded");

/**
 * Gets the current list of categories from the sidebar
 * @returns {Array} Array of current category names
 */
function getCurrentCategories() {
	console.log("getCurrentCategories: Retrieving current category list");
	const { categories } = extractCategoriesFromSidebar();
	console.log("getCurrentCategories: Found", categories.length, "categories");
	return categories;
}

/**
 * Checks if more categories can be added (max 10 categories allowed)
 * @returns {boolean} True if more categories can be added
 */
function canAddMoreCategories() {
	const currentCategories = getCurrentCategories();
	const maxCategories = 10;
	const canAdd = currentCategories.length < maxCategories;

	console.log(
		`canAddMoreCategories: ${currentCategories.length}/${maxCategories} categories. Can add more: ${canAdd}`
	);

	return canAdd;
}

/**
 * Adds a new category to the system
 * @param {string} categoryName - Name of the category to add
 * @returns {Promise<boolean>} True if category was added successfully
 */
async function addNewCategory(categoryName) {
	console.log(`addNewCategory: Adding new category '${categoryName}'`);

	// Validate category name
	if (!categoryName || categoryName.trim() === "") {
		console.warn("addNewCategory: Empty category name provided");
		alert("Please enter a category name.");
		return false;
	}

	const trimmedCategoryName = categoryName.trim();

	// Check if category already exists
	const currentCategories = getCurrentCategories();
	if (currentCategories.includes(trimmedCategoryName)) {
		console.warn(
			`addNewCategory: Category '${trimmedCategoryName}' already exists`
		);
		alert(`Category "${trimmedCategoryName}" already exists.`);
		return false;
	}

	// Check category limit
	if (!canAddMoreCategories()) {
		console.warn("addNewCategory: Maximum categories reached");
		alert("Maximum of 10 categories allowed.");
		return false;
	}

	try {
		// Create category display element
		const categoryDisplay = createCategoryDisplay(trimmedCategoryName);

		// Find add category button and insert before it
		const addCategoryItem = document.querySelector(".cat-list .add-list");
		if (!addCategoryItem) {
			console.error("addNewCategory: Add category button not found");
			return false;
		}

		// Insert the new category before the add button
		addCategoryItem.parentNode.insertBefore(categoryDisplay, addCategoryItem);

		// Set up event listeners for the new category
		setupCategoryEventListeners(categoryDisplay);

		// Add to all dropdown selects
		addCategoryToDropdowns(trimmedCategoryName);

		// Update add button state
		updateAddCategoryButtonState();

		console.log(
			`addNewCategory: Category '${trimmedCategoryName}' added successfully`
		);
		return true;
	} catch (error) {
		console.error(
			`addNewCategory: Error adding category '${trimmedCategoryName}':`,
			error
		);
		alert(`Error adding category: ${error.message}`);
		return false;
	}
}

/**
 * Deletes a category from the system
 * @param {string} categoryName - Name of the category to delete
 * @returns {Promise<boolean>} True if category was deleted successfully
 */
async function deleteCategory(categoryName) {
	console.log(`deleteCategory: Deleting category '${categoryName}'`);

	// Confirm deletion
	const confirmMessage = `Are you sure you want to delete the category "${categoryName}"?\n\nThis action will:\n- Remove the category from all tasks\n- Update all affected tasks to have no category\n- Re-render the task lists\n\nThis action cannot be undone.`;

	if (!confirm(confirmMessage)) {
		console.log(
			`deleteCategory: User cancelled deletion of category '${categoryName}'`
		);
		return false;
	}

	try {
		// Update tasks to remove this category
		await updateTasksAfterCategoryDeletion(categoryName);

		// Remove from dropdowns
		removeCategoryFromDropdowns(categoryName);

		// Remove from sidebar (find by category text)
		const categoryItems = document.querySelectorAll(
			".cat-list .cat-item:not(.add-list)"
		);

		for (const item of categoryItems) {
			const categoryText = item.querySelector(".cat-text");
			const itemCategoryName = categoryText
				? categoryText.textContent.trim()
				: item.textContent.trim();

			if (itemCategoryName === categoryName) {
				item.remove();
				console.log(
					`deleteCategory: Removed category '${categoryName}' from sidebar`
				);
				break;
			}
		}

		// Update add button state
		updateAddCategoryButtonState();

		// Re-render all task sections to reflect category changes
		if (window.renderAllTasksWithFilter) {
			await renderAllTasksWithFilter();
		}

		console.log(
			`deleteCategory: Category '${categoryName}' deleted successfully`
		);
		return true;
	} catch (error) {
		console.error(
			`deleteCategory: Error deleting category '${categoryName}':`,
			error
		);
		alert(`Error deleting category: ${error.message}`);
		return false;
	}
}

/**
 * Updates all tasks after a category is deleted (removes category from tasks)
 * @param {string} deletedCategoryName - Name of the deleted category
 * @returns {Promise<void>}
 */
async function updateTasksAfterCategoryDeletion(deletedCategoryName) {
	console.log(
		`updateTasksAfterCategoryDeletion: Updating tasks for deleted category '${deletedCategoryName}'`
	);

	try {
		// Get all tasks
		const allTasksData = await getAllTasks();
		let tasksUpdated = false;

		// Update tasks in all sections
		Object.keys(allTasksData).forEach((sectionName) => {
			const sectionTasks = allTasksData[sectionName] || [];

			sectionTasks.forEach((task) => {
				if (task.category === deletedCategoryName) {
					task.category = ""; // Remove category
					task.updatedAt = AppUtils.getCurrentTimestamp();
					tasksUpdated = true;
					console.log(
						`updateTasksAfterCategoryDeletion: Removed category from task '${task.text}'`
					);
				}
			});
		});

		// Save updated tasks if any changes were made
		if (tasksUpdated) {
			await saveAllTasks(allTasksData);
			console.log(`updateTasksAfterCategoryDeletion: Tasks updated and saved`);
		} else {
			console.log(
				`updateTasksAfterCategoryDeletion: No tasks had category '${deletedCategoryName}'`
			);
		}
	} catch (error) {
		console.error(
			`updateTasksAfterCategoryDeletion: Error updating tasks:`,
			error
		);
		throw error;
	}
}

// Expose functions globally
window.getCurrentCategories = getCurrentCategories;
window.canAddMoreCategories = canAddMoreCategories;
window.addNewCategory = addNewCategory;
window.deleteCategory = deleteCategory;
window.updateTasksAfterCategoryDeletion = updateTasksAfterCategoryDeletion;
