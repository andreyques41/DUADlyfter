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
	const categories = Array.from(catList).map((c) => c.textContent.trim());

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
	select.innerHTML = '<option value="">Select category</option>';

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

// Expose globally
window.populateAllCategoryDropdowns = populateAllCategoryDropdowns;

// Expose utility functions for dynamic category management
window.addCategoryToDropdowns = addCategoryToDropdowns;
window.removeCategoryFromDropdowns = removeCategoryFromDropdowns;
