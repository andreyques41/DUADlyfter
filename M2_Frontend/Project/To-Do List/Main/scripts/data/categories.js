// --- Category Dropdown Management ---
// Populates all category dropdowns in the UI
console.log("categories.js loaded");

// --- Helper Functions ---

// Helper: Extract categories from sidebar
function extractCategoriesFromSidebar() {
	console.log("extractCategoriesFromSidebar: Getting categories from sidebar");

	const catList = document.querySelectorAll(
		".cat-list .cat-item:not(.add-list)"
	);
	const categories = Array.from(catList).map((item) => {
		// Get only the category text, not the delete button
		const catText = item.querySelector(".cat-text");
		return catText ? catText.textContent.trim() : item.textContent.trim();
	});

	console.log("extractCategoriesFromSidebar: Found categories:", categories);

	if (categories.length === 0) {
		console.warn(
			"extractCategoriesFromSidebar: No categories found in sidebar"
		);
	}

	return { categories, catList };
}

// Helper: Get all category dropdown selects
function getCategoryDropdownSelects() {
	console.log("getCategoryDropdownSelects: Finding dropdown select elements");

	const selects = [
		document.getElementById("sidebar-add-task-category"),
		document.getElementById("sidebar-edit-task-category"),
	].filter(Boolean);

	console.log(
		"getCategoryDropdownSelects: Found",
		selects.length,
		"dropdown selects"
	);

	if (selects.length === 0) {
		console.warn(
			"getCategoryDropdownSelects: No category select elements found"
		);
	}

	return selects;
}

// Helper: Populate a single dropdown with categories
function populateSingleDropdown(select, categories) {
	console.log(`populateSingleDropdown: Populating select '${select.id}'`);

	// Clear existing options and add default
	select.innerHTML = '<option value="">No category</option>';

	// Add category options
	categories.forEach((categoryName) => {
		const option = document.createElement("option");
		option.value = categoryName;
		option.textContent = categoryName;
		select.appendChild(option);
	});

	console.log(
		`populateSingleDropdown: Added ${categories.length} options to select '${select.id}'`
	);
}

// --- Main Functions ---

function populateAllCategoryDropdowns() {
	console.log(
		"populateAllCategoryDropdowns: Starting category dropdown population"
	);

	// Extract categories from sidebar
	const { categories } = extractCategoriesFromSidebar();

	// Get all dropdown selects
	const selects = getCategoryDropdownSelects();

	if (selects.length === 0) {
		return;
	}

	// Populate each dropdown
	selects.forEach((select) => {
		populateSingleDropdown(select, categories);
	});

	console.log(
		"populateAllCategoryDropdowns: All category dropdowns populated successfully"
	);
}

// --- Advanced Category Utilities ---

// Utility: Add new category option to all dropdowns
function addCategoryToDropdowns(categoryName) {
	console.log(
		`addCategoryToDropdowns: Adding '${categoryName}' to all dropdowns`
	);

	const selects = getCategoryDropdownSelects();

	selects.forEach((select) => {
		const option = document.createElement("option");
		option.value = categoryName;
		option.textContent = categoryName;
		select.appendChild(option);

		console.log(
			`addCategoryToDropdowns: Added '${categoryName}' to '${select.id}'`
		);
	});
}

// Utility: Remove category option from all dropdowns
function removeCategoryFromDropdowns(categoryName) {
	console.log(
		`removeCategoryFromDropdowns: Removing '${categoryName}' from all dropdowns`
	);

	const selects = getCategoryDropdownSelects();

	selects.forEach((select) => {
		// Find the option with matching value
		const optionToRemove = select.querySelector(
			`option[value="${categoryName}"]`
		);

		if (optionToRemove) {
			optionToRemove.remove();
			console.log(
				`removeCategoryFromDropdowns: Removed '${categoryName}' from '${select.id}'`
			);
		} else {
			console.log(
				`removeCategoryFromDropdowns: '${categoryName}' not found in '${select.id}'`
			);
		}
	});
}

// --- Advanced Category Management ---

// Get current categories from storage or sidebar
function getCurrentCategories() {
	console.log("getCurrentCategories: Getting current categories");

	const { categories } = extractCategoriesFromSidebar();
	console.log("getCurrentCategories: Found categories:", categories);

	return categories;
}

// Check if we can add more categories (max 5)
function canAddMoreCategories() {
	const currentCategories = getCurrentCategories();
	const canAdd = currentCategories.length < 5;

	console.log(
		`canAddMoreCategories: ${currentCategories.length}/5 categories, can add: ${canAdd}`
	);

	return canAdd;
}

// Add a new category to the sidebar
async function addNewCategory(categoryName) {
	console.log(`addNewCategory: Adding new category '${categoryName}'`);

	// Validate category name
	if (
		!categoryName ||
		typeof categoryName !== "string" ||
		!categoryName.trim()
	) {
		console.error("addNewCategory: Invalid category name");
		return false;
	}

	const trimmedName = categoryName.trim();

	// Check if category already exists
	const currentCategories = getCurrentCategories();
	if (currentCategories.includes(trimmedName)) {
		console.warn(`addNewCategory: Category '${trimmedName}' already exists`);
		return false;
	}

	// Check if we can add more categories
	if (!canAddMoreCategories()) {
		console.warn("addNewCategory: Maximum number of categories (5) reached");
		return false;
	}

	// Add category to sidebar
	const catList = document.querySelector(".cat-list");
	const addListItem = catList.querySelector(".add-list");

	// Create new category item
	const newCategoryItem = document.createElement("li");
	newCategoryItem.className = "cat-item";
	newCategoryItem.innerHTML = `
		<span class="cat-text">${trimmedName}</span>
		<button class="delete-icon" aria-label="Delete category">&times;</button>
	`;

	// Insert before the "Add new category" item
	catList.insertBefore(newCategoryItem, addListItem);

	// Add to all dropdowns
	addCategoryToDropdowns(trimmedName);

	// Set up event listeners for the new category
	setupCategoryEventListeners(newCategoryItem);

	// Update "Add new category" button state
	updateAddCategoryButtonState();

	// Re-render all sections with current filter state to ensure new category shows properly
	if (window.renderAllTasksWithFilter) {
		await window.renderAllTasksWithFilter();
	}

	console.log(`addNewCategory: Successfully added category '${trimmedName}'`);
	return true;
}

// Delete a category from the sidebar and update all related data
async function deleteCategory(categoryName) {
	console.log(`deleteCategory: Deleting category '${categoryName}'`);

	if (!categoryName || typeof categoryName !== "string") {
		console.error("deleteCategory: Invalid category name");
		return false;
	}

	const trimmedName = categoryName.trim();

	// Find and remove the category item from sidebar
	const categoryItems = document.querySelectorAll(".cat-item:not(.add-list)");
	let categoryItem = null;

	for (const item of categoryItems) {
		const catText = item.querySelector(".cat-text");
		if (catText && catText.textContent.trim() === trimmedName) {
			categoryItem = item;
			break;
		}
	}

	if (!categoryItem) {
		console.warn(
			`deleteCategory: Category '${trimmedName}' not found in sidebar`
		);
		return false;
	}

	// Remove from sidebar
	categoryItem.remove();

	// Remove from all dropdowns
	removeCategoryFromDropdowns(trimmedName);

	// Update all tasks to remove this category
	await updateTasksAfterCategoryDeletion(trimmedName);

	// Clear category filter if it was active for this category
	if (
		window.CategoryFilter &&
		window.CategoryFilter.getCurrentFilter() === trimmedName
	) {
		window.CategoryFilter.clear();
	}

	// Update "Add new category" button state
	updateAddCategoryButtonState();

	// Refresh category filter events
	if (window.CategoryFilter && window.CategoryFilter.refreshEvents) {
		window.CategoryFilter.refreshEvents();
	}

	// Re-initialize category event listeners to ensure new categories have proper handlers
	const allCategoryItems = document.querySelectorAll(
		".cat-item:not(.add-list)"
	);
	allCategoryItems.forEach(setupCategoryEventListeners);

	// Re-render all sections with current filter state
	if (window.renderAllTasksWithFilter) {
		await window.renderAllTasksWithFilter();
	}

	console.log(`deleteCategory: Successfully deleted category '${trimmedName}'`);
	return true;
}

// Update all tasks to remove deleted category
async function updateTasksAfterCategoryDeletion(deletedCategoryName) {
	console.log(
		`updateTasksAfterCategoryDeletion: Updating tasks after deleting category '${deletedCategoryName}'`
	);

	try {
		// Get all tasks from storage
		const allTasks = await window.getAllTasks();
		let tasksUpdated = false;

		// Update tasks in all sections
		for (const section of Object.keys(allTasks)) {
			const sectionTasks = allTasks[section];

			for (let i = 0; i < sectionTasks.length; i++) {
				const task = sectionTasks[i];

				if (task.category === deletedCategoryName) {
					console.log(
						`updateTasksAfterCategoryDeletion: Updating task '${task.text}' in section '${section}'`
					);

					// Set category to empty string
					task.category = "";
					task.updatedAt = window.AppUtils.getCurrentTimestamp();
					tasksUpdated = true;
				}
			}
		}

		// Save updated tasks if any changes were made
		if (tasksUpdated) {
			await window.saveAllTasks(allTasks);

			// Refresh the UI to show updated tasks with filter state preserved
			if (window.renderAllTasksWithFilter) {
				await window.renderAllTasksWithFilter();
			} else if (window.renderSectionTasks) {
				// Fallback to rendering all sections individually
				await window.renderSectionTasks("today");
				await window.renderSectionTasks("upcoming-today");
				await window.renderSectionTasks("tomorrow");
				await window.renderSectionTasks("thisweek");
				await window.renderSectionTasks("finished");

				// Reapply filter if available
				if (window.CategoryFilter && window.CategoryFilter.reapplyFilter) {
					window.CategoryFilter.reapplyFilter();
				}
			}

			console.log(
				`updateTasksAfterCategoryDeletion: Successfully updated tasks for deleted category '${deletedCategoryName}'`
			);
		} else {
			console.log(
				`updateTasksAfterCategoryDeletion: No tasks found with category '${deletedCategoryName}'`
			);
		}
	} catch (error) {
		console.error(
			`updateTasksAfterCategoryDeletion: Error updating tasks:`,
			error
		);
	}
}

// Update the state of the "Add new category" button
function updateAddCategoryButtonState() {
	const addListItem = document.querySelector(".cat-item.add-list");

	if (!addListItem) {
		console.warn("updateAddCategoryButtonState: Add category button not found");
		return;
	}

	const canAdd = canAddMoreCategories();

	if (canAdd) {
		addListItem.style.display = "";
		addListItem.style.opacity = "1";
		addListItem.style.pointerEvents = "auto";
	} else {
		addListItem.style.opacity = "0.5";
		addListItem.style.pointerEvents = "none";
	}
}

// --- Event Handling ---

// Set up event listeners for a category item
function setupCategoryEventListeners(categoryItem) {
	console.log(
		"setupCategoryEventListeners: Setting up event listeners for category item"
	);

	// Check if listeners are already set up
	if (categoryItem.hasAttribute("data-listeners-set")) {
		console.log(
			"setupCategoryEventListeners: Listeners already set up for this item"
		);
		return;
	}

	// Delete button event listener
	const deleteButton = categoryItem.querySelector(".delete-icon");
	if (deleteButton) {
		deleteButton.addEventListener("click", function (e) {
			e.stopPropagation(); // Prevent category filter toggle

			const catText = categoryItem.querySelector(".cat-text");
			if (catText) {
				const categoryName = catText.textContent.trim();

				// Show confirmation dialog
				if (
					confirm(
						`Are you sure you want to delete the "${categoryName}" category?\n\nThis will remove the category from all tasks.`
					)
				) {
					deleteCategory(categoryName);
				}
			}
		});
	}

	// Category filter toggle (click on the category text/item)
	const catText = categoryItem.querySelector(".cat-text");
	if (catText) {
		// Add click event to the entire category item, not just the text
		categoryItem.addEventListener("click", function (e) {
			// Don't trigger if clicking on delete button
			if (e.target.classList.contains('delete-icon')) {
				return;
			}
			
			const categoryName = catText.textContent.trim();
			if (window.CategoryFilter && window.CategoryFilter.toggle) {
				window.CategoryFilter.toggle(categoryName);
			}
		});
		
		// Also make the entire item appear clickable
		categoryItem.style.cursor = 'pointer';
	}

	// Mark as having listeners set up
	categoryItem.setAttribute("data-listeners-set", "true");
}

// Set up event listeners for the "Add new category" button
function setupAddCategoryEventListener() {
	console.log(
		"setupAddCategoryEventListener: Setting up add category event listener"
	);

	const addListItem = document.querySelector(".cat-item.add-list");

	if (addListItem) {
		// Check if listener is already set up
		if (addListItem.hasAttribute("data-listener-set")) {
			console.log("setupAddCategoryEventListener: Listener already set up");
			return;
		}

		addListItem.addEventListener("click", async function () {
			if (!canAddMoreCategories()) {
				alert("Maximum number of categories (5) reached.");
				return;
			}

			const categoryName = prompt("Enter the name for the new category:");

			if (categoryName && categoryName.trim()) {
				const success = await addNewCategory(categoryName.trim());

				if (!success) {
					alert(
						"Could not add category. It may already exist or the name is invalid."
					);
				}
			}
		});

		// Mark as having listener set up
		addListItem.setAttribute("data-listener-set", "true");
	} else {
		console.warn(
			"setupAddCategoryEventListener: Add category button not found"
		);
	}
}

// Initialize all category event listeners
function initializeCategoryEventListeners() {
	console.log(
		"initializeCategoryEventListeners: Initializing all category event listeners"
	);

	// Set up event listeners for existing categories
	const categoryItems = document.querySelectorAll(".cat-item:not(.add-list)");
	categoryItems.forEach(setupCategoryEventListeners);

	// Set up event listener for "Add new category" button
	setupAddCategoryEventListener();

	// Update add category button state
	updateAddCategoryButtonState();

	console.log(
		`initializeCategoryEventListeners: Set up event listeners for ${categoryItems.length} categories`
	);
}

// --- Initialization ---

// Note: Initialization is handled by app.js to avoid duplicate event listeners
// This ensures category management is properly integrated with the app lifecycle

// --- Public API Extensions ---

// Expose new functions globally
window.addNewCategory = addNewCategory;
window.deleteCategory = deleteCategory;
window.getCurrentCategories = getCurrentCategories;
window.canAddMoreCategories = canAddMoreCategories;
window.initializeCategoryEventListeners = initializeCategoryEventListeners;

// Expose globally
window.populateAllCategoryDropdowns = populateAllCategoryDropdowns;

// Expose utility functions for dynamic category management
window.addCategoryToDropdowns = addCategoryToDropdowns;
window.removeCategoryFromDropdowns = removeCategoryFromDropdowns;
