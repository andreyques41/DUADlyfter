// --- Category Dropdown Management ---
// Manages category dropdown population and synchronization across the UI
console.log("category-dropdown.js loaded");

/**
 * Extracts categories from the sidebar category list
 * @returns {Object} Object containing categories array and category list elements
 */
function extractCategoriesFromSidebar() {
	console.log("extractCategoriesFromSidebar: Getting categories from sidebar");

	const categoryListItems = document.querySelectorAll(
		".cat-list .cat-item:not(.add-list)"
	);
	const categories = Array.from(categoryListItems).map((item) => {
		// Get only the category text, not the delete button
		const categoryText = item.querySelector(".cat-text");
		return categoryText
			? categoryText.textContent.trim()
			: item.textContent.trim();
	});

	console.log("extractCategoriesFromSidebar: Found categories:", categories);

	if (categories.length === 0) {
		console.warn(
			"extractCategoriesFromSidebar: No categories found in sidebar"
		);
	}

	return { categories, categoryListItems };
}

/**
 * Gets all category dropdown select elements in the UI
 * @returns {Array} Array of select elements
 */
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

/**
 * Populates a single dropdown select with category options
 * @param {HTMLSelectElement} selectElement - The select element to populate
 * @param {Array} categories - Array of category names
 */
function populateSingleDropdown(selectElement, categories) {
	console.log(
		`populateSingleDropdown: Populating select '${selectElement.id}'`
	);

	// Clear existing options and add default
	selectElement.innerHTML = '<option value="">No category</option>';

	// Add category options
	categories.forEach((categoryName) => {
		const option = document.createElement("option");
		option.value = categoryName;
		option.textContent = categoryName;
		selectElement.appendChild(option);
	});

	console.log(
		`populateSingleDropdown: Added ${categories.length} options to select '${selectElement.id}'`
	);
}

/**
 * Populates all category dropdowns in the UI with current categories
 */
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

/**
 * Adds a new category to all existing dropdowns
 * @param {string} categoryName - Name of the category to add
 */
function addCategoryToDropdowns(categoryName) {
	console.log(
		`addCategoryToDropdowns: Adding category '${categoryName}' to dropdowns`
	);

	const selects = getCategoryDropdownSelects();

	selects.forEach((select) => {
		const option = document.createElement("option");
		option.value = categoryName;
		option.textContent = categoryName;
		select.appendChild(option);
	});

	console.log(
		`addCategoryToDropdowns: Category '${categoryName}' added to ${selects.length} dropdowns`
	);
}

/**
 * Removes a category from all existing dropdowns
 * @param {string} categoryName - Name of the category to remove
 */
function removeCategoryFromDropdowns(categoryName) {
	console.log(
		`removeCategoryFromDropdowns: Removing category '${categoryName}' from dropdowns`
	);

	const selects = getCategoryDropdownSelects();

	selects.forEach((select) => {
		const optionToRemove = select.querySelector(
			`option[value="${categoryName}"]`
		);
		if (optionToRemove) {
			optionToRemove.remove();
		}
	});

	console.log(
		`removeCategoryFromDropdowns: Category '${categoryName}' removed from ${selects.length} dropdowns`
	);
}

// Expose functions globally
window.populateAllCategoryDropdowns = populateAllCategoryDropdowns;
window.addCategoryToDropdowns = addCategoryToDropdowns;
window.removeCategoryFromDropdowns = removeCategoryFromDropdowns;
